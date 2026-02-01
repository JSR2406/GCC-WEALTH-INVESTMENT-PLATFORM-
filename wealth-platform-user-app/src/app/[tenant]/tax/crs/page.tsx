'use client';

import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';

export default function CrsReportingPage() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    return (
        <div className="space-y-6 max-w-3xl mx-auto">
            <Link
                href={`/${tenant.slug}/tax`}
                className="text-gray-500 hover:text-gray-900 flex items-center gap-2 mb-4"
            >
                ← Back to Tax Dashboard
            </Link>

            <div className="bg-white rounded-2xl shadow-sm border p-8">
                <div className="flex items-center gap-4 mb-6">
                    <div className="text-4xl">🌍</div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">CRS Reporting</h1>
                        <p className="text-gray-500">Common Reporting Standard</p>
                    </div>
                    <span className="ml-auto px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                        Compliant
                    </span>
                </div>

                <div className="space-y-6">
                    <div className="bg-gray-50 p-4 rounded-xl border">
                        <h3 className="font-semibold text-gray-900 mb-2">Status Overview</h3>
                        <p className="text-sm text-gray-600">
                            Your tax residency information is up to date. We will automatically exchange your
                            account information with the relevant tax authorities in participating jurisdictions
                            as per OECD guidelines.
                        </p>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-900 mb-4">Tax Residencies on File</h3>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 border rounded-lg">
                                <div className="flex items-center gap-2">
                                    <span>🇦🇪</span>
                                    <span className="font-medium text-gray-900">United Arab Emirates</span>
                                </div>
                                <span className="text-sm text-gray-500">Primary</span>
                            </div>
                        </div>
                    </div>

                    <div className="pt-6 border-t flex justify-end">
                        <button
                            className="px-6 py-2 rounded-lg border font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                            Update Tax Residency
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
