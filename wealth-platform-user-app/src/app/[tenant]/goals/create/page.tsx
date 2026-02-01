'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTenant } from '@/components/tenant/TenantProvider';

const goalTypes = [
    { value: 'retirement', label: 'Retirement', icon: '🏖️', description: 'Secure your golden years' },
    { value: 'education', label: 'Education', icon: '🎓', description: "Children's university fund" },
    { value: 'home', label: 'Buy a Home', icon: '🏠', description: 'Save for a down payment' },
    { value: 'travel', label: 'Travel', icon: '✈️', description: 'Your dream vacation' },
    { value: 'emergency', label: 'Emergency Fund', icon: '🛟', description: '6+ months of expenses' },
    { value: 'custom', label: 'Custom Goal', icon: '⭐', description: 'Define your own goal' },
];

const riskProfiles = [
    { value: 'conservative', label: 'Conservative', description: 'Lower risk, steady growth', allocation: 'Bonds 60%, Stocks 30%, Cash 10%' },
    { value: 'moderate', label: 'Moderate', description: 'Balanced risk and reward', allocation: 'Stocks 60%, Bonds 30%, Alternatives 10%' },
    { value: 'aggressive', label: 'Aggressive', description: 'Higher risk, higher potential', allocation: 'Stocks 80%, Alternatives 15%, Bonds 5%' },
];

