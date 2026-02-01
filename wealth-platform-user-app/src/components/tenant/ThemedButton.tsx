'use client';

import { useTenant } from '@/components/tenant/TenantProvider';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
    fullWidth?: boolean;
}

export function ThemedButton({
    children,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    leftIcon,
    rightIcon,
    fullWidth = false,
    className = '',
    disabled,
    ...props
}: ButtonProps) {
    const tenant = useTenant();
    const primaryColor = tenant.branding.primary_color;

    const sizeClasses = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-5 py-2.5 text-base',
        lg: 'px-7 py-3.5 text-lg'
    };

    const getVariantStyles = (): React.CSSProperties => {
        switch (variant) {
            case 'primary':
                return { backgroundColor: primaryColor, color: 'white' };
            case 'secondary':
                return {
                    backgroundColor: 'transparent',
                    color: primaryColor,
                    border: `2px solid ${primaryColor}`
                };
            case 'ghost':
                return {
                    backgroundColor: `${primaryColor}10`,
                    color: primaryColor
                };
            case 'danger':
                return { backgroundColor: '#EF4444', color: 'white' };
            default:
                return {};
        }
    };

    return (
        <button
            className={`
        inline-flex items-center justify-center gap-2 
        rounded-xl font-semibold 
        transition-all duration-200 
        hover:opacity-90 hover:-translate-y-0.5
        active:translate-y-0
        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0
        ${sizeClasses[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
            style={getVariantStyles()}
            disabled={disabled || isLoading}
            {...props}
        >
            {isLoading ? (
                <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle
                            className="opacity-25"
                            cx="12" cy="12" r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                            fill="none"
                        />
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                    </svg>
                    <span>Loading...</span>
                </>
            ) : (
                <>
                    {leftIcon}
                    {children}
                    {rightIcon}
                </>
            )}
        </button>
    );
}
