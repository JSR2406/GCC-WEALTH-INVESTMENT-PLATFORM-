'use client';

import { useState } from 'react';
import { useTenant } from '@/components/tenant/TenantProvider';

export default function SettingsPage() {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const [profile, setProfile] = useState({
        full_name: 'Ahmed Al-Zahrani',
        email: 'ahmed.zahrani@email.com',
        phone: '+971 50 123 4567',
        nationality: 'SA',
        residency_country: 'AE',
        preferred_language: tenant.country === 'SA' ? 'ar' : 'en'
    });

    const [notifications, setNotifications] = useState({
        portfolio_updates: true,
        goal_milestones: true,
        tax_reminders: true,
        marketing: false
    });

    const [security, setSecurity] = useState({
        two_factor: true,
        biometric: false
    });

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
                <p className="text-gray-500 mt-1">Manage your account preferences</p>
            </div>

            {/* Profile Section */}
            <section className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                    <span>👤</span> Profile Information
                </h2>
                <div className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                            <input
                                type="text"
                                value={profile.full_name}
                                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 outline-none transition-all"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                            <input
                                type="email"
                                value={profile.email}
                                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 outline-none transition-all"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                        <input
                            type="tel"
                            value={profile.phone}
                            onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current focus:ring-2 outline-none transition-all"
                        />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Nationality</label>
                            <select
                                value={profile.nationality}
                                onChange={(e) => setProfile({ ...profile, nationality: e.target.value })}
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                            >
                                <option value="AE">United Arab Emirates</option>
                                <option value="SA">Saudi Arabia</option>
                                <option value="US">United States</option>
                                <option value="GB">United Kingdom</option>
                                <option value="IN">India</option>
                                <option value="PK">Pakistan</option>
                                <option value="EG">Egypt</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Country of Residence</label>
                            <select
                                value={profile.residency_country}
                                onChange={(e) => setProfile({ ...profile, residency_country: e.target.value })}
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                            >
                                <option value="AE">United Arab Emirates</option>
                                <option value="SA">Saudi Arabia</option>
                                <option value="BH">Bahrain</option>
                                <option value="KW">Kuwait</option>
                                <option value="QA">Qatar</option>
                                <option value="OM">Oman</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div className="mt-6 flex justify-end">
                    <button
                        className="px-6 py-2.5 rounded-xl text-white font-medium transition-all hover:opacity-90"
                        style={{ backgroundColor: primaryColor }}
                    >
                        Save Changes
                    </button>
                </div>
            </section>

            {/* Language & Display */}
            <section className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                    <span>🌐</span> Language & Display
                </h2>
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Preferred Language</label>
                        <select
                            value={profile.preferred_language}
                            onChange={(e) => setProfile({ ...profile, preferred_language: e.target.value })}
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-current outline-none"
                        >
                            <option value="en">English</option>
                            <option value="ar">العربية (Arabic)</option>
                        </select>
                    </div>
                    <p className="text-sm text-gray-500">
                        {profile.preferred_language === 'ar'
                            ? 'The interface will be displayed right-to-left with Arabic text.'
                            : 'The interface will be displayed left-to-right with English text.'}
                    </p>
                </div>
            </section>

            {/* Notifications */}
            <section className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                    <span>🔔</span> Notifications
                </h2>
                <div className="space-y-4">
                    {[
                        { key: 'portfolio_updates', label: 'Portfolio Updates', description: 'Get notified about significant changes to your portfolio' },
                        { key: 'goal_milestones', label: 'Goal Milestones', description: 'Celebrate when you reach goal milestones' },
                        { key: 'tax_reminders', label: 'Tax Reminders', description: 'Receive reminders about tax deadlines' },
                        { key: 'marketing', label: 'Marketing Communications', description: 'Receive news and offers from the bank' }
                    ].map((item) => (
                        <label
                            key={item.key}
                            className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors"
                        >
                            <div>
                                <p className="font-medium text-gray-900">{item.label}</p>
                                <p className="text-sm text-gray-500">{item.description}</p>
                            </div>
                            <div className="relative">
                                <input
                                    type="checkbox"
                                    checked={notifications[item.key as keyof typeof notifications]}
                                    onChange={(e) => setNotifications({ ...notifications, [item.key]: e.target.checked })}
                                    className="sr-only peer"
                                />
                                <div
                                    className="w-11 h-6 rounded-full peer-checked:bg-current bg-gray-200 transition-colors"
                                    style={{ backgroundColor: notifications[item.key as keyof typeof notifications] ? primaryColor : undefined }}
                                />
                                <div className="absolute left-0.5 top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
                            </div>
                        </label>
                    ))}
                </div>
            </section>

            {/* Security */}
            <section className="bg-white rounded-2xl shadow-sm border p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                    <span>🔐</span> Security
                </h2>
                <div className="space-y-4">
                    <label className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
                        <div>
                            <p className="font-medium text-gray-900">Two-Factor Authentication</p>
                            <p className="text-sm text-gray-500">Add an extra layer of security</p>
                        </div>
                        <div className="relative">
                            <input
                                type="checkbox"
                                checked={security.two_factor}
                                onChange={(e) => setSecurity({ ...security, two_factor: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div
                                className="w-11 h-6 rounded-full peer-checked:bg-current bg-gray-200 transition-colors"
                                style={{ backgroundColor: security.two_factor ? primaryColor : undefined }}
                            />
                            <div className="absolute left-0.5 top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
                        </div>
                    </label>

                    <label className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
                        <div>
                            <p className="font-medium text-gray-900">Biometric Login</p>
                            <p className="text-sm text-gray-500">Use fingerprint or face recognition</p>
                        </div>
                        <div className="relative">
                            <input
                                type="checkbox"
                                checked={security.biometric}
                                onChange={(e) => setSecurity({ ...security, biometric: e.target.checked })}
                                className="sr-only peer"
                            />
                            <div
                                className="w-11 h-6 rounded-full peer-checked:bg-current bg-gray-200 transition-colors"
                                style={{ backgroundColor: security.biometric ? primaryColor : undefined }}
                            />
                            <div className="absolute left-0.5 top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform peer-checked:translate-x-5" />
                        </div>
                    </label>

                    <div className="pt-4 border-t">
                        <button className="text-red-600 font-medium hover:underline">
                            Change Password
                        </button>
                    </div>
                </div>
            </section>

            {/* Danger Zone */}
            <section className="bg-red-50 rounded-2xl border border-red-200 p-6">
                <h2 className="text-lg font-semibold text-red-900 mb-2">Danger Zone</h2>
                <p className="text-red-700 text-sm mb-4">
                    Once you delete your account, there is no going back. Please be certain.
                </p>
                <button className="px-4 py-2 rounded-xl bg-red-600 text-white font-medium hover:bg-red-700 transition-colors">
                    Delete Account
                </button>
            </section>
        </div>
    );
}
