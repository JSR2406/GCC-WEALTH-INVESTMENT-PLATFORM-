import { NextRequest, NextResponse } from 'next/server';
import { SignJWT, jwtVerify } from 'jose';

// Secret key for JWT (in production, use environment variable)
const SECRET_KEY = new TextEncoder().encode(
    process.env.JWT_SECRET || 'gcc-wealth-platform-secret-key-min-32-chars'
);

// Mock Users Database
const MOCK_USERS: Record<string, Record<string, any>> = {
    fab: {
        'demo@fab.ae': {
            id: 'user-fab-001',
            email: 'demo@fab.ae',
            password: 'demo123',
            full_name: 'Ahmed Al-Zahrani',
            bank_id: 'fab-001',
            bank_slug: 'fab',
            kyc_status: 'verified',
            subscription_tier: 'premium',
            is_active: true,
        },
    },
    hsbc: {
        'john@example.com': {
            id: 'user-hsbc-001',
            email: 'john@example.com',
            password: 'demo123',
            full_name: 'John Smith',
            bank_id: 'hsbc-001',
            bank_slug: 'hsbc',
            kyc_status: 'verified',
            subscription_tier: 'premium',
            is_active: true,
        },
    },
    rajhi: {
        'mohammed@example.com': {
            id: 'user-rajhi-001',
            email: 'mohammed@example.com',
            password: 'demo123',
            full_name: 'محمد الراجحي',
            bank_id: 'rajhi-001',
            bank_slug: 'rajhi',
            kyc_status: 'verified',
            subscription_tier: 'premium',
            is_active: true,
        },
    },
};

async function createToken(payload: any, expiresIn: string = '30m') {
    return await new SignJWT(payload)
        .setProtectedHeader({ alg: 'HS256' })
        .setIssuedAt()
        .setExpirationTime(expiresIn)
        .sign(SECRET_KEY);
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { email, password, bank_slug } = body;

        // Validate input
        if (!email || !password || !bank_slug) {
            return NextResponse.json(
                { code: 'INVALID_REQUEST', message: 'Missing required fields' },
                { status: 400 }
            );
        }

        // Find user
        const bankUsers = MOCK_USERS[bank_slug] || {};
        const user = bankUsers[email];

        if (!user || user.password !== password) {
            return NextResponse.json(
                { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password' },
                { status: 401 }
            );
        }

        // Create tokens
        const tokenPayload = {
            sub: user.id,
            email: user.email,
            bank_id: user.bank_id,
            bank_slug: user.bank_slug,
            type: 'access',
        };

        const accessToken = await createToken(tokenPayload, '30m');
        const refreshToken = await createToken({ sub: user.id, type: 'refresh' }, '7d');

        // Return response (excluding password)
        const { password: _, ...userWithoutPassword } = user;

        return NextResponse.json({
            user: userWithoutPassword,
            tokens: {
                access_token: accessToken,
                refresh_token: refreshToken,
                token_type: 'bearer',
                expires_in: 1800,
            },
        });
    } catch (error) {
        console.error('Login error:', error);
        return NextResponse.json(
            { code: 'SERVER_ERROR', message: 'An error occurred during login' },
            { status: 500 }
        );
    }
}
