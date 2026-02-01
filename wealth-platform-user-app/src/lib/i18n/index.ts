/**
 * Internationalization
 * ====================
 * 
 * Multi-language support with RTL for Arabic.
 */

import { useTenant } from '@/components/tenant/TenantProvider';

export type Locale = 'en' | 'ar';

const translations: Record<Locale, Record<string, string>> = {
    en: {
        // Navigation
        'nav.portfolio': 'Portfolio',
        'nav.goals': 'Goals',
        'nav.tax': 'Tax',
        'nav.documents': 'Documents',
        'nav.settings': 'Settings',
        'nav.logout': 'Logout',

        // Portfolio
        'portfolio.title': 'Portfolio Overview',
        'portfolio.total_value': 'Total Net Worth',
        'portfolio.accounts': 'Your Accounts',
        'portfolio.performance': 'Performance',
        'portfolio.allocation': 'Asset Allocation',
        'portfolio.last_updated': 'Last updated',
        'portfolio.sync': 'Sync Accounts',

        // Goals
        'goals.title': 'Investment Goals',
        'goals.create': 'Create Goal',
        'goals.target': 'Target Amount',
        'goals.current': 'Current Amount',
        'goals.progress': 'Progress',
        'goals.on_track': 'On Track',
        'goals.behind': 'Behind Schedule',
        'goals.types.retirement': 'Retirement',
        'goals.types.education': 'Education',
        'goals.types.home': 'Buy a Home',
        'goals.types.travel': 'Travel',
        'goals.types.custom': 'Custom Goal',

        // Tax
        'tax.title': 'Tax Reports',
        'tax.fatca': 'FATCA Reporting',
        'tax.crs': 'CRS Reporting',
        'tax.zakat': 'Zakat Calculator',
        'tax.generate': 'Generate Report',
        'tax.download': 'Download PDF',

        // Common
        'common.loading': 'Loading...',
        'common.error': 'An error occurred',
        'common.save': 'Save',
        'common.cancel': 'Cancel',
        'common.delete': 'Delete',
        'common.confirm': 'Confirm',
        'common.next': 'Next',
        'common.back': 'Back',
        'common.submit': 'Submit',
        'common.search': 'Search',
        'common.filter': 'Filter',
        'common.all': 'All',

        // Auth
        'auth.login': 'Sign In',
        'auth.logout': 'Sign Out',
        'auth.email': 'Email Address',
        'auth.password': 'Password',
        'auth.forgot_password': 'Forgot Password?',
        'auth.register': 'Create Account',
    },
    ar: {
        // Navigation
        'nav.portfolio': 'المحفظة',
        'nav.goals': 'الأهداف',
        'nav.tax': 'الضرائب',
        'nav.documents': 'المستندات',
        'nav.settings': 'الإعدادات',
        'nav.logout': 'تسجيل الخروج',

        // Portfolio
        'portfolio.title': 'نظرة عامة على المحفظة',
        'portfolio.total_value': 'إجمالي صافي الثروة',
        'portfolio.accounts': 'حساباتك',
        'portfolio.performance': 'الأداء',
        'portfolio.allocation': 'توزيع الأصول',
        'portfolio.last_updated': 'آخر تحديث',
        'portfolio.sync': 'مزامنة الحسابات',

        // Goals
        'goals.title': 'أهداف الاستثمار',
        'goals.create': 'إنشاء هدف',
        'goals.target': 'المبلغ المستهدف',
        'goals.current': 'المبلغ الحالي',
        'goals.progress': 'التقدم',
        'goals.on_track': 'على المسار الصحيح',
        'goals.behind': 'متأخر عن الجدول',
        'goals.types.retirement': 'التقاعد',
        'goals.types.education': 'التعليم',
        'goals.types.home': 'شراء منزل',
        'goals.types.travel': 'السفر',
        'goals.types.custom': 'هدف مخصص',

        // Tax
        'tax.title': 'التقارير الضريبية',
        'tax.fatca': 'تقارير فاتكا',
        'tax.crs': 'تقارير CRS',
        'tax.zakat': 'حاسبة الزكاة',
        'tax.generate': 'إنشاء تقرير',
        'tax.download': 'تحميل PDF',

        // Common
        'common.loading': 'جاري التحميل...',
        'common.error': 'حدث خطأ',
        'common.save': 'حفظ',
        'common.cancel': 'إلغاء',
        'common.delete': 'حذف',
        'common.confirm': 'تأكيد',
        'common.next': 'التالي',
        'common.back': 'السابق',
        'common.submit': 'إرسال',
        'common.search': 'بحث',
        'common.filter': 'تصفية',
        'common.all': 'الكل',

        // Auth
        'auth.login': 'تسجيل الدخول',
        'auth.logout': 'تسجيل الخروج',
        'auth.email': 'البريد الإلكتروني',
        'auth.password': 'كلمة المرور',
        'auth.forgot_password': 'نسيت كلمة المرور؟',
        'auth.register': 'إنشاء حساب',
    }
};

export function useTranslation() {
    const tenant = useTenant();
    const locale: Locale = tenant.country === 'SA' ? 'ar' : 'en';

    const t = (key: string, params?: Record<string, string | number>): string => {
        let text = translations[locale][key] || translations['en'][key] || key;

        // Replace parameters
        if (params) {
            Object.entries(params).forEach(([param, value]) => {
                text = text.replace(`{{${param}}}`, String(value));
            });
        }

        return text;
    };

    const formatCurrency = (amount: number, currency = 'USD'): string => {
        return new Intl.NumberFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2
        }).format(amount);
    };

    const formatDate = (date: Date | string): string => {
        const d = typeof date === 'string' ? new Date(date) : date;
        return new Intl.DateTimeFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(d);
    };

    const formatNumber = (num: number): string => {
        return new Intl.NumberFormat(locale === 'ar' ? 'ar-SA' : 'en-US').format(num);
    };

    const formatPercentage = (value: number): string => {
        return new Intl.NumberFormat(locale === 'ar' ? 'ar-SA' : 'en-US', {
            style: 'percent',
            minimumFractionDigits: 1,
            maximumFractionDigits: 2
        }).format(value / 100);
    };

    return { t, formatCurrency, formatDate, formatNumber, formatPercentage, locale, isRTL: locale === 'ar' };
}

export { translations };
