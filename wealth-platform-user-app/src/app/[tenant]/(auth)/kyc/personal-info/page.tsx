'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTenant } from '@/components/tenant/TenantProvider';
import Link from 'next/link';

export default function KYCPersonalInfoPage() {
    const router = useRouter();
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        date_of_birth: '',
        nationality: '',
        gender: '',
        marital_status: '',
        employment_status: '',
        occupation: '',
        annual_income: '',
        source_of_wealth: ''
    });

    const updateForm = (field: string, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        router.push(`/${tenant.slug}/auth/kyc/documents`);
    };

    return (
        <div className="max-w-2xl mx-auto">
            {/* Progress */}
            <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                    {['Personal Info', 'Documents', 'Verification'].map((step, index) => (
                        <div key={step} className="flex items-center">
                            <div
                                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${index === 0 ? 'text-white' : 'bg-gray-100 text-gray-400'
                                    }`}
                                style={{ backgroundColor: index === 0 ? primaryColor : undefined }}
                            >
                                {index + 1}
                            </div>
                            {index < 2 && (
                                <div className="w-20 sm:w-32 h-1 mx-2 bg-gray-200 rounded" />
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
                <h1 className="text-2xl font-bold text-gray-900 mb-2">Personal Information</h1>
                <p className="text-gray-500 mb-6">Tell us about yourself to comply with regulatory requirements</p>

                <div className="space-y-5">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                            <input
                                type="text"
                                value={formData.first_name}
                                onChange={(e) => updateForm('first_name', e.target.value)}
                                required
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 outline-none transition-all"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                            <input
                                type="text"
                                value={formData.last_name}
                                onChange={(e) => updateForm('last_name', e.target.value)}
                                required
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 outline-none transition-all"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Date of Birth</label>
                            <input
                                type="date"
                                value={formData.date_of_birth}
                                onChange={(e) => updateForm('date_of_birth', e.target.value)}
                                required
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 outline-none transition-all"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Nationality</label>
                            <select
                                value={formData.nationality}
                                onChange={(e) => updateForm('nationality', e.target.value)}
                                required
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                            >
                                <option value="">Select...</option>
                                <option value="AE">United Arab Emirates</option>
                                <option value="SA">Saudi Arabia</option>
                                <option value="US">United States</option>
                                <option value="GB">United Kingdom</option>
                                <option value="IN">India</option>
                                <option value="PK">Pakistan</option>
                                <option value="EG">Egypt</option>
                                <option value="JO">Jordan</option>
                                <option value="LB">Lebanon</option>
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                            <select
                                value={formData.gender}
                                onChange={(e) => updateForm('gender', e.target.value)}
                                required
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                            >
                                <option value="">Select...</option>
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Marital Status</label>
                            <select
                                value={formData.marital_status}
                                onChange={(e) => updateForm('marital_status', e.target.value)}
                                required
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                            >
                                <option value="">Select...</option>
                                <option value="single">Single</option>
                                <option value="married">Married</option>
                                <option value="divorced">Divorced</option>
                                <option value="widowed">Widowed</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Employment Status</label>
                        <select
                            value={formData.employment_status}
                            onChange={(e) => updateForm('employment_status', e.target.value)}
                            required
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                        >
                            <option value="">Select...</option>
                            <option value="employed">Employed</option>
                            <option value="self_employed">Self-Employed</option>
                            <option value="business_owner">Business Owner</option>
                            <option value="retired">Retired</option>
                            <option value="student">Student</option>
                            <option value="unemployed">Unemployed</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Occupation</label>
                        <input
                            type="text"
                            value={formData.occupation}
                            onChange={(e) => updateForm('occupation', e.target.value)}
                            placeholder="e.g., Software Engineer, Doctor, Businessman"
                            required
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 outline-none transition-all"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Annual Income (USD)</label>
                        <select
                            value={formData.annual_income}
                            onChange={(e) => updateForm('annual_income', e.target.value)}
                            required
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                        >
                            <option value="">Select range...</option>
                            <option value="0-50000">Less than $50,000</option>
                            <option value="50000-100000">$50,000 - $100,000</option>
                            <option value="100000-250000">$100,000 - $250,000</option>
                            <option value="250000-500000">$250,000 - $500,000</option>
                            <option value="500000-1000000">$500,000 - $1,000,000</option>
                            <option value="1000000+">Over $1,000,000</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Primary Source of Wealth</label>
                        <select
                            value={formData.source_of_wealth}
                            onChange={(e) => updateForm('source_of_wealth', e.target.value)}
                            required
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                        >
                            <option value="">Select...</option>
                            <option value="salary">Employment Income</option>
                            <option value="business">Business Profits</option>
                            <option value="investments">Investment Returns</option>
                            <option value="inheritance">Inheritance</option>
                            <option value="property">Property Sales</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>

                {/* Navigation */}
                <div className="flex justify-between mt-8 pt-6 border-t">
                    <Link
                        href={`/${tenant.slug}/auth/signup`}
                        className="px-6 py-3 rounded-xl border border-gray-200 font-medium text-gray-600 hover:bg-gray-50 transition-colors"
                    >
                        Back
                    </Link>
                    <button
                        type="submit"
                        className="px-8 py-3 rounded-xl text-white font-medium transition-all hover:opacity-90"
                        style={{ backgroundColor: primaryColor }}
                    >
                        Continue
                    </button>
                </div>
            </form>

            {/* Privacy Note */}
            <p className="text-center text-gray-400 text-xs mt-6">
                Your information is encrypted and protected. We comply with UAE/KSA data protection regulations.
            </p>
        </div>
    );
}
