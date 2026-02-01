"""
Portfolios API - Investment Goals and Accounts
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.api.deps import AuthenticatedUser, Database
from app.models.account import UserAccount
from app.models.base import AccountType, GoalStatus, GoalType
from app.models.goal import InvestmentGoal
from app.schemas.common import SuccessResponse

logger = logging.getLogger(__name__)
router = APIRouter()


class GoalCreate(BaseModel):
    goal_type: GoalType
    name: str = Field(..., min_length=2, max_length=255)
    target_amount: float = Field(..., gt=0)
    target_date: str
    monthly_contribution: float = Field(default=0, ge=0)
    risk_level: Optional[str] = None


class GoalResponse(BaseModel):
    id: UUID
    goal_type: GoalType
    name: str
    target_amount: float
    current_amount: float
    progress_percentage: float
    target_date: str
    status: GoalStatus

    class Config:
        from_attributes = True


class AccountResponse(BaseModel):
    id: UUID
    account_name: str
    account_type: AccountType
    currency: str
    current_balance: float
    balance_usd: float


@router.get("/accounts", response_model=list[AccountResponse])
async def list_accounts(user: AuthenticatedUser, db: Database):
    result = await db.execute(
        select(UserAccount)
        .where(UserAccount.user_id == user.user_id)
        .where(UserAccount.is_active == True)
    )
    accounts = result.scalars().all()
    return [AccountResponse(
        id=a.id, account_name=a.account_name, account_type=a.account_type,
        currency=a.currency, current_balance=float(a.current_balance),
        balance_usd=float(a.balance_usd)
    ) for a in accounts]


@router.get("/goals", response_model=list[GoalResponse])
async def list_goals(user: AuthenticatedUser, db: Database):
    result = await db.execute(
        select(InvestmentGoal).where(InvestmentGoal.user_id == user.user_id)
    )
    goals = result.scalars().all()
    return [GoalResponse(
        id=g.id, goal_type=g.goal_type, name=g.name,
        target_amount=float(g.target_amount), current_amount=float(g.current_amount),
        progress_percentage=g.progress_percentage, target_date=g.target_date.isoformat(),
        status=g.status
    ) for g in goals]


@router.post("/goals", response_model=GoalResponse, status_code=201)
async def create_goal(goal_data: GoalCreate, user: AuthenticatedUser, db: Database):
    from datetime import date
    goal = InvestmentGoal(
        bank_id=user.bank_id, user_id=user.user_id, goal_type=goal_data.goal_type,
        name=goal_data.name, target_amount=goal_data.target_amount,
        target_date=date.fromisoformat(goal_data.target_date),
        monthly_contribution=goal_data.monthly_contribution, risk_level=goal_data.risk_level
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return GoalResponse(
        id=goal.id, goal_type=goal.goal_type, name=goal.name,
        target_amount=float(goal.target_amount), current_amount=0,
        progress_percentage=0, target_date=goal.target_date.isoformat(),
        status=goal.status
    )


@router.delete("/goals/{goal_id}", response_model=SuccessResponse)
async def cancel_goal(goal_id: UUID, user: AuthenticatedUser, db: Database):
    result = await db.execute(
        select(InvestmentGoal).where(InvestmentGoal.id == goal_id)
        .where(InvestmentGoal.user_id == user.user_id)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.status = GoalStatus.CANCELLED
    await db.commit()
    return SuccessResponse(message="Goal cancelled")
