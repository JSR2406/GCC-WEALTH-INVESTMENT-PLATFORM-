'use client';

import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';

// Mock data for demo
const mockPortfolioData = {
    total_aum: 485750.00,
    currency: 'USD',
    change_today: 2340.50,
    change_percentage: 0.48,
    accounts: [
        { id: '1', name: 'Investment Account', type: 'investment', balance: 325000, currency: 'USD' },
        { id: '2', name: 'Savings Account', type: 'savings', balance: 160750, currency: 'USD' },
    ],
    goals: [
        { id: '1', name: 'Retirement', progress: 68, target: 1000000 },
        { id: '2', name: 'Education Fund', progress: 45, target: 150000 },
    ],
    allocation: {
        'Stocks': 60,
        'Bonds': 25,
        'Cash': 10,
        'Alternatives': 5
    }
};

export default function PortfolioDashboard() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Welcome Section */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">
                        Welcome back! 👋
                    </h1>
                    <p className="text-gray-500 mt-1">
                        Here's your portfolio overview as of today
                    </p>
                </div>
                <button
                    className="px-4 py-2 rounded-lg text-white font-medium transition-all hover:opacity-90 flex items-center gap-2"
                    style={{ backgroundColor: primaryColor }}
                >
                    <span>🔄</span>
                    Sync Accounts
                </button>
            </div>

            {/* Net Worth Card */}
            <div
                className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 text-white shadow-xl"
                style={{
                    background: `linear-gradient(135deg, ${primaryColor} 0%, ${tenant.branding.secondary_color} 100%)`
                }}
            >
                <p className="text-white/80 text-sm font-medium uppercase tracking-wide">
                    Total Net Worth
                </p>
                <div className="flex items-baseline gap-2 mt-2">
                    <span className="text-5xl font-bold">
                        ${mockPortfolioData.total_aum.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </span>
                </div>
                <div className="flex items-center gap-2 mt-4">
                    <span className={`px-2 py-1 rounded text-sm font-medium ${mockPortfolioData.change_percentage >= 0
                            ? 'bg-green-500/20 text-green-200'
                            : 'bg-red-500/20 text-red-200'
                        }`}>
                        {mockPortfolioData.change_percentage >= 0 ? '+' : ''}
                        {mockPortfolioData.change_percentage.toFixed(2)}%
                    </span>
                    <span className="text-white/60 text-sm">
                        {mockPortfolioData.change_percentage >= 0 ? '+' : ''}
                        ${mockPortfolioData.change_today.toLocaleString()} today
                    </span>
                </div>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    icon="💰"
                    label="Accounts"
                    value={mockPortfolioData.accounts.length.toString()}
                    sublabel="Connected"
                    color={primaryColor}
                />
                <StatCard
                    icon="🎯"
                    label="Goals"
                    value={mockPortfolioData.goals.length.toString()}
                    sublabel="Active"
                    color={primaryColor}
                />
                <StatCard
                    icon="📈"
                    label="Avg Return"
                    value="12.4%"
                    sublabel="YTD"
                    color={primaryColor}
                />
                <StatCard
                    icon="⚡"
                    label="Risk Score"
                    value="Moderate"
                    sublabel="Well-balanced"
                    color={primaryColor}
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Accounts Section */}
                <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-lg font-semibold text-gray-900">Your Accounts</h2>
                        <Link
                            href={`/${tenant.slug}/portfolio/accounts`}
                            className="text-sm font-medium hover:underline"
                            style={{ color: primaryColor }}
                        >
                            View All →
                        </Link>
                    </div>
                    <div className="space-y-4">
                        {mockPortfolioData.accounts.map((account) => (
                            <div
                                key={account.id}
                                className="flex items-center justify-between p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer"
                            >
                                <div className="flex items-center gap-4">
                                    <div
                                        className="w-12 h-12 rounded-full flex items-center justify-center text-white text-lg"
                                        style={{ backgroundColor: account.type === 'investment' ? primaryColor : tenant.branding.secondary_color }}
                                    >
                                        {account.type === 'investment' ? '📊' : '💵'}
                                    </div>
                                    <div>
                                        <p className="font-medium text-gray-900">{account.name}</p>
                                        <p className="text-sm text-gray-500 capitalize">{account.type}</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="font-semibold text-gray-900">
                                        ${account.balance.toLocaleString()}
                                    </p>
                                    <p className="text-sm text-gray-500">{account.currency}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Asset Allocation */}
                <div className="bg-white rounded-xl shadow-sm border p-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-6">Asset Allocation</h2>
                    <div className="space-y-4">
                        {Object.entries(mockPortfolioData.allocation).map(([asset, percentage]) => (
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
                                            opacity: 0.5 + (percentage / 200)
                                        }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Goals Section */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-lg font-semibold text-gray-900">Investment Goals</h2>
                    <Link
                        href={`/${tenant.slug}/goals/create`}
                        className="px-4 py-2 rounded-lg text-white text-sm font-medium transition-all hover:opacity-90 flex items-center gap-2"
                        style={{ backgroundColor: primaryColor }}
                    >
                        <span>+</span>
                        New Goal
                    </Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {mockPortfolioData.goals.map((goal) => (
                        <Link
                            key={goal.id}
                            href={`/${tenant.slug}/goals/${goal.id}`}
                            className="p-4 rounded-xl border-2 hover:border-gray-300 transition-all group"
                            style={{ borderColor: `${primaryColor}30` }}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <p className="font-semibold text-gray-900 group-hover:text-inherit transition-colors" style={{ '--hover-color': primaryColor } as React.CSSProperties}>
                                        {goal.name}
                                    </p>
                                    <p className="text-sm text-gray-500">
                                        Target: ${goal.target.toLocaleString()}
                                    </p>
                                </div>
                                <span
                                    className="px-2 py-1 rounded text-xs font-medium"
                                    style={{
                                        backgroundColor: `${primaryColor}15`,
                                        color: primaryColor
                                    }}
                                >
                                    {goal.progress}%
                                </span>
                            </div>
                            {/* Progress Ring */}
                            <div className="flex items-center gap-4">
                                <div className="relative w-16 h-16">
                                    <svg className="w-full h-full -rotate-90">
                                        <circle
                                            cx="32"
                                            cy="32"
                                            r="28"
                                            stroke="#e5e7eb"
                                            strokeWidth="6"
                                            fill="none"
                                        />
                                        <circle
                                            cx="32"
                                            cy="32"
                                            r="28"
                                            stroke={primaryColor}
                                            strokeWidth="6"
                                            fill="none"
                                            strokeDasharray={`${goal.progress * 1.76} 176`}
                                            className="transition-all duration-500"
                                        />
                                    </svg>
                                    <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-gray-700">
                                        {goal.progress}%
                                    </span>
                                </div>
                                <div className="flex-1">
                                    <div className="text-sm text-gray-500">Progress</div>
                                    <div className="font-semibold text-gray-900">
                                        ${((goal.target * goal.progress) / 100).toLocaleString()}
                                        <span className="text-gray-400 font-normal"> / ${goal.target.toLocaleString()}</span>
                                    </div>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <QuickAction
                    href={`/${tenant.slug}/portfolio/accounts`}
                    icon="➕"
                    label="Add Account"
                    color={primaryColor}
                />
                <QuickAction
                    href={`/${tenant.slug}/goals/create`}
                    icon="🎯"
                    label="Create Goal"
                    color={primaryColor}
                />
                <QuickAction
                    href={`/${tenant.slug}/tax`}
                    icon="📋"
                    label="Tax Reports"
                    color={primaryColor}
                />
                {tenant.features.zakat_calculator && (
                    <QuickAction
                        href={`/${tenant.slug}/tax/zakat`}
                        icon="🕌"
                        label="Zakat Calculator"
                        color={primaryColor}
                    />
                )}
            </div>
        </div>
    );
}

function StatCard({ icon, label, value, sublabel, color }: {
    icon: string;
    label: string;
    value: string;
    sublabel: string;
    color: string;
}) {
    return (
        <div className="bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center gap-3">
                <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                    style={{ backgroundColor: `${color}15` }}
                >
                    {icon}
                </div>
                <div>
                    <p className="text-sm text-gray-500">{label}</p>
                    <p className="font-semibold text-gray-900">{value}</p>
                    <p className="text-xs text-gray-400">{sublabel}</p>
                </div>
            </div>
        </div>
    );
}

function QuickAction({ href, icon, label, color }: {
    href: string;
    icon: string;
    label: string;
    color: string;
}) {
    return (
        <Link
            href={href}
            className="bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition-all flex flex-col items-center justify-center gap-2 text-center group"
        >
            <div
                className="w-12 h-12 rounded-full flex items-center justify-center text-xl group-hover:scale-110 transition-transform"
                style={{ backgroundColor: `${color}15` }}
            >
                {icon}
            </div>
            <span className="text-sm font-medium text-gray-700">{label}</span>
        </Link>
    );
}
