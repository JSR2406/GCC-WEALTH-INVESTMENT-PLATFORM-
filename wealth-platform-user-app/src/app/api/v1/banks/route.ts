import { NextRequest, NextResponse } from 'next/server';

// Mock Banks Data
const MOCK_BANKS = [
    {
        id: 'fab-001',
        name: 'First Abu Dhabi Bank',
        slug: 'fab',
        country: 'AE',
        branding: {
            primary_color: '#00A651',
            secondary_color: '#003366',
            app_name: 'FAB Wealth',
        },
        features: {
            sharia_products: true,
            zakat_calculator: true,
            goal_based_investing: true,
        },
    },
    {
        id: 'hsbc-001',
        name: 'HSBC Middle East',
        slug: 'hsbc',
        country: 'AE',
        branding: {
            primary_color: '#DB0011',
            secondary_color: '#2E2E2E',
            app_name: 'HSBC Wealth',
        },
        features: {
            sharia_products: false,
            zakat_calculator: false,
            goal_based_investing: true,
        },
    },
    {
        id: 'rajhi-001',
        name: 'Al Rajhi Bank',
        slug: 'rajhi',
        country: 'SA',
        branding: {
            primary_color: '#004B87',
            secondary_color: '#00A0DF',
            app_name: 'Al Rajhi Wealth',
        },
        features: {
            sharia_products: true,
            zakat_calculator: true,
            goal_based_investing: true,
        },
    },
];

export async function GET(request: NextRequest) {
    return NextResponse.json({
        data: MOCK_BANKS,
        total: MOCK_BANKS.length,
    });
}
