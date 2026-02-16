/**
 * API Client
 * ==========
 * 
 * Centralized API client with authentication, caching, and error handling.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const IS_DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true' || typeof window !== 'undefined' && window.location.hostname.includes('vercel.app');

interface ApiError {
    code: string;
    message: string;
    details?: Record<string, string[]>;
}

export class ApiClientError extends Error {
    constructor(
        public statusCode: number,
        public error: ApiError
    ) {
        super(error.message);
        this.name = 'ApiClientError';
    }
}

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface RequestOptions {
    method?: HttpMethod;
    body?: unknown;
    headers?: Record<string, string>;
    cache?: RequestCache;
    revalidate?: number;
}

class ApiClient {
    private baseUrl: string;
    private token: string | null = null;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    setToken(token: string | null) {
        this.token = token;
        if (token && typeof window !== 'undefined') {
            localStorage.setItem('auth_token', token);
        } else if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
        }
    }

    getToken(): string | null {
        if (this.token) return this.token;
        if (typeof window !== 'undefined') {
            return localStorage.getItem('auth_token');
        }
        return null;
    }

    private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
        const { method = 'GET', body, headers = {}, cache, revalidate } = options;

        const token = this.getToken();
        const requestHeaders: Record<string, string> = {
            'Content-Type': 'application/json',
            ...headers,
        };

        if (token) {
            requestHeaders['Authorization'] = `Bearer ${token}`;
        }

        const fetchOptions: RequestInit = {
            method,
            headers: requestHeaders,
        };

        if (body) {
            fetchOptions.body = JSON.stringify(body);
        }

        if (cache) {
            (fetchOptions as Record<string, unknown>).cache = cache;
        }

        if (revalidate !== undefined) {
            (fetchOptions as Record<string, unknown>).next = { revalidate };
        }

        let response: Response;
        try {
            response = await fetch(`${this.baseUrl}${endpoint}`, fetchOptions);
        } catch (err) {
            // Fallback for Demo Mode if API is unreachable
            if (IS_DEMO_MODE) {
                console.warn('API Unreachable, falling back to mock data for demo:', endpoint);
                return this.getMockData(endpoint, options) as unknown as T;
            }
            throw err;
        }

        if (!response.ok) {
            let error: ApiError;
            try {
                const errorData = await response.json();
                error = errorData.error || { code: 'UNKNOWN', message: response.statusText };
            } catch {
                error = { code: 'UNKNOWN', message: response.statusText };
            }
            throw new ApiClientError(response.status, error);
        }

        if (response.status === 204) {
            return {} as T;
        }

        return response.json();
    }

    // Auth endpoints
    async login(email: string, password: string, bankSlug: string) {
        const response = await this.request<{ access_token: string; refresh_token: string }>(
            '/auth/login',
            {
                method: 'POST',
                body: { email, password, bank_slug: bankSlug }
            }
        );
        this.setToken(response.access_token);
        return response;
    }

    async logout() {
        await this.request('/auth/logout', { method: 'POST' });
        this.setToken(null);
    }

    async refreshToken() {
        const response = await this.request<{ access_token: string }>('/auth/refresh', {
            method: 'POST'
        });
        this.setToken(response.access_token);
        return response;
    }

    // User endpoints
    async getCurrentUser() {
        return this.request<UserProfile>('/users/me');
    }

    async updateProfile(data: Partial<UserProfile>) {
        return this.request<UserProfile>('/users/me', {
            method: 'PATCH',
            body: data
        });
    }

    // Portfolio endpoints
    async getPortfolio() {
        return this.request<Portfolio>('/portfolios/summary');
    }

    async getAccounts() {
        return this.request<Account[]>('/portfolios/accounts');
    }

    async getTransactions(accountId: string, page = 1, limit = 20) {
        return this.request<PaginatedResponse<Transaction>>(
            `/portfolios/accounts/${accountId}/transactions?page=${page}&limit=${limit}`
        );
    }

    // Goals endpoints
    async getGoals() {
        return this.request<Goal[]>('/portfolios/goals');
    }

    async getGoal(goalId: string) {
        return this.request<Goal>(`/portfolios/goals/${goalId}`);
    }

    async createGoal(data: CreateGoalRequest) {
        return this.request<Goal>('/portfolios/goals', {
            method: 'POST',
            body: data
        });
    }

    async updateGoal(goalId: string, data: Partial<CreateGoalRequest>) {
        return this.request<Goal>(`/portfolios/goals/${goalId}`, {
            method: 'PATCH',
            body: data
        });
    }

    async deleteGoal(goalId: string) {
        return this.request(`/portfolios/goals/${goalId}`, { method: 'DELETE' });
    }

    // Tax endpoints
    async getFatcaReport(taxYear: number) {
        return this.request<FatcaReport>(`/tax/fatca/${taxYear}`);
    }

    async getCrsReport(taxYear: number) {
        return this.request<CrsReport>(`/tax/crs/${taxYear}`);
    }

    async getZakatCalculation(hijriYear: number) {
        return this.request<ZakatCalculation>(`/tax/zakat/${hijriYear}`);
    }

    // Documents endpoints
    async getDocuments() {
        return this.request<Document[]>('/documents');
    }

    async uploadDocument(file: File, type: string) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', type);

        const token = this.getToken();
        const response = await fetch(`${this.baseUrl}/documents/upload`, {
            method: 'POST',
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: formData
        });

        if (!response.ok) {
            throw new ApiClientError(response.status, { code: 'UPLOAD_FAILED', message: 'Upload failed' });
        }

        return response.json();
    }

    // Fee endpoints
    async calculateFee(data: { fee_code: string; base_amount?: number; quantity?: number }) {
        return this.request<any>('/fees/calculate', {
            method: 'POST',
            body: data
        });
    }

    async chargeFee(data: { fee_code: string; quantity?: number; payment_method_id?: string; reference_type?: string; reference_id?: string; metadata?: any }) {
        return this.request<any>('/fees/charge', {
            method: 'POST',
            body: data
        });
    }

    private getMockData(endpoint: string, options: any): any {
        if (endpoint.includes('/fees/calculate')) {
            const body = JSON.parse(options.body || '{}');
            const amount = body.fee_code === 'TAX_REPORT_FATCA' ? 19.99 : 9.99;
            return {
                fee_amount: amount,
                currency: 'USD',
                description: 'Demo Fee Calculation',
                chargeable_to: 'end_user',
                is_optional: true,
                breakdown: { rate: null }
            };
        }
        if (endpoint.includes('/fees/charge')) {
            return {
                charge_id: 'mock_charge_' + Math.random().toString(36).substring(7),
                status: 'captured',
                amount: 19.99,
                currency: 'USD',
                created_at: new Date().toISOString()
            };
        }
        if (endpoint.includes('/users/me')) {
            return {
                id: 'demo-user',
                email: 'demo@wealth.com',
                full_name: 'Demo User',
                nationality: 'US',
                residency_country: 'UAE'
            };
        }
        return {};
    }
}

// Type definitions
export interface UserProfile {
    id: string;
    email: string;
    full_name: string;
    phone?: string;
    nationality: string;
    residency_country: string;
    kyc_status: 'pending' | 'verified' | 'rejected';
    subscription_tier: 'basic' | 'premium';
    created_at: string;
}

export interface Portfolio {
    total_aum: number;
    currency: string;
    change_percentage: number;
    last_synced_at: string;
    accounts_count: number;
    goals_count: number;
    asset_allocation: Record<string, number>;
}

export interface Account {
    id: string;
    account_name: string;
    account_type: 'checking' | 'savings' | 'investment';
    currency: string;
    current_balance: number;
    balance_usd: number;
    holdings_count: number;
    last_sync_at: string | null;
}

export interface Transaction {
    id: string;
    date: string;
    description: string;
    amount: number;
    currency: string;
    type: 'credit' | 'debit';
    category?: string;
}

export interface Goal {
    id: string;
    goal_type: string;
    name: string;
    target_amount: number;
    current_amount: number;
    progress_percentage: number;
    target_date: string;
    monthly_contribution: number;
    status: 'active' | 'paused' | 'completed' | 'cancelled';
    risk_level?: string;
}

export interface CreateGoalRequest {
    goal_type: string;
    name: string;
    target_amount: number;
    target_date: string;
    monthly_contribution?: number;
    risk_level?: string;
}

export interface FatcaReport {
    is_us_person: boolean;
    requires_fbar: boolean;
    total_foreign_assets: number;
    fbar_pdf_url?: string;
}

export interface CrsReport {
    tax_residence_countries: string[];
    reportable_accounts: unknown[];
    total_account_balance: number;
}

export interface ZakatCalculation {
    hijri_year: number;
    zakatable_assets: Record<string, number>;
    zakat_due: number;
    nisab_met: boolean;
}

export interface Document {
    id: string;
    name: string;
    type: string;
    url: string;
    created_at: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    pagination: {
        page: number;
        page_size: number;
        total_items: number;
        total_pages: number;
    };
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL);
export const calculateFee = (data: { fee_code: string; base_amount?: number; quantity?: number }) => apiClient.calculateFee(data);
export default apiClient;
