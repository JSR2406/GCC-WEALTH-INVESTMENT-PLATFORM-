'use client';

import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';

export default function FatcaReportingPage() {
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
                    <div className="text-4xl">🇺🇸</div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">FATCA Reporting</h1>
                        <p className="text-gray-500">Foreign Account Tax Compliance Act</p>
                    </div>
                    <span className="ml-auto px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                        Action Required
                    </span>
                </div>

                <div className="space-y-6">
                    <div className="bg-gray-50 p-4 rounded-xl border">
                        <h3 className="font-semibold text-gray-900 mb-2">Status Overview</h3>
                        <p className="text-sm text-gray-600">
                            Our records indicate you may be a U.S. person for tax purposes.
                            FATCA regulations require us to report your account details to the IRS.
                        </p>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-900 mb-4">Required Documents</h3>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 border rounded-lg">
                                <span className="text-gray-700">Form W-9 (Request for Taxpayer ID)</span>
                                <button className="text-blue-600 font-medium text-sm hover:underline">Download</button>
                            </div>
                            <div className="flex items-center justify-between p-3 border rounded-lg">
                                <span className="text-gray-700">Form 8938 (Statement of Foreign Financial Assets)</span>
                                <button className="text-blue-600 font-medium text-sm hover:underline">Upload</button>
                            </div>
                        </div>
                    </div>

                    <div className="pt-6 border-t">
                        <button
                            className="w-full py-3 rounded-xl text-white font-medium hover:opacity-90 transition-opacity"
                            style={{ backgroundColor: primaryColor }}
                        >
                            Start FATCA Certification
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
