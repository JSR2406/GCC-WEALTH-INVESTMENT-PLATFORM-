'use client';

import { use, useEffect } from 'react';
import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';

// Mock data (would be fetched by ID in real app)
const mockAccountDetails = {
    id: 'acc-1',
    name: 'Investment Account',
    balance: 325000,
    currency: 'USD',
    holdings: [
        { symbol: 'AAPL', name: 'Apple Inc.', value: 150000, allocation: 46 },
        { symbol: 'MSFT', name: 'Microsoft Corp.', value: 100000, allocation: 30 },
        { symbol: 'USHY', name: 'iShares High Yield Corp', value: 75000, allocation: 24 }
    ],
    history: [
        { date: '2026-01-30', type: 'Buy', description: 'Bought 50 AAPL', amount: -12500 },
        { date: '2026-01-15', type: 'Dividend', description: 'Dividend Payment', amount: 450 }
    ]
};

export default function AccountDetailsPage({ params }: { params: Promise<{ id: string }> }) {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    // In a real app we'd fetch data based on resolvedParams.id
    // const resolvedParams = use(params); 

    return (
        <div className="space-y-6 animate-fade-in">
            <Link
                href={`/${tenant.slug}/portfolio/accounts`}
                className="text-gray-500 hover:text-gray-900 flex items-center gap-2"
            >
                ← Back to Accounts
            </Link>

            {/* Header Card */}
            <div className="bg-white rounded-2xl shadow-sm border p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="flex items-center gap-4">
                    <div
                        className="w-16 h-16 rounded-xl flex items-center justify-center text-3xl"
                        style={{ backgroundColor: `${primaryColor}15` }}
                    >
                        📈
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">{mockAccountDetails.name}</h1>
                        <p className="text-gray-500">ID: {mockAccountDetails.id}</p>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-sm text-gray-500">Current Balance</p>
                    <p className="text-3xl font-bold text-gray-900">
                        ${mockAccountDetails.balance.toLocaleString()}
                    </p>
                </div>
            </div>

            {/* Holdings & History Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Holdings - Takes up 2 cols */}
                <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-6">Holdings</h2>
                    <div className="space-y-4">
                        {mockAccountDetails.holdings.map((holding) => (
                            <div key={holding.symbol} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center font-bold text-gray-600 text-xs">
                                        {holding.symbol}
                                    </div>
                                    <div>
                                        <p className="font-medium text-gray-900">{holding.name}</p>
                                        <p className="text-xs text-gray-500">{holding.allocation}% allocation</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="font-semibold text-gray-900">${holding.value.toLocaleString()}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-white rounded-xl shadow-sm border p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-6">Recent Activity</h2>
                    <div className="space-y-6">
                        {mockAccountDetails.history.map((item, idx) => (
                            <div key={idx} className="relative pl-6 pb-6 border-l-2 border-gray-100 last:pb-0 last:border-0">
                                <div
                                    className="absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 border-white"
                                    style={{ backgroundColor: primaryColor }}
                                />
                                <p className="text-sm text-gray-400 mb-1">{item.date}</p>
                                <p className="font-medium text-gray-900">{item.description}</p>
                                <p className={`text-sm font-semibold ${item.amount > 0 ? 'text-green-600' : 'text-gray-900'}`}>
                                    {item.amount > 0 ? '+' : ''}${Math.abs(item.amount).toLocaleString()}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
