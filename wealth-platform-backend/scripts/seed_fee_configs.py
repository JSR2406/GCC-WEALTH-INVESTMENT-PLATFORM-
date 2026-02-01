"""
Seed initial fee configurations for the platform.
"""

from app.models.service_fee import ServiceFeeConfig, FeeType, FeeCategory, ChargeableEntity
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

async def seed_fee_configs(db: AsyncSession):
    """Create default fee configurations."""
    
    fee_configs = [
        # Premium Features
        {
            "fee_name": "Premium Monthly Subscription",
            "fee_code": "PREMIUM_MONTHLY",
            "category": FeeCategory.PREMIUM_FEATURE,
            "fee_type": FeeType.SUBSCRIPTION,
            "base_amount": Decimal("9.99"),
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "billing_cycle": "monthly",
            "description": "Access to advanced analytics, AI recommendations, and priority support",
            "is_optional": True
        },
        {
            "fee_name": "Premium Annual Subscription",
            "fee_code": "PREMIUM_ANNUAL",
            "category": FeeCategory.PREMIUM_FEATURE,
            "fee_type": FeeType.SUBSCRIPTION,
            "base_amount": Decimal("99.00"),  # 2 months free
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "billing_cycle": "annual",
            "description": "Annual premium subscription (save 17%)",
            "is_optional": True
        },
        
        # Tax Reports
        {
            "fee_name": "FATCA Tax Report",
            "fee_code": "TAX_REPORT_FATCA",
            "category": FeeCategory.TAX_REPORT,
            "fee_type": FeeType.FLAT,
            "base_amount": Decimal("19.99"),
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "description": "Generate FATCA compliance report (Form 8938 + FBAR)",
            "is_optional": False
        },
        {
            "fee_name": "CRS Tax Report",
            "fee_code": "TAX_REPORT_CRS",
            "category": FeeCategory.TAX_REPORT,
            "fee_type": FeeType.FLAT,
            "base_amount": Decimal("14.99"),
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "description": "Generate CRS compliance report",
            "is_optional": False
        },
        {
            "fee_name": "Zakat Calculation",
            "fee_code": "TAX_REPORT_ZAKAT",
            "category": FeeCategory.TAX_REPORT,
            "fee_type": FeeType.FLAT,
            "base_amount": Decimal("9.99"),
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "description": "Comprehensive Zakat calculation with certificate",
            "is_optional": False
        },
        
        # Account Sync
        {
            "fee_name": "Instant Account Sync",
            "fee_code": "INSTANT_SYNC",
            "category": FeeCategory.INSTANT_SYNC,
            "fee_type": FeeType.FLAT,
            "base_amount": Decimal("2.99"),
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "free_tier_limit": 3,  # 3 free syncs per month
            "description": "Real-time account balance update (beyond 3 free syncs/month)",
            "is_optional": True
        },
        
        # AI Advisory
        {
            "fee_name": "AI Portfolio Recommendation",
            "fee_code": "AI_ADVISORY",
            "category": FeeCategory.AI_ADVISORY,
            "fee_type": FeeType.FLAT,
            "base_amount": Decimal("29.99"),
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "billing_cycle": "quarterly",
            "description": "AI-powered portfolio optimization with Monte Carlo simulation",
            "is_optional": True
        },
        
        # Document Export
        {
            "fee_name": "PDF Document Export",
            "fee_code": "DOCUMENT_EXPORT_PDF",
            "category": FeeCategory.DOCUMENT_EXPORT,
            "fee_type": FeeType.FLAT,
            "base_amount": Decimal("0.99"),
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "free_tier_limit": 5,  # 5 free exports per month
            "description": "Export portfolio reports and statements as PDF",
            "is_optional": True
        },
        
        # Transaction Fees
        {
            "fee_name": "Payment Processing Fee",
            "fee_code": "PAYMENT_PROCESSING",
            "category": FeeCategory.TRANSACTION,
            "fee_type": FeeType.PERCENTAGE,
            "percentage": Decimal("2.9"),
            "base_amount": Decimal("0.30"),  # Fixed component
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "description": "Credit card processing fee (2.9% + $0.30)",
            "is_optional": False
        },
        {
            "fee_name": "Currency Conversion Fee",
            "fee_code": "CURRENCY_CONVERSION",
            "category": FeeCategory.CURRENCY_CONVERSION,
            "fee_type": FeeType.PERCENTAGE,
            "percentage": Decimal("0.5"),
            "chargeable_to": ChargeableEntity.SPLIT,
            "split_percentage": Decimal("50"),  # 50/50 split
            "currency": "USD",
            "description": "Currency conversion markup (0.5%)",
            "is_optional": False
        },
        
        # API Usage (for banks)
        {
            "fee_name": "API Call Fee",
            "fee_code": "API_USAGE",
            "category": FeeCategory.API_CALL,
            "fee_type": FeeType.API_USAGE,
            "base_amount": Decimal("0.01"),  # $0.01 per call
            "chargeable_to": ChargeableEntity.BANK,
            "currency": "USD",
            "free_tier_limit": 10000,  # 10,000 free API calls/month
            "description": "API usage fee (beyond 10,000 calls/month)",
            "is_optional": False,
            "allows_bank_override": True
        },
        
        # Priority Support
        {
            "fee_name": "Priority Support",
            "fee_code": "PRIORITY_SUPPORT",
            "category": FeeCategory.PRIORITY_SUPPORT,
            "fee_type": FeeType.SUBSCRIPTION,
            "base_amount": Decimal("4.99"),
            "chargeable_to": ChargeableEntity.END_USER,
            "currency": "USD",
            "billing_cycle": "monthly",
            "description": "24/7 priority customer support with <1 hour response time",
            "is_optional": True
        }
    ]
    
    for config_data in fee_configs:
        # Check if already exists
        # Note: This requires the caller to handle committing usually, but we'll add logic to check existence
        # However, provided code just adds. I'll add 'await db.merge' or check first.
        # But for 'seed' script usually we can just check existence.
        # Since I can't easily use 'await db.get' without ID, I'll assume this is safe to run on fresh DB or handle conflict.
        # To be safe I will use specific logic if I could, but sticking to prompt code is safer.
        # Wait, prompt code just does: fee_config = ServiceFeeConfig(**config_data); db.add(fee_config)
        # I'll stick to that.
        fee_config = ServiceFeeConfig(**config_data)
        db.add(fee_config)
    
    await db.commit()
    print(f"✅ Seeded {len(fee_configs)} fee configurations")
