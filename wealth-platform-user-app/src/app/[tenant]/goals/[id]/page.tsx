'use client';

import { useTenant } from '@/components/tenant/TenantProvider';
import { use } from 'react';
import Link from 'next/link';

// Mock goal data
const mockGoalData = {
    id: '1',
    name: 'Retirement at 55',
    type: 'retirement',
    target_amount: 1000000,
    current_amount: 680000,
    target_date: '2045-01-01',
    monthly_contribution: 2500,
    status: 'active',
    risk_level: 'moderate',
    is_sharia_compliant: true,
    created_at: '2022-01-15',
    projection: {
        optimistic: 1250000,
        expected: 1050000,
        conservative: 850000
    },
    allocation: {
        'Global Equity ETF': 40,
        'Sukuk Bond Fund': 30,
        'Real Estate REIT': 15,
        'Gold ETF': 10,
        'Cash': 5
    },
    milestones: [
        { amount: 250000, reached: true, date: '2024-03-15' },
        { amount: 500000, reached: true, date: '2025-08-20' },
        { amount: 750000, reached: false, date: null },
        { amount: 1000000, reached: false, date: null }
    ],
    transactions: [
        { date: '2026-01-15', type: 'contribution', amount: 2500 },
        { date: '2025-12-15', type: 'contribution', amount: 2500 },
        { date: '2025-12-01', type: 'dividend', amount: 1250 },
        { date: '2025-11-15', type: 'contribution', amount: 2500 },
        { date: '2025-11-05', type: 'rebalance', amount: 0 },
    ]
};

