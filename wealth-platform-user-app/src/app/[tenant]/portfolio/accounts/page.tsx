'use client';

import { useState } from 'react';
import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';

const mockAccounts = [
    {
        id: 'acc-1',
        account_name: 'Investment Account',
        account_type: 'investment',
        institution: 'Charles Schwab',
        currency: 'USD',
        current_balance: 325000,
        holdings_count: 15,
        last_sync_at: '2026-01-30T10:30:00Z',
        change_24h: 1250.50,
        change_percentage: 0.39
    },
    {
        id: 'acc-2',
        account_name: 'Savings Account',
        account_type: 'savings',
        institution: 'Emirates NBD',
        currency: 'AED',
        current_balance: 590000,
        holdings_count: 0,
        last_sync_at: '2026-01-30T08:00:00Z',
        change_24h: 0,
        change_percentage: 0
    },
    {
        id: 'acc-3',
        account_name: 'Retirement (401k)',
        account_type: 'retirement',
        institution: 'Fidelity',
        currency: 'USD',
        current_balance: 185000,
        holdings_count: 8,
        last_sync_at: '2026-01-29T22:00:00Z',
        change_24h: 890.00,
        change_percentage: 0.48
    },
    {
        id: 'acc-4',
        account_name: 'Crypto Wallet',
        account_type: 'crypto',
        institution: 'Coinbase',
        currency: 'USD',
        current_balance: 45000,
        holdings_count: 5,
        last_sync_at: '2026-01-30T11:00:00Z',
        change_24h: -320.00,
        change_percentage: -0.71
    }
];

const accountIcons: Record<string, string> = {
    investment: '📈',
    savings: '💰',
    checking: '💳',
    retirement: '🏖️',
    crypto: '₿',
    real_estate: '🏠'
};

export default function AccountsPage() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;
    const [isSyncing, setIsSyncing] = useState(false);

    const totalBalance = mockAccounts.reduce((sum, acc) => {
        // Convert to USD for display
        const usdBalance = acc.currency === 'AED' ? acc.current_balance / 3.67 : acc.current_balance;
        return sum + usdBalance;
    }, 0);

    const handleSync = async () => {
        setIsSyncing(true);
        await new Promise(resolve => setTimeout(resolve, 2000));
        setIsSyncing(false);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Your Accounts</h1>
                    <p className="text-gray-500 mt-1">{mockAccounts.length} accounts connected</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={handleSync}
                        disabled={isSyncing}
                        className="px-4 py-2 rounded-xl border border-gray-200 font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2 disabled:opacity-50"
                    >
                        <span className={isSyncing ? 'animate-spin' : ''}>🔄</span>
                        {isSyncing ? 'Syncing...' : 'Sync All'}
                    </button>
                    <button
                        className="px-4 py-2 rounded-xl text-white font-medium transition-all hover:opacity-90 flex items-center gap-2"
                        style={{ backgroundColor: primaryColor }}
                    >
                        <span>+</span>
                        Add Account
                    </button>
                </div>
            </div>

            {/* Total Value Card */}
            <div
                className="rounded-2xl p-6 text-white"
                style={{
                    background: `linear-gradient(135deg, ${primaryColor} 0%, ${tenant.branding.secondary_color} 100%)`
                }}
            >
                <p className="text-white/70 text-sm">Total Across All Accounts</p>
                <p className="text-4xl font-bold mt-2">
                    ${totalBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <p className="text-white/60 text-sm mt-2">
                    Last synced: {new Date().toLocaleString()}
                </p>
            </div>

            {/* Accounts Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {mockAccounts.map((account) => (
                    <Link
                        key={account.id}
                        href={`/${tenant.slug}/portfolio/accounts/${account.id}`}
                        className="bg-white rounded-2xl shadow-sm border p-6 hover:shadow-lg transition-all group"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div
                                    className="w-12 h-12 rounded-xl flex items-center justify-center text-xl"
                                    style={{ backgroundColor: `${primaryColor}15` }}
                                >
                                    {accountIcons[account.account_type] || '💵'}
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900">{account.account_name}</h3>
                                    <p className="text-sm text-gray-500">{account.institution}</p>
                                </div>
                            </div>
                            <span className="text-xs text-gray-400 capitalize px-2 py-1 bg-gray-100 rounded-full">
                                {account.account_type}
                            </span>
                        </div>

                        <div className="flex justify-between items-end">
                            <div>
                                <p className="text-2xl font-bold text-gray-900">
                                    {account.currency === 'AED' ? 'د.إ' : '$'}
                                    {account.current_balance.toLocaleString()}
                                </p>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className={`text-sm font-medium ${account.change_percentage >= 0 ? 'text-green-600' : 'text-red-600'
                                        }`}>
                                        {account.change_percentage >= 0 ? '+' : ''}
                                        {account.change_percentage.toFixed(2)}%
                                    </span>
                                    <span className="text-gray-400 text-sm">
                                        ({account.change_24h >= 0 ? '+' : ''}{account.currency === 'AED' ? 'د.إ' : '$'}{account.change_24h.toLocaleString()})
                                    </span>
                                </div>
                            </div>
                            <span
                                className="text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity"
                                style={{ color: primaryColor }}
                            >
                                View Details →
                            </span>
                        </div>

                        {/* Last Sync */}
                        <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center text-xs text-gray-400">
                            <span>
                                {account.holdings_count > 0
                                    ? `${account.holdings_count} holdings`
                                    : 'Cash account'}
                            </span>
                            <span>
                                Synced {new Date(account.last_sync_at).toLocaleDateString()} at{' '}
                                {new Date(account.last_sync_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    </Link>
                ))}
            </div>

            {/* Add Account Card */}
            <button className="w-full bg-white rounded-2xl border-2 border-dashed border-gray-200 p-8 hover:border-gray-300 transition-all text-center group">
                <div
                    className="w-16 h-16 rounded-full flex items-center justify-center text-3xl mx-auto mb-4 group-hover:scale-110 transition-transform"
                    style={{ backgroundColor: `${primaryColor}10` }}
                >
                    +
                </div>
                <p className="text-gray-600 font-medium">Connect a New Account</p>
                <p className="text-gray-400 text-sm mt-1">
                    Link your bank, brokerage, or crypto wallet
                </p>
            </button>

            {/* Supported Institutions */}
            <div className="bg-gray-50 rounded-xl p-6">
                <p className="text-sm text-gray-600 mb-4">Supported institutions include:</p>
                <div className="flex flex-wrap gap-4">
                    {['Charles Schwab', 'Fidelity', 'Vanguard', 'Emirates NBD', 'ADCB', 'Al Rajhi Bank', 'Coinbase', 'Interactive Brokers'].map(inst => (
                        <span key={inst} className="px-3 py-1 bg-white rounded-full border text-sm text-gray-600">
                            {inst}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}
