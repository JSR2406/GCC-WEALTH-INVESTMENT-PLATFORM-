'use client';

import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';

export default function TaxOverviewPage() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;
    const currentYear = new Date().getFullYear();

    const taxReports = [
        {
            id: 'fatca',
            title: 'FATCA Reporting',
            description: 'Foreign Account Tax Compliance Act (US Persons)',
            icon: '🇺🇸',
            status: 'required',
            deadline: `April 15, ${currentYear + 1}`,
            href: `/${tenant.slug}/tax/fatca`
        },
        {
            id: 'crs',
            title: 'CRS Reporting',
            description: 'Common Reporting Standard (OECD Countries)',
            icon: '🌍',
            status: 'optional',
            deadline: 'Automatic',
            href: `/${tenant.slug}/tax/crs`
        },
    ];

    // Add Zakat if enabled for this tenant
    if (tenant.features.zakat_calculator) {
        taxReports.push({
            id: 'zakat',
            title: 'Zakat Calculator',
            description: 'Islamic alms tax calculation',
            icon: '🕌',
            status: 'optional',
            deadline: 'Ramadan',
            href: `/${tenant.slug}/tax/zakat`
        });
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Tax Reports</h1>
                <p className="text-gray-500 mt-1">Manage your tax compliance and reporting</p>
            </div>

            {/* Summary Card */}
            <div
                className="rounded-2xl p-6 text-white"
                style={{
                    background: `linear-gradient(135deg, ${primaryColor} 0%, ${tenant.branding.secondary_color} 100%)`
                }}
            >
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <p className="text-white/70 text-sm">Tax Year</p>
                        <p className="text-3xl font-bold">{currentYear}</p>
                    </div>
                    <div className="flex gap-4">
                        <div className="text-center">
                            <p className="text-white/70 text-sm">Reports Due</p>
                            <p className="text-2xl font-bold">1</p>
                        </div>
                        <div className="text-center">
                            <p className="text-white/70 text-sm">Completed</p>
                            <p className="text-2xl font-bold">0</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tax Reports Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {taxReports.map((report) => (
                    <Link
                        key={report.id}
                        href={report.href}
                        className="bg-white rounded-2xl shadow-sm border p-6 hover:shadow-lg transition-all group"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div
                                className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl"
                                style={{ backgroundColor: `${primaryColor}15` }}
                            >
                                {report.icon}
                            </div>
                            <span
                                className={`px-3 py-1 rounded-full text-xs font-medium ${report.status === 'required'
                                        ? 'bg-red-100 text-red-700'
                                        : 'bg-gray-100 text-gray-600'
                                    }`}
                            >
                                {report.status === 'required' ? 'Required' : 'Optional'}
                            </span>
                        </div>

                        <h3 className="font-semibold text-gray-900 text-lg">{report.title}</h3>
                        <p className="text-gray-500 text-sm mt-1">{report.description}</p>

                        <div className="mt-4 pt-4 border-t flex justify-between items-center">
                            <div>
                                <p className="text-xs text-gray-400">Deadline</p>
                                <p className="font-medium text-gray-900">{report.deadline}</p>
                            </div>
                            <span
                                className="text-sm font-medium group-hover:translate-x-1 transition-transform"
                                style={{ color: primaryColor }}
                            >
                                View →
                            </span>
                        </div>
                    </Link>
                ))}
            </div>

            {/* Important Documents */}
            <div className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Tax Documents</h2>
                <div className="space-y-3">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                        <div className="flex items-center gap-3">
                            <span className="text-xl">📄</span>
                            <div>
                                <p className="font-medium text-gray-900">Annual Tax Statement {currentYear - 1}</p>
                                <p className="text-sm text-gray-500">Generated: Jan 15, {currentYear}</p>
                            </div>
                        </div>
                        <button
                            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80"
                            style={{ backgroundColor: `${primaryColor}15`, color: primaryColor }}
                        >
                            Download PDF
                        </button>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                        <div className="flex items-center gap-3">
                            <span className="text-xl">📄</span>
                            <div>
                                <p className="font-medium text-gray-900">Capital Gains Summary {currentYear - 1}</p>
                                <p className="text-sm text-gray-500">Generated: Jan 15, {currentYear}</p>
                            </div>
                        </div>
                        <button
                            className="px-4 py-2 rounded-lg text-sm font-medium transition-colors hover:opacity-80"
                            style={{ backgroundColor: `${primaryColor}15`, color: primaryColor }}
                        >
                            Download PDF
                        </button>
                    </div>
                </div>
            </div>

            {/* Help Section */}
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                <div className="flex gap-4">
                    <span className="text-2xl">💡</span>
                    <div>
                        <h3 className="font-semibold text-amber-900">Need Help with Tax Reporting?</h3>
                        <p className="text-amber-700 text-sm mt-1">
                            Our tax compliance engine automatically generates required reports based on your
                            residency and citizenship. For specific tax advice, please consult a qualified
                            tax professional.
                        </p>
                        <button
                            className="mt-3 text-sm font-medium text-amber-900 underline"
                        >
                            Learn more about cross-border taxation →
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
