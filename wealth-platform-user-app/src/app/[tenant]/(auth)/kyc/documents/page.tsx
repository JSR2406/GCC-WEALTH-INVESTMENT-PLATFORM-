'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTenant } from '@/components/tenant/TenantProvider';

interface DocumentUpload {
    type: string;
    file: File | null;
    preview: string | null;
    status: 'pending' | 'uploading' | 'uploaded' | 'error';
}

const requiredDocuments = [
    {
        type: 'passport',
        title: 'Passport',
        description: 'Clear photo of passport bio page',
        icon: '🪪'
    },
    {
        type: 'emirates_id',
        title: 'Emirates ID / Iqama',
        description: 'Front and back of your ID',
        icon: '🆔'
    },
    {
        type: 'address_proof',
        title: 'Proof of Address',
        description: 'Utility bill or bank statement (last 3 months)',
        icon: '📍'
    }
];

export default function KYCDocumentsPage() {
    const router = useRouter();
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const [documents, setDocuments] = useState<Record<string, DocumentUpload>>(() => {
        const initial: Record<string, DocumentUpload> = {};
        requiredDocuments.forEach(doc => {
            initial[doc.type] = { type: doc.type, file: null, preview: null, status: 'pending' };
        });
        return initial;
    });

    const handleFileSelect = (type: string, file: File) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            setDocuments(prev => ({
                ...prev,
                [type]: {
                    ...prev[type],
                    file,
                    preview: e.target?.result as string,
                    status: 'uploaded'
                }
            }));
        };
        reader.readAsDataURL(file);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        router.push(`/${tenant.slug}/auth/kyc/verification`);
    };

    const allUploaded = Object.values(documents).every(doc => doc.status === 'uploaded');

    return (
        <div className="max-w-2xl mx-auto">
            {/* Progress */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    {['Personal Info', 'Documents', 'Verification'].map((step, index) => (
                        <div key={step} className="flex items-center">
                            <div
                                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${index <= 1 ? 'text-white' : 'bg-gray-100 text-gray-400'
                                    }`}
                                style={{ backgroundColor: index <= 1 ? primaryColor : undefined }}
                            >
                                {index < 1 ? '✓' : index + 1}
                            </div>
                            {index < 2 && (
                                <div
                                    className="w-20 sm:w-32 h-1 mx-2 rounded"
                                    style={{ backgroundColor: index < 1 ? primaryColor : '#e5e7eb' }}
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

            {/* Form */}
            <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border p-6">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">Document Upload</h1>
                <p className="text-gray-500 mb-6">Upload clear photos of the following documents</p>

                <div className="space-y-4">
                    {requiredDocuments.map((doc) => (
                        <div
                            key={doc.type}
                            className={`border-2 rounded-xl p-4 transition-all ${documents[doc.type].status === 'uploaded'
                                    ? 'border-green-300 bg-green-50'
                                    : 'border-dashed border-gray-200 hover:border-gray-300'
                                }`}
                        >
                            <div className="flex items-start gap-4">
                                <div
                                    className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
                                    style={{ backgroundColor: `${primaryColor}15` }}
                                >
                                    {doc.icon}
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-semibold text-gray-900">{doc.title}</h3>
                                    <p className="text-sm text-gray-500">{doc.description}</p>

                                    {documents[doc.type].preview ? (
                                        <div className="mt-3 flex items-center gap-3">
                                            <img
                                                src={documents[doc.type].preview!}
                                                alt={doc.title}
                                                className="w-20 h-14 object-cover rounded-lg"
                                            />
                                            <div className="flex-1">
                                                <p className="text-sm font-medium text-gray-900">
                                                    {documents[doc.type].file?.name}
                                                </p>
                                                <p className="text-xs text-gray-500">
                                                    {((documents[doc.type].file?.size || 0) / 1024).toFixed(1)} KB
                                                </p>
                                            </div>
                                            <button
                                                type="button"
                                                onClick={() => setDocuments(prev => ({
                                                    ...prev,
                                                    [doc.type]: { ...prev[doc.type], file: null, preview: null, status: 'pending' }
                                                }))}
                                                className="text-red-500 hover:text-red-700 text-sm"
                                            >
                                                Remove
                                            </button>
                                        </div>
                                    ) : (
                                        <label className="mt-3 flex items-center justify-center gap-2 px-4 py-3 rounded-lg border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors">
                                            <span className="text-gray-600">📤</span>
                                            <span className="text-sm font-medium text-gray-600">Upload File</span>
                                            <input
                                                type="file"
                                                accept="image/*,.pdf"
                                                onChange={(e) => {
                                                    const file = e.target.files?.[0];
                                                    if (file) handleFileSelect(doc.type, file);
                                                }}
                                                className="hidden"
                                            />
                                        </label>
                                    )}
                                </div>
                                {documents[doc.type].status === 'uploaded' && (
                                    <span className="text-green-500 text-xl">✓</span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Additional Notes */}
                <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                    <h4 className="font-medium text-amber-900 mb-2">📸 Photo Tips</h4>
                    <ul className="text-sm text-amber-800 space-y-1">
                        <li>• Ensure all text is clearly readable</li>
                        <li>• Avoid glare and shadows</li>
                        <li>• Include all four corners of the document</li>
                        <li>• Maximum file size: 10MB per document</li>
                    </ul>
                </div>

                {/* Navigation */}
                <div className="flex justify-between mt-8 pt-6 border-t">
                    <button
                        type="button"
                        onClick={() => router.back()}
                        className="px-6 py-3 rounded-xl border border-gray-200 font-medium text-gray-600 hover:bg-gray-50 transition-colors"
                    >
                        Back
                    </button>
                    <button
                        type="submit"
                        disabled={!allUploaded}
                        className="px-8 py-3 rounded-xl text-white font-medium transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
                        style={{ backgroundColor: primaryColor }}
                    >
                        Continue to Verification
                    </button>
                </div>
            </form>

            {/* Security */}
            <div className="flex items-center justify-center gap-2 mt-6 text-gray-400 text-xs">
                <span>🔒</span>
                <span>Your documents are encrypted and stored securely</span>
            </div>
        </div>
    );
}
