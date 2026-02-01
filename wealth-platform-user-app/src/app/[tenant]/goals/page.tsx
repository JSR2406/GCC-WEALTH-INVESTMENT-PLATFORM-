'use client';

import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';

const mockGoals = [
    {
        id: '1',
        name: 'Retirement at 55',
        type: 'retirement',
        target_amount: 1000000,
        current_amount: 680000,
        target_date: '2045-01-01',
        monthly_contribution: 2500,
        status: 'active' as const,
        on_track: true
    },
    {
        id: '2',
        name: "Children's Education",
        type: 'education',
        target_amount: 150000,
        current_amount: 67500,
        target_date: '2032-09-01',
        monthly_contribution: 1000,
        status: 'active' as const,
        on_track: true
    },
    {
        id: '3',
        name: 'Dream Home',
        type: 'home',
        target_amount: 500000,
        current_amount: 125000,
        target_date: '2028-06-01',
        monthly_contribution: 3000,
        status: 'active' as const,
        on_track: false
    },
    {
        id: '4',
        name: 'World Travel',
        type: 'travel',
        target_amount: 50000,
        current_amount: 35000,
        target_date: '2026-12-01',
        monthly_contribution: 500,
        status: 'active' as const,
        on_track: true
    }
];

const goalIcons: Record<string, string> = {
    retirement: '🏖️',
    education: '🎓',
    home: '🏠',
    travel: '✈️',
    emergency: '🛟',
    custom: '⭐'
};

export default function GoalsPage() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const totalTarget = mockGoals.reduce((sum, g) => sum + g.target_amount, 0);
    const totalCurrent = mockGoals.reduce((sum, g) => sum + g.current_amount, 0);
    const overallProgress = Math.round((totalCurrent / totalTarget) * 100);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Investment Goals</h1>
                    <p className="text-gray-500 mt-1">Track your financial objectives</p>
                </div>
                <Link
                    href={`/${tenant.slug}/goals/create`}
                    className="px-6 py-3 rounded-xl text-white font-medium transition-all hover:opacity-90 flex items-center gap-2 shadow-lg"
                    style={{ backgroundColor: primaryColor }}
                >
                    <span className="text-xl">+</span>
                    Create New Goal
                </Link>
            </div>

            {/* Summary Card */}
            <div
                className="rounded-2xl p-6 text-white shadow-xl"
                style={{
                    background: `linear-gradient(135deg, ${primaryColor} 0%, ${tenant.branding.secondary_color} 100%)`
                }}
            >
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <p className="text-white/70 text-sm">Total Goals Value</p>
                        <p className="text-3xl font-bold mt-1">
                            ${totalCurrent.toLocaleString()}
                        </p>
                        <p className="text-white/60 text-sm mt-1">
                            of ${totalTarget.toLocaleString()} target
                        </p>
                    </div>
                    <div>
                        <p className="text-white/70 text-sm">Overall Progress</p>
                        <p className="text-3xl font-bold mt-1">{overallProgress}%</p>
                        <div className="w-full h-2 bg-white/20 rounded-full mt-2">
                            <div
                                className="h-full bg-white rounded-full transition-all"
                                style={{ width: `${overallProgress}%` }}
                            />
                        </div>
                    </div>
                    <div>
                        <p className="text-white/70 text-sm">Active Goals</p>
                        <p className="text-3xl font-bold mt-1">{mockGoals.length}</p>
                        <p className="text-white/60 text-sm mt-1">
                            {mockGoals.filter(g => g.on_track).length} on track
                        </p>
                    </div>
                </div>
            </div>

            {/* Goals Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {mockGoals.map((goal) => {
                    const progress = Math.round((goal.current_amount / goal.target_amount) * 100);
                    const remaining = goal.target_amount - goal.current_amount;
                    const targetDate = new Date(goal.target_date);
                    const monthsLeft = Math.max(0, Math.round((targetDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24 * 30)));

                    return (
                        <Link
                            key={goal.id}
                            href={`/${tenant.slug}/goals/${goal.id}`}
                            className="bg-white rounded-2xl shadow-sm border-2 p-6 hover:shadow-lg transition-all group"
                            style={{ borderColor: `${primaryColor}20` }}
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex items-center gap-4">
                                    <div
                                        className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl"
                                        style={{ backgroundColor: `${primaryColor}15` }}
                                    >
                                        {goalIcons[goal.type] || '⭐'}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 text-lg group-hover:text-inherit transition-colors">
                                            {goal.name}
                                        </h3>
                                        <p className="text-sm text-gray-500 capitalize">{goal.type}</p>
                                    </div>
                                </div>
                                <span
                                    className={`px-3 py-1 rounded-full text-xs font-medium ${goal.on_track
                                            ? 'bg-green-100 text-green-700'
                                            : 'bg-amber-100 text-amber-700'
                                        }`}
                                >
                                    {goal.on_track ? '✓ On Track' : '⚠ Behind'}
                                </span>
                            </div>

                            {/* Progress Section */}
                            <div className="mt-6">
                                <div className="flex justify-between items-baseline mb-2">
                                    <span className="text-2xl font-bold text-gray-900">
                                        ${goal.current_amount.toLocaleString()}
                                    </span>
                                    <span className="text-gray-500">
                                        of ${goal.target_amount.toLocaleString()}
                                    </span>
                                </div>
                                <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full rounded-full transition-all duration-700"
                                        style={{
                                            width: `${progress}%`,
                                            backgroundColor: goal.on_track ? primaryColor : '#f59e0b'
                                        }}
                                    />
                                </div>
                                <div className="flex justify-between mt-2 text-sm">
                                    <span className="text-gray-500">{progress}% complete</span>
                                    <span className="text-gray-500">${remaining.toLocaleString()} to go</span>
                                </div>
                            </div>

                            {/* Meta Info */}
                            <div className="mt-6 grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
                                <div>
                                    <p className="text-xs text-gray-400 uppercase">Monthly</p>
                                    <p className="font-semibold text-gray-900">
                                        ${goal.monthly_contribution.toLocaleString()}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs text-gray-400 uppercase">Time Left</p>
                                    <p className="font-semibold text-gray-900">
                                        {monthsLeft} months
                                    </p>
                                </div>
                            </div>
                        </Link>
                    );
                })}
            </div>

            {/* Add Goal Card */}
            <Link
                href={`/${tenant.slug}/goals/create`}
                className="block bg-white rounded-2xl border-2 border-dashed border-gray-200 p-8 hover:border-gray-300 transition-all text-center group"
            >
                <div
                    className="w-16 h-16 rounded-full flex items-center justify-center text-3xl mx-auto mb-4 group-hover:scale-110 transition-transform"
                    style={{ backgroundColor: `${primaryColor}10` }}
                >
                    +
                </div>
                <p className="text-gray-600 font-medium">Create a New Goal</p>
                <p className="text-gray-400 text-sm mt-1">
                    Start planning for your next financial milestone
                </p>
            </Link>
        </div>
    );
}
