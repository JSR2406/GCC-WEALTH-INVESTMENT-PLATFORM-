'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// Types
interface User {
    id: string;
    email: string;
    full_name: string;
    bank_id: string;
    bank_slug: string;
    kyc_status: string;
    subscription_tier: string;
    is_active: boolean;
}

interface AuthTokens {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
}

interface AuthContextType {
    user: User | null;
    tokens: AuthTokens | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string, bankSlug: string) => Promise<{ success: boolean; error?: string }>;
    logout: () => void;
    refreshToken: () => Promise<boolean>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const STORAGE_KEYS = {
    USER: 'gcc_wealth_user',
    TOKENS: 'gcc_wealth_tokens',
};

// API base URL - empty for relative URLs in production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// Auth Provider Component
export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [tokens, setTokens] = useState<AuthTokens | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Initialize auth state from storage
    useEffect(() => {
        const initAuth = () => {
            try {
                const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
                const storedTokens = localStorage.getItem(STORAGE_KEYS.TOKENS);

                if (storedUser && storedTokens) {
                    setUser(JSON.parse(storedUser));
                    setTokens(JSON.parse(storedTokens));
                }
            } catch (error) {
                console.error('Failed to restore auth state:', error);
                // Clear corrupted data
                localStorage.removeItem(STORAGE_KEYS.USER);
                localStorage.removeItem(STORAGE_KEYS.TOKENS);
            } finally {
                setIsLoading(false);
            }
        };

        initAuth();
    }, []);

    // Login function
    const login = useCallback(async (
        email: string,
        password: string,
        bankSlug: string
    ): Promise<{ success: boolean; error?: string }> => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password,
                    bank_slug: bankSlug,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                return {
                    success: false,
                    error: data.detail?.message || 'Login failed',
                };
            }

            // Store auth data
            const userData = data.user;
            const tokenData = data.tokens;

            setUser(userData);
            setTokens(tokenData);

            localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(userData));
            localStorage.setItem(STORAGE_KEYS.TOKENS, JSON.stringify(tokenData));

            return { success: true };
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: 'Network error. Please check your connection.',
            };
        }
    }, []);

    // Logout function
    const logout = useCallback(() => {
        setUser(null);
        setTokens(null);
        localStorage.removeItem(STORAGE_KEYS.USER);
        localStorage.removeItem(STORAGE_KEYS.TOKENS);

        // Optional: Call logout endpoint
        fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
            method: 'POST',
            headers: tokens ? {
                'Authorization': `Bearer ${tokens.access_token}`,
            } : {},
        }).catch(() => { }); // Ignore errors
    }, [tokens]);

    // Refresh token function
    const refreshToken = useCallback(async (): Promise<boolean> => {
        if (!tokens?.refresh_token) {
            return false;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh_token: tokens.refresh_token,
                }),
            });

            if (!response.ok) {
                logout();
                return false;
            }

            const newTokens = await response.json();
            setTokens(newTokens);
            localStorage.setItem(STORAGE_KEYS.TOKENS, JSON.stringify(newTokens));

            return true;
        } catch (error) {
            console.error('Token refresh error:', error);
            logout();
            return false;
        }
    }, [tokens, logout]);

    const value: AuthContextType = {
        user,
        tokens,
        isAuthenticated: !!user && !!tokens,
        isLoading,
        login,
        logout,
        refreshToken,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

// Hook to use auth context
export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

// Protected route wrapper component
export function RequireAuth({
    children,
    fallback
}: {
    children: React.ReactNode;
    fallback?: React.ReactNode;
}) {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                    <p className="text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return fallback || null;
    }

    return <>{children}</>;
}

// Authenticated fetch helper
export async function authFetch(
    url: string,
    options: RequestInit = {},
    tokens: AuthTokens | null
): Promise<Response> {
    const headers: HeadersInit = {
        ...options.headers,
    };

    if (tokens?.access_token) {
        (headers as Record<string, string>)['Authorization'] = `Bearer ${tokens.access_token}`;
    }

    return fetch(url, {
        ...options,
        headers,
    });
}
