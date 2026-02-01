"""
Revenue Calculator Service
==========================

Calculates monthly revenue based on bank's revenue model configuration.
"""

import logging
from calendar import monthrange
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bank import Bank
from app.models.base import InvoiceStatus, RevenueModel
from app.models.invoice import Invoice
from app.models.revenue import RevenueCalculation
from app.models.user import User
from app.models.account import UserAccount

logger = logging.getLogger(__name__)


class RevenueCalculator:
    """
    Revenue Calculator Service.
    
    Handles:
    - Monthly revenue calculation per user
    - Invoice generation
    - Pro-rating for mid-month signups
    """
    
    async def calculate_monthly_revenue(
        self,
        db: AsyncSession,
        bank_id: Optional[UUID],
        month: int,
        year: int
    ) -> dict:
        """Calculate monthly revenue for one or all banks."""
        
        if bank_id:
            banks = [await self._get_bank(db, bank_id)]
        else:
            banks = await self._get_active_banks(db)
        
        total_calculations = 0
        total_revenue = Decimal(0)
        invoices_created = []
        
        for bank in banks:
            result = await self._calculate_bank_revenue(db, bank, month, year)
            total_calculations += result["calculations"]
            total_revenue += result["total_revenue"]
            if result.get("invoice_id"):
                invoices_created.append(result["invoice_id"])
        
        return {
            "calculations_created": total_calculations,
            "total_revenue": total_revenue,
            "invoices_created": invoices_created
        }
    
    async def _get_bank(self, db: AsyncSession, bank_id: UUID) -> Bank:
        result = await db.execute(select(Bank).where(Bank.id == bank_id))
        return result.scalar_one()
    
    async def _get_active_banks(self, db: AsyncSession) -> list[Bank]:
        result = await db.execute(
            select(Bank).where(Bank.status == "active")
        )
        return result.scalars().all()
    
    async def _calculate_bank_revenue(
        self,
        db: AsyncSession,
        bank: Bank,
        month: int,
        year: int
    ) -> dict:
        """Calculate revenue for a single bank."""
        
        # Get active users for this bank
        users_result = await db.execute(
            select(User)
            .where(User.bank_id == bank.id)
            .where(User.is_active == True)
        )
        users = users_result.scalars().all()
        
        calculations = []
        total_revenue = Decimal(0)
        total_aum = Decimal(0)
        
        for user in users:
            calc = await self._calculate_user_revenue(
                db, bank, user, month, year
            )
            if calc:
                calculations.append(calc)
                total_revenue += calc.total_revenue
                total_aum += calc.user_aum_snapshot
        
        # Create invoice
        invoice = await self._create_invoice(
            db, bank, month, year,
            len(users), total_aum, total_revenue
        )
        
        # Mark calculations as invoiced
        for calc in calculations:
            calc.invoice_id = invoice.id
            calc.is_invoiced = True
            calc.invoiced_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.info(
            f"Revenue calculated for {bank.slug}: "
            f"{len(calculations)} users, ${total_revenue}"
        )
        
        return {
            "calculations": len(calculations),
            "total_revenue": total_revenue,
            "invoice_id": invoice.id
        }
    
    async def _calculate_user_revenue(
        self,
        db: AsyncSession,
        bank: Bank,
        user: User,
        month: int,
        year: int
    ) -> Optional[RevenueCalculation]:
        """Calculate revenue for a single user based on bank's revenue model."""
        
        # Check if already calculated
        existing = await db.execute(
            select(RevenueCalculation)
            .where(RevenueCalculation.user_id == user.id)
            .where(RevenueCalculation.calculation_month == month)
            .where(RevenueCalculation.calculation_year == year)
        )
        if existing.scalar_one_or_none():
            return None  # Already calculated
        
        # Get user's total AUM
        aum_result = await db.execute(
            select(func.sum(UserAccount.balance_usd))
            .where(UserAccount.user_id == user.id)
            .where(UserAccount.is_active == True)
        )
        user_aum = Decimal(aum_result.scalar() or 0)
        
        # Calculate pro-rating
        days_in_month = monthrange(year, month)[1]
        days_active = days_in_month
        is_prorated = False
        
        if user.onboarded_at:
            onboard_date = user.onboarded_at
            if onboard_date.year == year and onboard_date.month == month:
                days_active = days_in_month - onboard_date.day + 1
                is_prorated = True
        
        prorate_factor = Decimal(days_active) / Decimal(days_in_month)
        
        # Calculate based on revenue model
        subscription_fee = Decimal(0)
        aum_revenue_share = Decimal(0)
        
        if bank.revenue_model == RevenueModel.SAAS:
            monthly_fee = (bank.base_fee_usd or Decimal(0)) / 12
            subscription_fee = monthly_fee * prorate_factor
            
        elif bank.revenue_model == RevenueModel.HYBRID:
            monthly_fee = (bank.base_fee_usd or Decimal(0)) / 12
            subscription_fee = monthly_fee * prorate_factor
            aum_share_pct = (bank.aum_share_percentage or Decimal(0)) / 100
            aum_revenue_share = (user_aum * aum_share_pct / 12) * prorate_factor
            
        elif bank.revenue_model == RevenueModel.AUM_SHARE:
            aum_share_pct = (bank.aum_share_percentage or Decimal(0)) / 100
            aum_revenue_share = (user_aum * aum_share_pct / 12) * prorate_factor
        
        total_revenue = subscription_fee + aum_revenue_share
        
        # Create calculation record
        calculation = RevenueCalculation(
            bank_id=bank.id,
            user_id=user.id,
            calculation_month=month,
            calculation_year=year,
            user_aum_snapshot=user_aum,
            subscription_fee=subscription_fee.quantize(Decimal("0.01")),
            aum_revenue_share=aum_revenue_share.quantize(Decimal("0.01")),
            total_revenue=total_revenue.quantize(Decimal("0.01")),
            days_active=days_active,
            is_prorated=is_prorated,
        )
        
        db.add(calculation)
        return calculation
    
    async def _create_invoice(
        self,
        db: AsyncSession,
        bank: Bank,
        month: int,
        year: int,
        total_users: int,
        total_aum: Decimal,
        total_revenue: Decimal
    ) -> Invoice:
        """Create invoice for the bank."""
        
        # Generate invoice number
        count_result = await db.execute(
            select(func.count(Invoice.id))
            .where(Invoice.billing_year == year)
            .where(Invoice.billing_month == month)
        )
        count = count_result.scalar() or 0
        invoice_number = f"INV-{year}-{month:02d}-{count + 1:03d}"
        
        # Due date = 15 days after end of billing month
        from datetime import date, timedelta
        from calendar import monthrange
        
        last_day = monthrange(year, month)[1]
        due_date = datetime(year, month, last_day) + timedelta(days=15)
        
        invoice = Invoice(
            bank_id=bank.id,
            invoice_number=invoice_number,
            billing_month=month,
            billing_year=year,
            total_users=total_users,
            total_aum=total_aum,
            subscription_total=total_revenue * Decimal("0.2"),  # Simplified
            aum_share_total=total_revenue * Decimal("0.8"),
            subtotal=total_revenue,
            tax_amount=Decimal(0),
            total_amount=total_revenue,
            status=InvoiceStatus.SENT,
            due_date=due_date,
        )
        
        db.add(invoice)
        return invoice
