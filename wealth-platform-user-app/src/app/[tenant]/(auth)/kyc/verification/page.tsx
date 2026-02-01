'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTenant } from '@/components/tenant/TenantProvider';

export default function KYCVerificationPage() {
    const router = useRouter();
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const [verificationStatus, setVerificationStatus] = useState<'processing' | 'success' | 'failed'>('processing');
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        // Simulate verification process
        const interval = setInterval(() => {
            setProgress(prev => {
                if (prev >= 100) {
                    clearInterval(interval);
                    setVerificationStatus('success');
                    return 100;
                }
                return prev + 10;
            });
        }, 500);

        return () => clearInterval(interval);
    }, []);

    const handleComplete = () => {
        router.push(`/${tenant.slug}`);
    };

    return (
        <div className="max-w-2xl mx-auto">
            {/* Progress */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    {['Personal Info', 'Documents', 'Verification'].map((step, index) => (
                        <div key={step} className="flex items-center">
                            <div
                                className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium text-white"
                                style={{ backgroundColor: primaryColor }}
                            >
                                {index < 2 ? '✓' : index + 1}
                            </div>
                            {index < 2 && (
                                <div
                                    className="w-20 sm:w-32 h-1 mx-2 rounded"
                                    style={{ backgroundColor: primaryColor }}
                                />
                            )}
                        </div>
                    ))}
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                    <span>Personal Info</span>
                    <span>Documents</span>
                    <span>Verification</span>
                </div>
            </div>

            {/* Verification Card */}
            <div className="bg-white rounded-2xl shadow-sm border p-8 text-center">
                {verificationStatus === 'processing' && (
                    <>
                        <div className="w-24 h-24 mx-auto mb-6 relative">
                            <svg className="w-full h-full animate-spin" viewBox="0 0 100 100">
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="40"
                                    stroke="#e5e7eb"
                                    strokeWidth="8"
                                    fill="none"
                                />
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="40"
                                    stroke={primaryColor}
                                    strokeWidth="8"
                                    fill="none"
                                    strokeDasharray={`${progress * 2.51} 251`}
                                    strokeLinecap="round"
                                    className="transition-all duration-300"
                                />
                            </svg>
                            <span className="absolute inset-0 flex items-center justify-center text-xl font-bold text-gray-900">
                                {progress}%
                            </span>
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">Verifying Your Documents</h1>
                        <p className="text-gray-500 mb-6">
                            Please wait while we verify your identity...
                        </p>
                        <div className="space-y-3 text-left max-w-xs mx-auto">
                            {[
                                { label: 'Checking document authenticity', done: progress >= 30 },
                                { label: 'Verifying personal information', done: progress >= 60 },
                                { label: 'Running compliance checks', done: progress >= 90 },
                                { label: 'Finalizing verification', done: progress >= 100 },
                            ].map((step, index) => (
                                <div
                                    key={index}
                                    className={`flex items-center gap-3 ${step.done ? 'text-gray-900' : 'text-gray-400'}`}
                                >
                                    {step.done ? (
                                        <span className="text-green-500">✓</span>
                                    ) : (
                                        <span className="animate-pulse">○</span>
                                    )}
                                    <span className="text-sm">{step.label}</span>
                                </div>
                            ))}
                        </div>
                    </>
                )}

                {verificationStatus === 'success' && (
                    <>
                        <div
                            className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center text-5xl animate-scale-in"
                            style={{ backgroundColor: `${primaryColor}15` }}
                        >
                            ✓
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">Verification Complete!</h1>
                        <p className="text-gray-500 mb-8">
                            Your identity has been verified successfully. You can now start managing your wealth.
                        </p>
                        <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-8 text-left">
                            <h3 className="font-medium text-green-900 mb-2">✓ Account Activated</h3>
                            <p className="text-green-700 text-sm">
                                Your account is now fully verified and ready to use. You have access to all
                                platform features including portfolio tracking, goal-based investing, and tax reporting.
                            </p>
                        </div>
                        <button
                            onClick={handleComplete}
                            className="w-full px-8 py-4 rounded-xl text-white font-semibold text-lg transition-all hover:opacity-90"
                            style={{ backgroundColor: primaryColor }}
                        >
                            Get Started
                        </button>
                    </>
                )}

                {verificationStatus === 'failed' && (
                    <>
                        <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-red-100 flex items-center justify-center text-5xl">
                            ✗
                        </div>
                        <h1 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h1>
                        <p className="text-gray-500 mb-8">
                            We couldn't verify your documents. Please check the following and try again:
                        </p>
                        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-8 text-left">
                            <ul className="text-red-700 text-sm space-y-2">
                                <li>• Ensure all documents are clearly visible</li>
                                <li>• Check that documents are not expired</li>
                                <li>• Make sure names match across all documents</li>
                            </ul>
                        </div>
                        <button
                            onClick={() => router.push(`/${tenant.slug}/auth/kyc/documents`)}
                            className="w-full px-8 py-4 rounded-xl text-white font-semibold text-lg transition-all hover:opacity-90"
                            style={{ backgroundColor: primaryColor }}
                        >
                            Re-upload Documents
                        </button>
                    </>
                )}
            </div>

            {/* Help */}
            <div className="mt-6 text-center">
                <p className="text-gray-400 text-sm">
                    Having trouble? <a href="#" className="underline" style={{ color: primaryColor }}>Contact Support</a>
                </p>
            </div>
        </div>
    );
}