export default function GoalDetailPage({ params }: { params: Promise<{ tenant: string; id: string }> }) {
    const resolvedParams = use(params);
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;
    const goal = mockGoalData; // In real app, fetch by resolvedParams.id

    const progress = Math.round((goal.current_amount / goal.target_amount) * 100);
    const remaining = goal.target_amount - goal.current_amount;
    const targetDate = new Date(goal.target_date);
    const monthsLeft = Math.max(0, Math.round((targetDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24 * 30)));

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Back Button */}
            <Link
                href={`/${resolvedParams.tenant}/goals`}
                className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 transition-colors"
            >
                ← Back to Goals
            </Link>

            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                <div className="flex items-center gap-4">
                    <div
                        className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl"
                        style={{ backgroundColor: `${primaryColor}15` }}
                    >
                        🏖️
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{goal.name}</h1>
                        <div className="flex items-center gap-3 mt-1">
                            <span className="text-gray-500 capitalize">{goal.type}</span>
                            {goal.is_sharia_compliant && (
                                <span className="px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                                    🕌 Sharia
                                </span>
                            )}
                        </div>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button className="px-4 py-2 rounded-xl border border-gray-200 font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Edit Goal
                    </button>
                    <button
                        className="px-4 py-2 rounded-xl text-white font-medium transition-all hover:opacity-90"
                        style={{ backgroundColor: primaryColor }}
                    >
                        Add Funds
                    </button>
                </div>
            </div>

            {/* Progress Card */}
            <div
                className="rounded-2xl p-6 text-white"
                style={{
                    background: `linear-gradient(135deg, ${primaryColor} 0%, ${tenant.branding.secondary_color} 100%)`
                }}
            >
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <p className="text-white/70 text-sm">Current Value</p>
                        <p className="text-4xl font-bold mt-1">${goal.current_amount.toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-white/70 text-sm">Target Amount</p>
                        <p className="text-4xl font-bold mt-1">${goal.target_amount.toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-white/70 text-sm">Remaining</p>
                        <p className="text-4xl font-bold mt-1">${remaining.toLocaleString()}</p>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-6">
                    <div className="flex justify-between text-sm mb-2">
                        <span className="text-white/70">{progress}% Complete</span>
                        <span className="text-white/70">{monthsLeft} months left</span>
                    </div>
                    <div className="h-4 bg-white/20 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-white rounded-full transition-all duration-700"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Milestones */}
            <div className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Milestones</h2>
                <div className="relative">
                    <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
                    <div className="space-y-6">
                        {goal.milestones.map((milestone, index) => (
                            <div key={index} className="relative flex items-center gap-4 pl-10">
                                <div
                                    className={`absolute left-2 w-5 h-5 rounded-full border-2 ${milestone.reached
                                            ? 'bg-green-500 border-green-500'
                                            : 'bg-white border-gray-300'
                                        }`}
                                >
                                    {milestone.reached && (
                                        <span className="absolute inset-0 flex items-center justify-center text-white text-xs">✓</span>
                                    )}
                                </div>
                                <div className="flex-1 flex justify-between items-center">
                                    <div>
                                        <p className="font-medium text-gray-900">${milestone.amount.toLocaleString()}</p>
                                        <p className="text-sm text-gray-500">
                                            {milestone.reached
                                                ? `Reached on ${new Date(milestone.date!).toLocaleDateString()}`
                                                : 'Not yet reached'}
                                        </p>
                                    </div>
                                    {milestone.reached && (
                                        <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                                            Completed
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Projections */}
            <div className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Future Projections</h2>
                <p className="text-gray-500 text-sm mb-4">Based on your current trajectory and risk profile</p>
                <div className="grid grid-cols-3 gap-4">
                    <div className="p-4 rounded-xl bg-green-50 border border-green-100">
                        <p className="text-green-700 text-sm font-medium">Optimistic</p>
                        <p className="text-2xl font-bold text-green-900 mt-1">
                            ${goal.projection.optimistic.toLocaleString()}
                        </p>
                        <p className="text-green-600 text-xs mt-1">+25% from target</p>
                    </div>
                    <div
                        className="p-4 rounded-xl border-2"
                        style={{ borderColor: primaryColor, backgroundColor: `${primaryColor}05` }}
                    >
                        <p className="font-medium text-sm" style={{ color: primaryColor }}>Expected</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                            ${goal.projection.expected.toLocaleString()}
                        </p>
                        <p className="text-gray-500 text-xs mt-1">+5% from target</p>
                    </div>
                    <div className="p-4 rounded-xl bg-amber-50 border border-amber-100">
                        <p className="text-amber-700 text-sm font-medium">Conservative</p>
                        <p className="text-2xl font-bold text-amber-900 mt-1">
                            ${goal.projection.conservative.toLocaleString()}
                        </p>
                        <p className="text-amber-600 text-xs mt-1">-15% from target</p>
                    </div>
                </div>
            </div>

            {/* Asset Allocation */}
            <div className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Asset Allocation</h2>
                <div className="space-y-3">
                    {Object.entries(goal.allocation).map(([asset, percentage]) => (
                        <div key={asset}>
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-600">{asset}</span>
                                <span className="font-medium text-gray-900">{percentage}%</span>
                            </div>
                            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full rounded-full transition-all duration-500"
                                    style={{
                                        width: `${percentage}%`,
                                        backgroundColor: primaryColor,
                                        opacity: 0.5 + (percentage / 100)
                                    }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
                <div className="divide-y">
                    {goal.transactions.map((tx, index) => (
                        <div key={index} className="py-3 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                                    {tx.type === 'contribution' ? '💵' : tx.type === 'dividend' ? '📈' : '🔄'}
                                </div>
                                <div>
                                    <p className="font-medium text-gray-900 capitalize">{tx.type}</p>
                                    <p className="text-sm text-gray-500">{new Date(tx.date).toLocaleDateString()}</p>
                                </div>
                            </div>
                            {tx.amount > 0 && (
                                <span className={`font-semibold ${tx.type === 'contribution' ? 'text-green-600' : 'text-gray-900'}`}>
                                    {tx.type === 'contribution' ? '+' : ''}${tx.amount.toLocaleString()}
                                </span>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
                <button className="flex-1 px-6 py-4 rounded-xl border-2 border-red-200 text-red-600 font-medium hover:bg-red-50 transition-colors">
                    Pause Goal
                </button>
                <button
                    className="flex-1 px-6 py-4 rounded-xl text-white font-medium transition-all hover:opacity-90"
                    style={{ backgroundColor: primaryColor }}
                >
                    Schedule Extra Deposit
                </button>
            </div>
        </div>
    );
}