export default function CreateGoalPage() {
    const router = useRouter();
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        goal_type: '',
        name: '',
        target_amount: 0,
        target_date: '',
        monthly_contribution: 0,
        risk_profile: 'moderate',
        is_sharia_compliant: false
    });

    const updateForm = (field: string, value: unknown) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = async () => {
        // TODO: API call to create goal
        console.log('Creating goal:', formData);
        router.push(`/${tenant.slug}/goals`);
    };

    const canProceed = (currentStep: number): boolean => {
        switch (currentStep) {
            case 1: return !!formData.goal_type;
            case 2: return !!formData.name && formData.target_amount > 0 && !!formData.target_date;
            case 3: return !!formData.risk_profile;
            case 4: return true;
            default: return false;
        }
    };

    return (
        <div className="max-w-3xl mx-auto">
            {/* Progress Steps */}
            <div className="mb-8">
                <div className="flex items-center justify-between">
                    {['Goal Type', 'Target', 'Risk Profile', 'Review'].map((label, index) => (
                        <div key={label} className="flex items-center">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all ${index + 1 <= step
                                        ? 'text-white'
                                        : 'bg-gray-100 text-gray-400'
                                    }`}
                                style={{ backgroundColor: index + 1 <= step ? primaryColor : undefined }}
                            >
                                {index + 1 < step ? '✓' : index + 1}
                            </div>
                            {index < 3 && (
                                <div
                                    className={`w-16 sm:w-24 h-1 mx-2 rounded ${index + 1 < step ? '' : 'bg-gray-100'
                                        }`}
                                    style={{ backgroundColor: index + 1 < step ? primaryColor : undefined }}
                                />
                            )}
                        </div>
                    ))}
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                    <span>Goal Type</span>
                    <span>Target</span>
                    <span>Risk</span>
                    <span>Review</span>
                </div>
            </div>

            {/* Form Card */}
            <div className="bg-white rounded-2xl shadow-lg border overflow-hidden">
                <div className="p-6 border-b bg-gray-50">
                    <h1 className="text-2xl font-bold text-gray-900">
                        {step === 1 && 'What are you saving for?'}
                        {step === 2 && 'Set your target'}
                        {step === 3 && 'Choose your risk level'}
                        {step === 4 && 'Review your goal'}
                    </h1>
                    <p className="text-gray-500 mt-1">
                        {step === 1 && 'Select the type of goal you want to achieve'}
                        {step === 2 && 'Define your target amount and timeline'}
                        {step === 3 && 'Select how aggressive you want to invest'}
                        {step === 4 && 'Confirm your goal details'}
                    </p>
                </div>

                <div className="p-6">
                    {/* Step 1: Goal Type */}
                    {step === 1 && (
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                            {goalTypes.map((type) => (
                                <button
                                    key={type.value}
                                    onClick={() => updateForm('goal_type', type.value)}
                                    className={`p-4 rounded-xl border-2 text-left transition-all ${formData.goal_type === type.value
                                            ? 'border-current shadow-lg'
                                            : 'border-gray-100 hover:border-gray-200'
                                        }`}
                                    style={{
                                        borderColor: formData.goal_type === type.value ? primaryColor : undefined,
                                        backgroundColor: formData.goal_type === type.value ? `${primaryColor}05` : undefined
                                    }}
                                >
                                    <div className="text-3xl mb-2">{type.icon}</div>
                                    <div className="font-semibold text-gray-900">{type.label}</div>
                                    <div className="text-xs text-gray-500 mt-1">{type.description}</div>
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Step 2: Target & Timeline */}
                    {step === 2 && (
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Goal Name
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => updateForm('name', e.target.value)}
                                    placeholder="e.g., Retirement Fund"
                                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 focus:ring-current/20 outline-none transition-all"
                                    style={{ '--tw-ring-color': primaryColor } as React.CSSProperties}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Target Amount (USD)
                                </label>
                                <div className="relative">
                                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                                    <input
                                        type="number"
                                        value={formData.target_amount || ''}
                                        onChange={(e) => updateForm('target_amount', Number(e.target.value))}
                                        placeholder="500,000"
                                        className="w-full pl-8 pr-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 focus:ring-current/20 outline-none transition-all"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Target Date
                                </label>
                                <input
                                    type="date"
                                    value={formData.target_date}
                                    onChange={(e) => updateForm('target_date', e.target.value)}
                                    min={new Date().toISOString().split('T')[0]}
                                    className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 focus:ring-current/20 outline-none transition-all"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Monthly Contribution (USD)
                                </label>
                                <div className="relative">
                                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                                    <input
                                        type="number"
                                        value={formData.monthly_contribution || ''}
                                        onChange={(e) => updateForm('monthly_contribution', Number(e.target.value))}
                                        placeholder="2,000"
                                        className="w-full pl-8 pr-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 focus:ring-current/20 outline-none transition-all"
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Step 3: Risk Profile */}
                    {step === 3 && (
                        <div className="space-y-4">
                            {riskProfiles.map((profile) => (
                                <button
                                    key={profile.value}
                                    onClick={() => updateForm('risk_profile', profile.value)}
                                    className={`w-full p-5 rounded-xl border-2 text-left transition-all ${formData.risk_profile === profile.value
                                            ? 'shadow-lg'
                                            : 'border-gray-100 hover:border-gray-200'
                                        }`}
                                    style={{
                                        borderColor: formData.risk_profile === profile.value ? primaryColor : undefined,
                                        backgroundColor: formData.risk_profile === profile.value ? `${primaryColor}05` : undefined
                                    }}
                                >
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <div className="font-semibold text-gray-900 text-lg">{profile.label}</div>
                                            <div className="text-gray-500 mt-1">{profile.description}</div>
                                            <div className="text-sm text-gray-400 mt-2">{profile.allocation}</div>
                                        </div>
                                        <div
                                            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${formData.risk_profile === profile.value ? 'border-current' : 'border-gray-300'
                                                }`}
                                            style={{ borderColor: formData.risk_profile === profile.value ? primaryColor : undefined }}
                                        >
                                            {formData.risk_profile === profile.value && (
                                                <div
                                                    className="w-3 h-3 rounded-full"
                                                    style={{ backgroundColor: primaryColor }}
                                                />
                                            )}
                                        </div>
                                    </div>
                                </button>
                            ))}

                            {tenant.features.sharia_products && (
                                <label className="flex items-center gap-3 p-4 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors">
                                    <input
                                        type="checkbox"
                                        checked={formData.is_sharia_compliant}
                                        onChange={(e) => updateForm('is_sharia_compliant', e.target.checked)}
                                        className="w-5 h-5 rounded"
                                        style={{ accentColor: primaryColor }}
                                    />
                                    <div>
                                        <div className="font-medium text-gray-900">🕌 Sharia-Compliant Investments Only</div>
                                        <div className="text-sm text-gray-500">Invest according to Islamic principles</div>
                                    </div>
                                </label>
                            )}
                        </div>
                    )}

                    {/* Step 4: Review */}
                    {step === 4 && (
                        <div className="space-y-6">
                            <div className="bg-gray-50 rounded-xl p-6">
                                <h3 className="font-semibold text-gray-900 mb-4">Goal Summary</h3>
                                <dl className="space-y-3">
                                    <div className="flex justify-between">
                                        <dt className="text-gray-500">Goal Type</dt>
                                        <dd className="font-medium text-gray-900 capitalize">{formData.goal_type}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-500">Name</dt>
                                        <dd className="font-medium text-gray-900">{formData.name}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-500">Target Amount</dt>
                                        <dd className="font-medium text-gray-900">${formData.target_amount.toLocaleString()}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-500">Target Date</dt>
                                        <dd className="font-medium text-gray-900">{formData.target_date}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-500">Monthly Contribution</dt>
                                        <dd className="font-medium text-gray-900">${formData.monthly_contribution.toLocaleString()}</dd>
                                    </div>
                                    <div className="flex justify-between">
                                        <dt className="text-gray-500">Risk Profile</dt>
                                        <dd className="font-medium text-gray-900 capitalize">{formData.risk_profile}</dd>
                                    </div>
                                    {formData.is_sharia_compliant && (
                                        <div className="flex justify-between">
                                            <dt className="text-gray-500">Sharia Compliant</dt>
                                            <dd className="font-medium text-green-600">Yes ✓</dd>
                                        </div>
                                    )}
                                </dl>
                            </div>

                            <div
                                className="rounded-xl p-4 text-sm"
                                style={{ backgroundColor: `${primaryColor}10`, color: primaryColor }}
                            >
                                <p className="font-medium">📊 Projection</p>
                                <p className="mt-1 opacity-80">
                                    Based on your inputs and a moderate risk profile, you have an estimated
                                    <strong> 78% probability </strong> of reaching your goal.
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Navigation */}
                <div className="px-6 py-4 border-t bg-gray-50 flex justify-between">
                    <button
                        onClick={() => setStep(step - 1)}
                        disabled={step === 1}
                        className="px-6 py-2.5 rounded-xl border border-gray-200 font-medium text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white transition-colors"
                    >
                        Back
                    </button>

                    {step < 4 ? (
                        <button
                            onClick={() => setStep(step + 1)}
                            disabled={!canProceed(step)}
                            className="px-6 py-2.5 rounded-xl font-medium text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-90"
                            style={{ backgroundColor: primaryColor }}
                        >
                            Next
                        </button>
                    ) : (
                        <button
                            onClick={handleSubmit}
                            className="px-8 py-2.5 rounded-xl font-medium text-white transition-all hover:opacity-90 flex items-center gap-2"
                            style={{ backgroundColor: primaryColor }}
                        >
                            <span>✓</span>
                            Create Goal
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
