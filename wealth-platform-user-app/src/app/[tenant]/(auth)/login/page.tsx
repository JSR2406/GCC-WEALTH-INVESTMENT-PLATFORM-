'use client';

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth/AuthContext';

// Demo credentials per bank
const DEMO_CREDENTIALS: Record<string, { email: string; password: string }> = {
    fab: { email: 'demo@fab.ae', password: 'demo123' },
    hsbc: { email: 'john@example.com', password: 'demo123' },
    rajhi: { email: 'mohammed@example.com', password: 'demo123' },
};

export default function LoginPage() {
    const router = useRouter();
    const params = useParams();
    const tenant = params.tenant as string;
    const { login, isAuthenticated } = useAuth();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    // If already authenticated, redirect to dashboard
    if (isAuthenticated) {
        router.push(`/${tenant}`);
        return null;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const result = await login(email, password, tenant);

            if (result.success) {
                router.push(`/${tenant}`);
            } else {
                setError(result.error || 'Login failed');
            }
        } catch (err) {
            setError('An unexpected error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    const fillDemoCredentials = () => {
        const demo = DEMO_CREDENTIALS[tenant] || DEMO_CREDENTIALS.fab;
        setEmail(demo.email);
        setPassword(demo.password);
        setError('');
    };

    const handleGoogleLogin = async () => {
        setIsLoading(true);
        setError('');

        // Simulating Google OAuth with demo credentials
        try {
            // Find demo credentials for current tenant
            const demo = DEMO_CREDENTIALS[tenant] || DEMO_CREDENTIALS.fab;

            // Artificial delay to simulate OAuth popup/network
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Perform login with demo account
            const result = await login(demo.email, demo.password, tenant);

            if (result.success) {
                router.push(`/${tenant}`);
            } else {
                setError(result.error || 'Google login failed');
            }
        } catch (err) {
            setError('Google login validation failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            {/* Animated background elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div
                    className="absolute -top-40 -right-40 w-80 h-80 rounded-full blur-3xl opacity-20"
                    style={{ background: 'var(--color-primary, #00A651)' }}
                />
                <div
                    className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full blur-3xl opacity-20"
                    style={{ background: 'var(--color-secondary, #003366)' }}
                />
            </div>

            <div className="w-full max-w-md relative z-10">
                {/* Logo and Header */}
                <div className="text-center mb-8">
                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 text-white/60 hover:text-white mb-6 transition-colors"
                    >
                        <span>←</span>
                        <span>Back to Home</span>
                    </Link>

                    <div
                        className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center text-3xl shadow-lg"
                        style={{ background: 'linear-gradient(135deg, var(--color-primary, #00A651), var(--color-secondary, #003366))' }}
                    >
                        {tenant === 'fab' && '🏦'}
                        {tenant === 'hsbc' && '🔴'}
                        {tenant === 'rajhi' && '🕌'}
                        {!['fab', 'hsbc', 'rajhi'].includes(tenant) && '💰'}
                    </div>

                    <h1 className="text-2xl font-bold text-white mb-2">
                        Welcome Back
                    </h1>
                    <p className="text-gray-400">
                        Sign in to access your wealth dashboard
                    </p>
                </div>

                {/* Login Form */}
                <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20">
                    {/* Demo Credentials Banner */}
                    <button
                        type="button"
                        onClick={fillDemoCredentials}
                        className="w-full mb-6 p-3 rounded-lg bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 text-yellow-200 text-sm hover:from-yellow-500/30 hover:to-orange-500/30 transition-all"
                    >
                        🎯 Click here to fill demo credentials
                    </button>

                    {error && (
                        <div className="mb-4 p-4 rounded-lg bg-red-500/20 border border-red-500/30 text-red-200 text-sm">
                            ⚠️ {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        {/* Email Input */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Email Address
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@example.com"
                                required
                                className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                            />
                        </div>

                        {/* Password Input */}
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    minLength={6}
                                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all pr-12"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                                >
                                    {showPassword ? '🙈' : '👁️'}
                                </button>
                            </div>
                        </div>

                        {/* Remember Me & Forgot Password */}
                        <div className="flex items-center justify-between text-sm">
                            <label className="flex items-center gap-2 text-gray-400 cursor-pointer">
                                <input
                                    type="checkbox"
                                    className="w-4 h-4 rounded border-gray-600 bg-white/5 text-primary focus:ring-primary"
                                />
                                Remember me
                            </label>
                            <Link
                                href={`/${tenant}/forgot-password`}
                                className="text-primary hover:underline"
                                style={{ color: 'var(--color-primary, #00A651)' }}
                            >
                                Forgot password?
                            </Link>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-4 rounded-lg font-semibold text-white transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
                            style={{
                                background: 'linear-gradient(135deg, var(--color-primary, #00A651), var(--color-secondary, #003366))',
                            }}
                        >
                            {isLoading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Signing in...
                                </>
                            ) : (
                                <>
                                    Sign In
                                    <span>→</span>
                                </>
                            )}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="my-6 flex items-center">
                        <div className="flex-1 border-t border-white/10"></div>
                        <span className="px-4 text-sm text-gray-500">or continue with</span>
                        <div className="flex-1 border-t border-white/10"></div>
                    </div>

                    {/* Social Login */}
                    <div className="space-y-3">
                        <button
                            type="button"
                            onClick={() => handleGoogleLogin()}
                            className="w-full flex items-center justify-center gap-2 py-3 rounded-lg bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24">
                                <path
                                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                    fill="#4285F4"
                                />
                                <path
                                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                    fill="#34A853"
                                />
                                <path
                                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                    fill="#FBBC05"
                                />
                                <path
                                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                    fill="#EA4335"
                                />
                            </svg>
                            Continue with Google
                        </button>

                        <div className="grid grid-cols-2 gap-3">
                            <button className="flex items-center justify-center gap-2 py-3 rounded-lg bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-colors text-sm">
                                <span>🔐</span>
                                Emirates ID
                            </button>
                            <button className="flex items-center justify-center gap-2 py-3 rounded-lg bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-colors text-sm">
                                <span>📱</span>
                                UAE Pass
                            </button>
                        </div>
                    </div>
                </div>

                {/* Register Link */}
                <p className="text-center mt-6 text-gray-400">
                    Don't have an account?{' '}
                    <Link
                        href={`/${tenant}/register`}
                        className="font-medium hover:underline"
                        style={{ color: 'var(--color-primary, #00A651)' }}
                    >
                        Create account
                    </Link>
                </p>

                {/* Security Badge */}
                <div className="flex items-center justify-center gap-2 mt-8 text-gray-500 text-sm">
                    <span>🔒</span>
                    <span>Bank-grade encryption • 256-bit SSL</span>
                </div>
            </div>
        </div>
    );
}
