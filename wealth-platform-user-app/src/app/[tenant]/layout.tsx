import { headers } from 'next/headers';
import { resolveTenant } from '@/lib/tenant';
import { TenantProvider } from '@/components/tenant/TenantProvider';
import TenantClientWrapper from '@/components/layout/TenantClientWrapper';
import { notFound } from 'next/navigation';

export default async function TenantLayout({
    children,
    params
}: {
    children: React.ReactNode;
    params: Promise<{ tenant: string }>;
}) {
    const { tenant } = await params;
    const headersList = await headers();
    const hostname = headersList.get('host') || 'localhost:3000';
    const pathname = `/${tenant}`;

    let config;
    try {
        config = await resolveTenant(hostname, pathname);
    } catch {
        notFound();
    }

    // Validate tenant slug matches URL
    if (tenant && tenant !== config.slug) {
        notFound();
    }

    const navLinks = [
        { href: `/${config.slug}`, label: 'Dashboard', icon: '📊' },
        { href: `/${config.slug}/portfolio/accounts`, label: 'Accounts', icon: '💰' },
        { href: `/${config.slug}/goals`, label: 'Goals', icon: '🎯' },
        { href: `/${config.slug}/tax`, label: 'Tax', icon: '📋' },
    ];

    // Serialize config for client component
    const serializedConfig = {
        slug: config.slug,
        name: config.name,
        branding: {
            primary_color: config.branding.primary_color,
            secondary_color: config.branding.secondary_color,
            app_name: config.branding.app_name,
        },
    };

    return (
        <TenantProvider config={config}>
            <TenantClientWrapper
                config={serializedConfig}
                navLinks={navLinks}
            >
                {children}
            </TenantClientWrapper>
        </TenantProvider>
    );
}
