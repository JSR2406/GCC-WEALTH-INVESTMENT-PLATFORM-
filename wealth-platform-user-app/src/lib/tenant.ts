/**
 * Tenant Resolution & Configuration
 * ==================================
 * 
 * Resolves bank tenant from URL/subdomain and fetches branding config.
 */

import { notFound } from 'next/navigation';

export interface BankBranding {
  logo_url: string;
  primary_color: string;
  secondary_color: string;
  font_family: string;
  app_name: string;
}

export interface BankFeatures {
  sharia_products: boolean;
  zakat_calculator: boolean;
  estate_planning: boolean;
  goal_based_investing: boolean;
}

export interface BankConfig {
  id: string;
  slug: string;
  name: string;
  country: 'AE' | 'SA';
  branding: BankBranding;
  features: BankFeatures;
  api_base_url: string;
}

// Mock bank configurations for demo
const MOCK_BANKS: Record<string, BankConfig> = {
  'fab': {
    id: 'bank-fab-001',
    slug: 'fab',
    name: 'First Abu Dhabi Bank',
    country: 'AE',
    branding: {
      logo_url: '/tenant-assets/fab/logo.svg',
      primary_color: '#00A651',
      secondary_color: '#003366',
      font_family: 'Inter, sans-serif',
      app_name: 'FAB Wealth'
    },
    features: {
      sharia_products: true,
      zakat_calculator: true,
      estate_planning: true,
      goal_based_investing: true
    },
    api_base_url: 'http://localhost:8000/api/v1'
  },
  'hsbc': {
    id: 'bank-hsbc-002',
    slug: 'hsbc',
    name: 'HSBC Middle East',
    country: 'AE',
    branding: {
      logo_url: '/tenant-assets/hsbc/logo.svg',
      primary_color: '#DB0011',
      secondary_color: '#000000',
      font_family: 'Univers, Arial, sans-serif',
      app_name: 'HSBC Wealth Manager'
    },
    features: {
      sharia_products: false,
      zakat_calculator: false,
      estate_planning: true,
      goal_based_investing: true
    },
    api_base_url: 'http://localhost:8000/api/v1'
  },
  'rajhi': {
    id: 'bank-rajhi-003',
    slug: 'rajhi',
    name: 'Al Rajhi Bank',
    country: 'SA',
    branding: {
      logo_url: '/tenant-assets/rajhi/logo.svg',
      primary_color: '#004B87',
      secondary_color: '#F7941D',
      font_family: 'Tahoma, sans-serif',
      app_name: 'الراجحي للثروات'
    },
    features: {
      sharia_products: true,
      zakat_calculator: true,
      estate_planning: true,
      goal_based_investing: true
    },
    api_base_url: 'http://localhost:8000/api/v1'
  }
};

/**
 * Resolve tenant from URL/subdomain
 * 
 * Supports:
 * - Subdomain: fab.wealthplatform.com → 'fab'
 * - Path: wealthplatform.com/fab → 'fab'
 * - Custom domain: fabwealth.ae → 'fab' (via DB lookup)
 */
export async function resolveTenant(
  hostname: string,
  pathname: string
): Promise<BankConfig> {
  let tenantSlug: string | null = null;

  // Strategy 1: Subdomain extraction
  if (hostname.includes('.') && !hostname.includes('localhost') && !hostname.includes('vercel.app')) {
    const parts = hostname.split('.');
    if (parts.length > 2) {
      const candidateSlug = parts[0];
      // Only accept if it matches a known mock bank (or valid pattern)
      if (MOCK_BANKS[candidateSlug]) {
        tenantSlug = candidateSlug;
      }
    }
  }

  // Strategy 2: Path extraction (fallback or explicit path)
  if (!tenantSlug && pathname.startsWith('/')) {
    const pathParts = pathname.split('/').filter(Boolean);
    if (pathParts.length > 0 && MOCK_BANKS[pathParts[0]]) {
      tenantSlug = pathParts[0];
    }
  }

  // Strategy 3: API lookup for custom domains
  if (!tenantSlug && process.env.NEXT_PUBLIC_API_URL && !hostname.includes('vercel.app')) {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/tenants/resolve?domain=${hostname}`,
        { cache: 'force-cache', next: { revalidate: 3600 } }
      );

      if (response.ok) {
        const data = await response.json();
        tenantSlug = data.slug;
      }
    } catch {
      // Fallback to mock data
    }
  }

  // Return mock config or fetch from API
  if (tenantSlug && MOCK_BANKS[tenantSlug]) {
    return MOCK_BANKS[tenantSlug];
  }

  // Try fetching from API
  if (tenantSlug && process.env.NEXT_PUBLIC_API_URL) {
    try {
      const configResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/banks/slug/${tenantSlug}/config`,
        { cache: 'force-cache', next: { revalidate: 600 } }
      );

      if (configResponse.ok) {
        return await configResponse.json();
      }
    } catch {
      // notFound will be called below
    }
  }

  notFound();
}

/**
 * Get all available tenant slugs (for static generation)
 */
export function getAllTenantSlugs(): string[] {
  return Object.keys(MOCK_BANKS);
}

/**
 * Get tenant config by slug (synchronous, for client components)
 */
export function getTenantBySlug(slug: string): BankConfig | null {
  return MOCK_BANKS[slug] || null;
}
