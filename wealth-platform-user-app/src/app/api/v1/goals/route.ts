import { NextRequest, NextResponse } from 'next/server';

const MOCK_GOALS = [
    {
        id: 'goal-001',
        name: 'Retirement at 55',
        type: 'retirement',
        target_amount: 1000000,
        current_amount: 680000,
        target_date: '2045-01-01',
        monthly_contribution: 2500,
        status: 'active',
        progress: 68,
    },
    {
        id: 'goal-002',
        name: "Children's Education",
        type: 'education',
        target_amount: 200000,
        current_amount: 95000,
        target_date: '2035-09-01',
        monthly_contribution: 1500,
        status: 'active',
        progress: 47.5,
    },
    {
        id: 'goal-003',
        name: 'Dream Home',
        type: 'home',
        target_amount: 500000,
        current_amount: 125000,
        target_date: '2030-06-01',
        monthly_contribution: 3000,
        status: 'active',
        progress: 25,
    },
];

export async function GET(request: NextRequest) {
    return NextResponse.json({
        data: MOCK_GOALS,
        total: MOCK_GOALS.length,
        summary: {
            total_target: 1700000,
            total_current: 900000,
            overall_progress: 52.9,
        },
    });
}
