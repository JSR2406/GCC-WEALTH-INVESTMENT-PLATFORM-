'use client';

import { useTenant } from '@/components/tenant/TenantProvider';

// Pie Chart Component (SVG-based)
interface PieChartProps {
    data: { label: string; value: number; color?: string }[];
    size?: number;
    showLegend?: boolean;
}

export function AssetAllocationChart({ data, size = 200, showLegend = true }: PieChartProps) {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const total = data.reduce((sum, item) => sum + item.value, 0);
    let cumulativeAngle = 0;

    const colors = [
        primaryColor,
        tenant.branding.secondary_color,
        '#10B981',
        '#F59E0B',
        '#6366F1',
        '#EC4899',
        '#8B5CF6',
        '#14B8A6'
    ];

    const segments = data.map((item, index) => {
        const percentage = (item.value / total) * 100;
        const angle = (item.value / total) * 360;
        const startAngle = cumulativeAngle;
        cumulativeAngle += angle;

        const startRad = (startAngle - 90) * (Math.PI / 180);
        const endRad = (cumulativeAngle - 90) * (Math.PI / 180);

        const largeArc = angle > 180 ? 1 : 0;
        const radius = size / 2 - 10;
        const centerX = size / 2;
        const centerY = size / 2;

        const x1 = centerX + radius * Math.cos(startRad);
        const y1 = centerY + radius * Math.sin(startRad);
        const x2 = centerX + radius * Math.cos(endRad);
        const y2 = centerY + radius * Math.sin(endRad);

        const path = `
      M ${centerX} ${centerY}
      L ${x1} ${y1}
      A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}
      Z
    `;

        return {
            ...item,
            path,
            color: item.color || colors[index % colors.length],
            percentage: percentage.toFixed(1)
        };
    });

    return (
        <div className="flex flex-col md:flex-row items-center gap-6">
            {/* SVG Pie Chart */}
            <div className="relative">
                <svg width={size} height={size} className="transform -rotate-90">
                    {segments.map((segment, index) => (
                        <path
                            key={index}
                            d={segment.path}
                            fill={segment.color}
                            className="transition-all duration-300 hover:opacity-80 cursor-pointer"
                            style={{ transformOrigin: 'center' }}
                        />
                    ))}
                    {/* Center hole for donut effect */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={size / 4}
                        fill="white"
                    />
                </svg>
                {/* Center text */}
                <div
                    className="absolute inset-0 flex flex-col items-center justify-center"
                >
                    <span className="text-2xl font-bold text-gray-900">100%</span>
                    <span className="text-xs text-gray-500">Allocated</span>
                </div>
            </div>

            {/* Legend */}
            {showLegend && (
                <div className="space-y-2 flex-1">
                    {segments.map((segment, index) => (
                        <div key={index} className="flex items-center justify-between gap-4">
                            <div className="flex items-center gap-2">
                                <div
                                    className="w-3 h-3 rounded-full"
                                    style={{ backgroundColor: segment.color }}
                                />
                                <span className="text-sm text-gray-600">{segment.label}</span>
                            </div>
                            <span className="text-sm font-semibold text-gray-900">
                                {segment.percentage}%
                            </span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

// Performance Chart (Line chart using SVG)
interface PerformanceChartProps {
    data: { date: string; value: number }[];
    height?: number;
}

export function PerformanceChart({ data, height = 200 }: PerformanceChartProps) {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    if (data.length === 0) return null;

    const values = data.map(d => d.value);
    const minValue = Math.min(...values) * 0.95;
    const maxValue = Math.max(...values) * 1.05;
    const range = maxValue - minValue;

    const width = 400;
    const padding = { top: 20, right: 20, bottom: 30, left: 50 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const points = data.map((d, i) => {
        const x = padding.left + (i / (data.length - 1)) * chartWidth;
        const y = padding.top + chartHeight - ((d.value - minValue) / range) * chartHeight;
        return { x, y, ...d };
    });

    const linePath = points.map((p, i) =>
        `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`
    ).join(' ');

    const areaPath = linePath +
        ` L ${points[points.length - 1].x} ${height - padding.bottom}` +
        ` L ${padding.left} ${height - padding.bottom} Z`;

    const isPositive = values[values.length - 1] >= values[0];

    return (
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
            {/* Gradient fill */}
            <defs>
                <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor={isPositive ? primaryColor : '#EF4444'} stopOpacity="0.2" />
                    <stop offset="100%" stopColor={isPositive ? primaryColor : '#EF4444'} stopOpacity="0" />
                </linearGradient>
            </defs>

            {/* Grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => (
                <g key={i}>
                    <line
                        x1={padding.left}
                        y1={padding.top + ratio * chartHeight}
                        x2={width - padding.right}
                        y2={padding.top + ratio * chartHeight}
                        stroke="#E5E7EB"
                        strokeDasharray="4 4"
                    />
                    <text
                        x={padding.left - 10}
                        y={padding.top + ratio * chartHeight + 4}
                        textAnchor="end"
                        className="text-xs fill-gray-400"
                    >
                        ${Math.round(maxValue - ratio * range / 1000)}k
                    </text>
                </g>
            ))}

            {/* Area fill */}
            <path d={areaPath} fill="url(#chartGradient)" />

            {/* Line */}
            <path
                d={linePath}
                stroke={isPositive ? primaryColor : '#EF4444'}
                strokeWidth="2"
                fill="none"
            />

            {/* Data points */}
            {points.map((p, i) => (
                <circle
                    key={i}
                    cx={p.x}
                    cy={p.y}
                    r="4"
                    fill="white"
                    stroke={isPositive ? primaryColor : '#EF4444'}
                    strokeWidth="2"
                    className="opacity-0 hover:opacity-100 transition-opacity cursor-pointer"
                />
            ))}

            {/* X-axis labels */}
            {points.filter((_, i) => i % Math.ceil(data.length / 5) === 0).map((p, i) => (
                <text
                    key={i}
                    x={p.x}
                    y={height - 10}
                    textAnchor="middle"
                    className="text-xs fill-gray-400"
                >
                    {new Date(p.date).toLocaleDateString('en-US', { month: 'short' })}
                </text>
            ))}
        </svg>
    );
}

// Account Card Component
interface AccountCardProps {
    name: string;
    type: string;
    balance: number;
    currency: string;
    change?: number;
    changePercentage?: number;
    onClick?: () => void;
}

export function AccountCard({
    name,
    type,
    balance,
    currency,
    change = 0,
    changePercentage = 0,
    onClick
}: AccountCardProps) {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const accountIcons: Record<string, string> = {
        investment: '📈',
        savings: '💰',
        checking: '💳',
        retirement: '🏖️',
        crypto: '₿'
    };

    const formatCurrency = (amount: number, curr: string) => {
        const symbols: Record<string, string> = { USD: '$', AED: 'د.إ', SAR: '﷼' };
        return `${symbols[curr] || curr} ${amount.toLocaleString()}`;
    };

    return (
        <div
            onClick={onClick}
            className="bg-white rounded-xl p-5 border hover:shadow-lg transition-all cursor-pointer group"
        >
            <div className="flex items-center gap-4">
                <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-xl"
                    style={{ backgroundColor: `${primaryColor}15` }}
                >
                    {accountIcons[type] || '💵'}
                </div>
                <div className="flex-1">
                    <p className="font-semibold text-gray-900">{name}</p>
                    <p className="text-sm text-gray-500 capitalize">{type}</p>
                </div>
                <div className="text-right">
                    <p className="font-bold text-gray-900">{formatCurrency(balance, currency)}</p>
                    <p className={`text-sm ${changePercentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {changePercentage >= 0 ? '+' : ''}{changePercentage.toFixed(2)}%
                    </p>
                </div>
            </div>
        </div>
    );
}

// Transaction List Item
interface TransactionItemProps {
    description: string;
    amount: number;
    currency: string;
    date: string;
    type: 'credit' | 'debit';
    category?: string;
}

export function TransactionItem({
    description,
    amount,
    currency,
    date,
    type,
    category
}: TransactionItemProps) {
    const categoryIcons: Record<string, string> = {
        dividend: '💵',
        interest: '📊',
        deposit: '➕',
        withdrawal: '➖',
        transfer: '🔄',
        fee: '📋',
        purchase: '🛒',
        sale: '💰'
    };

    return (
        <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                    {categoryIcons[category || type] || '📄'}
                </div>
                <div>
                    <p className="font-medium text-gray-900">{description}</p>
                    <p className="text-sm text-gray-500">
                        {new Date(date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric'
                        })}
                    </p>
                </div>
            </div>
            <span className={`font-semibold ${type === 'credit' ? 'text-green-600' : 'text-red-600'}`}>
                {type === 'credit' ? '+' : '-'}{currency === 'USD' ? '$' : currency} {amount.toLocaleString()}
            </span>
        </div>
    );
}
