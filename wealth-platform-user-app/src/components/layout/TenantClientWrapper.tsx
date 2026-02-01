'use client';

import { AuthProvider, useAuth } from '@/lib/auth/AuthContext';
import Link from 'next/link';

interface TenantClientWrapperProps {
    children: React.ReactNode;
    config: {
        slug: string;
        name: string;
        branding: {
            primary_color: string;
            secondary_color: string;
            app_name: string;
        };
    };
    navLinks: Array<{ href: string; label: string; icon: string }>;
}

function UserMenuContent({ config }: { config: TenantClientWrapperProps['config'] }) {
    const { user, isAuthenticated, logout } = useAuth();

    if (!isAuthenticated) {
        return (
            <Link
                href={`/${config.slug}/login`}
                className="px-4 py-2 rounded-lg font-medium text-white transition-colors"
                style={{ backgroundColor: config.branding.primary_color }}
            >
                Sign In
            </Link>
        );
    }

    return (
        <div className="flex items-center gap-3">
            <button className="p-2 hover:bg-gray-100 rounded-full relative">
                <span className="sr-only">Notifications</span>
                🔔
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            <div className="relative group">
                <button className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg">
                    <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm"
                        style={{ backgroundColor: config.branding.primary_color }}
                    >
                        {user?.full_name?.charAt(0) || 'U'}
                    </div>
                    <span className="hidden sm:block text-sm font-medium text-gray-700 max-w-24 truncate">
                        {user?.full_name || 'User'}
                    </span>
                    <span className="text-gray-400">▼</span>
                </button>

                {/* Dropdown Menu */}
                <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-lg border opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                    <div className="p-4 border-b">
                        <p className="font-medium text-gray-900">{user?.full_name}</p>
                        <p className="text-sm text-gray-500 truncate">{user?.email}</p>
                        <span
                            className="inline-block mt-2 px-2 py-0.5 rounded text-xs font-medium capitalize"
                            style={{
                                backgroundColor: `${config.branding.primary_color}20`,
                                color: config.branding.primary_color
                            }}
                        >
                            {user?.subscription_tier} Plan
                        </span>
                    </div>

                    <div className="py-2">
                        <Link
                            href={`/${config.slug}/settings`}
                            className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-50"
                        >
                            <span>⚙️</span>
                            Settings
                        </Link>
                        <Link
                            href={`/${config.slug}/documents`}
                            className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-50"
                        >
                            <span>📄</span>
                            Documents
                        </Link>
                        <Link
                            href={`/${config.slug}/support`}
                            className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-50"
                        >
                            <span>❓</span>
                            Help & Support
                        </Link>
                    </div>

                    <div className="py-2 border-t">
                        <button
                            onClick={logout}
                            className="flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 w-full text-left"
                        >
                            <span>🚪</span>
                            Sign Out
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function TenantClientWrapper({
    children,
    config,
    navLinks
}: TenantClientWrapperProps) {
    return (
        <AuthProvider>
            <div className="min-h-screen bg-gray-50">
                {/* Top Navigation */}
                <header
                    className="sticky top-0 z-50 bg-white shadow-sm border-b"
                    style={{ borderColor: `${config.branding.primary_color}20` }}
                >
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex justify-between items-center h-16">
                            {/* Logo & App Name */}
                            <Link href={`/${config.slug}`} className="flex items-center gap-3">
                                <div
                                    className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-lg"
                                    style={{ backgroundColor: config.branding.primary_color }}
                                >
                                    {config.name.charAt(0)}
                                </div>
                                <span
                                    className="text-xl font-semibold hidden sm:block"
                                    style={{ color: config.branding.secondary_color }}
                                >
                                    {config.branding.app_name}
                                </span>
                            </Link>

                            {/* Desktop Navigation */}
                            <nav className="hidden md:flex items-center gap-1">
                                {navLinks.map((link) => (
                                    <Link
                                        key={link.href}
                                        href={link.href}
                                        className="px-4 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors flex items-center gap-2"
                                    >
                                        <span>{link.icon}</span>
                                        <span>{link.label}</span>
                                    </Link>
                                ))}
                            </nav>

                            {/* User Menu */}
                            <UserMenuContent config={config} />
                        </div>
                    </div>
                </header>

                {/* Main Content */}
                <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    {children}
                </main>

                {/* Mobile Bottom Navigation */}
                <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t shadow-lg">
                    <div className="flex justify-around items-center h-16">
                        <Link
                            href={`/${config.slug}`}
                            className="flex flex-col items-center py-2 px-3 text-gray-600"
                        >
                            <span className="text-xl">🏠</span>
                            <span className="text-xs">Home</span>
                        </Link>
                        {navLinks.slice(0, 3).map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className="flex flex-col items-center py-2 px-3 text-gray-600"
                            >
                                <span className="text-xl">{link.icon}</span>
                                <span className="text-xs">{link.label}</span>
                            </Link>
                        ))}
                        <Link
                            href={`/${config.slug}/settings`}
                            className="flex flex-col items-center py-2 px-3 text-gray-600"
                        >
                            <span className="text-xl">⚙️</span>
                            <span className="text-xs">More</span>
                        </Link>
                    </div>
                </nav>

                {/* Footer */}
                <footer className="bg-white border-t mt-16 pb-20 md:pb-0">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                            <div className="flex items-center gap-2 text-gray-500 text-sm">
                                <span>Powered by</span>
                                <span className="font-semibold text-gray-700">GCC Wealth Platform</span>
                            </div>
                            <div className="flex gap-6 text-sm text-gray-500">
                                <Link href={`/${config.slug}/privacy`} className="hover:text-gray-700">
                                    Privacy Policy
                                </Link>
                                <Link href={`/${config.slug}/terms`} className="hover:text-gray-700">
                                    Terms of Service
                                </Link>
                                <Link href={`/${config.slug}/support`} className="hover:text-gray-700">
                                    Support
                                </Link>
                            </div>
                        </div>
                    </div>
                </footer>
            </div>
        </AuthProvider>
    );
}
