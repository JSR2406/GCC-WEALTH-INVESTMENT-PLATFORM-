'use client';

import { createContext, useContext, useEffect, ReactNode } from 'react';
import type { BankConfig } from '@/lib/tenant';

const TenantContext = createContext<BankConfig | null>(null);

interface TenantProviderProps {
    config: BankConfig;
    children: ReactNode;
}

export function TenantProvider({ config, children }: TenantProviderProps) {
    useEffect(() => {
        // Apply dynamic CSS variables
        const root = document.documentElement;
        root.style.setProperty('--primary-color', config.branding.primary_color);
        root.style.setProperty('--secondary-color', config.branding.secondary_color);
        root.style.setProperty('--font-family', config.branding.font_family);

        // Update meta tags
        document.title = config.branding.app_name;

        // Update favicon
        const favicon = document.querySelector('link[rel="icon"]') as HTMLLinkElement;
        if (favicon) {
            favicon.href = `/tenant-assets/${config.slug}/icon.png`;
        }

        // Apply RTL for Arabic (Saudi Arabia)
        if (config.country === 'SA') {
            document.documentElement.dir = 'rtl';
            document.documentElement.lang = 'ar';
        } else {
            document.documentElement.dir = 'ltr';
            document.documentElement.lang = 'en';
        }

        // Apply theme colors to meta theme-color
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        if (metaTheme) {
            metaTheme.setAttribute('content', config.branding.primary_color);
        }
    }, [config]);

    return (
        <TenantContext.Provider value={config}>
            <div
                className="min-h-screen"
                style={{
                    fontFamily: config.branding.font_family,
                    '--tw-primary': config.branding.primary_color,
                    '--tw-secondary': config.branding.secondary_color
                } as React.CSSProperties}
            >
                {children}
            </div>
        </TenantContext.Provider>
    );
}

export function useTenant(): BankConfig {
    const context = useContext(TenantContext);
    if (!context) {
        throw new Error('useTenant must be used within TenantProvider');
    }
    return context;
}

export function useTenantOptional(): BankConfig | null {
    return useContext(TenantContext);
}
