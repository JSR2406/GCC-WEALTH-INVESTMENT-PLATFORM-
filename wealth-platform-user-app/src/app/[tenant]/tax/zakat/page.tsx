'use client';

import { useState } from 'react';
import { useTenant } from '@/components/tenant/TenantProvider';

// Mock Zakat calculation data
const mockZakatData = {
    hijri_year: 1448,
    gregorian_year: 2026,
    nisab_gold_price: 2000, // per ounce
    nisab_threshold: 5460, // 85 grams * $64.24/gram
    assets: {
        cash_bank: 50000,
        gold_silver: 12000,
        investments: 200000,
        business_assets: 0,
        receivables: 5000,
        real_estate_rental: 0,
    },
    liabilities: {
        short_term_debts: 15000,
        loans: 0,
        credit_cards: 2000,
    }
};

export default function ZakatCalculatorPage() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const [assets, setAssets] = useState(mockZakatData.assets);
    const [liabilities, setLiabilities] = useState(mockZakatData.liabilities);

    // Calculate totals
    const totalAssets = Object.values(assets).reduce((sum, val) => sum + val, 0);
    const totalLiabilities = Object.values(liabilities).reduce((sum, val) => sum + val, 0);
    const netZakatableWealth = totalAssets - totalLiabilities;
    const nisabMet = netZakatableWealth >= mockZakatData.nisab_threshold;
    const zakatDue = nisabMet ? netZakatableWealth * 0.025 : 0;

    const updateAsset = (key: string, value: number) => {
        setAssets(prev => ({ ...prev, [key]: value }));
    };

    const updateLiability = (key: string, value: number) => {
        setLiabilities(prev => ({ ...prev, [key]: value }));
    };

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center">
                <div className="text-5xl mb-4">🕌</div>
                <h1 className="text-3xl font-bold text-gray-900">Zakat Calculator</h1>
                <p className="text-gray-500 mt-2">
                    Calculate your Zakat obligation for Hijri Year {mockZakatData.hijri_year}
                </p>
            </div>

            {/* Nisab Info */}
            <div
                className="rounded-xl p-4 text-center"
                style={{ backgroundColor: `${primaryColor}10` }}
            >
                <p className="text-sm" style={{ color: primaryColor }}>
                    <strong>Nisab Threshold:</strong> ${mockZakatData.nisab_threshold.toLocaleString()}
                    (based on 85 grams of gold at ${mockZakatData.nisab_gold_price}/oz)
                </p>
            </div>

            {/* Assets Section */}
            <div className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <span>💰</span> Zakatable Assets
                </h2>
                <div className="space-y-4">
                    <InputRow
                        label="Cash & Bank Balances"
                        value={assets.cash_bank}
                        onChange={(v) => updateAsset('cash_bank', v)}
                        placeholder="Enter amount"
                    />
                    <InputRow
                        label="Gold & Silver (market value)"
                        value={assets.gold_silver}
                        onChange={(v) => updateAsset('gold_silver', v)}
                        placeholder="Enter value"
                    />
                    <InputRow
                        label="Investments & Stocks"
                        value={assets.investments}
                        onChange={(v) => updateAsset('investments', v)}
                        placeholder="Enter value"
                        helperText="Only Shariah-compliant investments"
                    />
                    <InputRow
                        label="Business Assets & Inventory"
                        value={assets.business_assets}
                        onChange={(v) => updateAsset('business_assets', v)}
                        placeholder="Enter value"
                    />
                    <InputRow
                        label="Money Owed to You (Receivables)"
                        value={assets.receivables}
                        onChange={(v) => updateAsset('receivables', v)}
                        placeholder="Enter amount"
                    />
                    <InputRow
                        label="Rental Property Income"
                        value={assets.real_estate_rental}
                        onChange={(v) => updateAsset('real_estate_rental', v)}
                        placeholder="Enter amount"
                        helperText="Exclude primary residence"
                    />
                    <div className="pt-4 border-t flex justify-between items-center">
                        <span className="font-semibold text-gray-700">Total Assets</span>
                        <span className="text-xl font-bold text-gray-900">
                            ${totalAssets.toLocaleString()}
                        </span>
                    </div>
                </div>
            </div>

            {/* Liabilities Section */}
            <div className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <span>📉</span> Deductible Liabilities
                </h2>
                <div className="space-y-4">
                    <InputRow
                        label="Short-term Debts (due within 1 year)"
                        value={liabilities.short_term_debts}
                        onChange={(v) => updateLiability('short_term_debts', v)}
                        placeholder="Enter amount"
                    />
                    <InputRow
                        label="Loans & Mortgages (1 year's payment)"
                        value={liabilities.loans}
                        onChange={(v) => updateLiability('loans', v)}
                        placeholder="Enter amount"
                    />
                    <InputRow
                        label="Credit Card Balance"
                        value={liabilities.credit_cards}
                        onChange={(v) => updateLiability('credit_cards', v)}
                        placeholder="Enter amount"
                    />
                    <div className="pt-4 border-t flex justify-between items-center">
                        <span className="font-semibold text-gray-700">Total Liabilities</span>
                        <span className="text-xl font-bold text-gray-900">
                            ${totalLiabilities.toLocaleString()}
                        </span>
                    </div>
                </div>
            </div>

            {/* Calculation Result */}
            <div
                className="rounded-2xl p-8 text-white text-center"
                style={{
                    background: `linear-gradient(135deg, ${primaryColor} 0%, ${tenant.branding.secondary_color} 100%)`
                }}
            >
                <p className="text-white/70 text-sm uppercase tracking-wide">Net Zakatable Wealth</p>
                <p className="text-4xl font-bold mt-2">${netZakatableWealth.toLocaleString()}</p>

                <div className="mt-6 pt-6 border-t border-white/20">
                    {nisabMet ? (
                        <>
                            <p className="text-white/70 text-sm uppercase tracking-wide">Zakat Due (2.5%)</p>
                            <p className="text-5xl font-bold mt-2">${zakatDue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                            <p className="mt-4 text-white/60 text-sm">
                                Your wealth exceeds the Nisab threshold. Zakat is obligatory.
                            </p>
                        </>
                    ) : (
                        <>
                            <p className="text-2xl font-bold">Zakat Not Obligatory</p>
                            <p className="mt-2 text-white/60">
                                Your net zakatable wealth is below the Nisab threshold of ${mockZakatData.nisab_threshold.toLocaleString()}.
                                However, you may still give voluntary charity (Sadaqah).
                            </p>
                        </>
                    )}
                </div>
            </div>

            {/* Actions */}
            {nisabMet && (
                <div className="flex flex-col sm:flex-row gap-4">
                    <button
                        className="flex-1 px-6 py-4 rounded-xl text-white font-medium transition-all hover:opacity-90"
                        style={{ backgroundColor: primaryColor }}
                    >
                        📄 Download Zakat Certificate
                    </button>
                    <button
                        className="flex-1 px-6 py-4 rounded-xl border-2 font-medium transition-all hover:bg-gray-50"
                        style={{ borderColor: primaryColor, color: primaryColor }}
                    >
                        💳 Pay Zakat Online
                    </button>
                </div>
            )}

            {/* Information */}
            <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                <h3 className="font-semibold text-green-900 flex items-center gap-2">
                    <span>📚</span> About Zakat
                </h3>
                <ul className="mt-3 space-y-2 text-green-800 text-sm">
                    <li>• Zakat is 2.5% of wealth held for one lunar year above the Nisab threshold</li>
                    <li>• The Nisab is equivalent to 85 grams of gold or 595 grams of silver</li>
                    <li>• Personal items, primary residence, and debts are not zakatable</li>
                    <li>• Zakat purifies wealth and helps those in need</li>
                    <li>• For specific rulings, consult a qualified Islamic scholar</li>
                </ul>
            </div>
        </div>
    );
}

function InputRow({
    label,
    value,
    onChange,
    placeholder,
    helperText
}: {
    label: string;
    value: number;
    onChange: (v: number) => void;
    placeholder?: string;
    helperText?: string;
}) {
    return (
        <div>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                <label className="text-gray-700 flex-1">{label}</label>
                <div className="relative w-full sm:w-48">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
                    <input
                        type="number"
                        value={value || ''}
                        onChange={(e) => onChange(Number(e.target.value) || 0)}
                        placeholder={placeholder}
                        className="w-full pl-7 pr-3 py-2 rounded-lg border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-500/20 outline-none transition-all text-right"
                    />
                </div>
            </div>
            {helperText && (
                <p className="text-xs text-gray-400 mt-1 sm:text-right">{helperText}</p>
            )}
        </div>
    );
}
