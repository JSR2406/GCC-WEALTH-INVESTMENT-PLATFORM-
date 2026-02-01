import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    return NextResponse.json({
        reports: [
            {
                type: 'fatca',
                name: 'FATCA Report 2025',
                status: 'submitted',
                deadline: '2026-03-31',
                description: 'Foreign Account Tax Compliance Act reporting',
            },
            {
                type: 'crs',
                name: 'CRS Report 2025',
                status: 'pending',
                deadline: '2026-06-30',
                description: 'Common Reporting Standard for tax information',
            },
        ],
        zakat: {
            enabled: true,
            zakatable_wealth: 575000,
            zakat_due: 14375,
            nisab_threshold: 5500,
            gold_nisab: 87.48,
            silver_nisab: 612.36,
        },
    });
}
