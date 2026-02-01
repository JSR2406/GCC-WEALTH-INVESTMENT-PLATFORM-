'use client';

import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';
import { useState } from 'react';
import { FeeDisclosure } from '@/components/fees/FeeDisclosure';
import { apiClient } from '@/lib/api-client';

export default function FatcaReportingPage() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;
    const [showFee, setShowFee] = useState(false);
    const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
    const [chargeId, setChargeId] = useState<string | null>(null);

    const handleAcceptFee = async () => {
        setStatus('processing');
        try {
            // In a real app, we would collect payment method ID via Stripe Elements
            // Here we send a request which will either mock it or fail if no stripe key
            const paymentMethodId = "pm_card_visa"; // Mock payment method

            const result = await apiClient.chargeFee({
                fee_code: "TAX_REPORT_FATCA",
                quantity: 1,
                payment_method_id: paymentMethodId,
                reference_type: "tax_report",
                metadata: { tax_year: new Date().getFullYear() }
            });

            setChargeId(result.charge_id);
            setStatus('success');
            setShowFee(false);
        } catch (error) {
            console.error(error);
            setStatus('error');
        }
    };

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
                        </div>
                    </div>

                    {/* Premium Service Section */}
                    {status === 'success' ? (
                        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                            <div className="text-green-600 text-5xl mb-2">✅</div>
                            <h3 className="text-xl font-bold text-green-800">Payment Successful!</h3>
                            <p className="text-green-700 mt-2">
                                Your certified FATCA report is being generated.
                                <br />Charge ID: <span className="font-mono text-sm">{chargeId}</span>
                            </p>
                            <button className="mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                                Download Report PDF
                            </button>
                        </div>
                    ) : showFee ? (
                        <div className="border-t pt-6">
                            <h3 className="font-semibold text-gray-900 mb-4">Confirm Service Charge</h3>
                            <FeeDisclosure
                                feeCode="TAX_REPORT_FATCA"
                                baseAmount={0}
                                quantity={1}
                                onAccept={handleAcceptFee}
                                onDecline={() => setShowFee(false)}
                            />
                            {status === 'error' && (
                                <p className="text-red-600 text-sm mt-2">
                                    Payment failed. Please try again later (or check Stripe config).
                                </p>
                            )}
                            {status === 'processing' && (
                                <p className="text-blue-600 text-sm mt-2 animate-pulse">
                                    Processing payment...
                                </p>
                            )}
                        </div>
                    ) : (
                        <div className="pt-6 border-t">
                            <div className="bg-amber-50 rounded-xl p-4 mb-4 border border-amber-100">
                                <p className="text-amber-800 text-sm font-medium">
                                    ℹ️ Need a certified report for your accountant? We can generate a fully compliant Form 8938 + FBAR report for you.
                                </p>
                            </div>
                            <button
                                onClick={() => setShowFee(true)}
                                className="w-full py-3 rounded-xl text-white font-medium hover:opacity-90 transition-opacity"
                                style={{ backgroundColor: primaryColor }}
                            >
                                Generate Certified FATCA Report ($19.99)
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
