import { NextRequest, NextResponse } from 'next/server';
import { SignJWT } from 'jose';

const SECRET_KEY = new TextEncoder().encode(
    process.env.JWT_SECRET || 'gcc-wealth-platform-secret-key-min-32-chars'
);

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
        const { refresh_token } = body;

        if (!refresh_token) {
            return NextResponse.json(
                { code: 'INVALID_REQUEST', message: 'Missing refresh token' },
                { status: 400 }
            );
        }

        // In a real app, verify the refresh token. 
        // Here we just mock success and return new tokens.

        const accessToken = await createToken({ type: 'access' }, '30m');
        const newRefreshToken = await createToken({ type: 'refresh' }, '7d');

        return NextResponse.json({
            access_token: accessToken,
            refresh_token: newRefreshToken,
            token_type: 'bearer',
            expires_in: 1800,
        });
    } catch (error) {
        return NextResponse.json(
            { code: 'SERVER_ERROR', message: 'Refresh failed' },
            { status: 500 }
        );
    }
}
