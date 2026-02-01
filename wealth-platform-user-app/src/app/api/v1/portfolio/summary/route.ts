import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    return NextResponse.json({
        total_aum: 575000,
        currency: 'USD',
        change_24h: 2.5,
        change_7d: 4.2,
        accounts: [
            { type: 'savings', name: 'FAB Savings', balance: 125000, currency: 'AED', percentage: 21.7 },
            { type: 'investment', name: 'FAB Investment', balance: 450000, currency: 'USD', percentage: 78.3 },
        ],
        allocation: {
            equity: 45,
            fixed_income: 30,
            real_estate: 15,
            cash: 10,
        },
    });
}
