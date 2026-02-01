import Link from 'next/link';
import { getAllTenantSlugs, getTenantBySlug } from '@/lib/tenant';

export default function HomePage() {
  const tenants = getAllTenantSlugs();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Decorative background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-500/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-4 py-20">
        {/* Hero */}
        <header className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 backdrop-blur border border-white/20 text-green-400 text-sm mb-6">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            Demo Mode
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            GCC Wealth
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-300">
              Platform
            </span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Cross-border wealth management for affluent expats in UAE and Saudi Arabia.
            White-labeled for regional banks.
          </p>
        </header>

        {/* Feature highlights */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
          {[
            { icon: '🏦', label: 'Multi-Bank' },
            { icon: '📊', label: 'Goal Tracking' },
            { icon: '🕌', label: 'Sharia Compliant' },
            { icon: '📋', label: 'Tax Reports' },
          ].map((feature) => (
            <div
              key={feature.label}
              className="bg-white/5 backdrop-blur border border-white/10 rounded-xl p-4 text-center"
            >
              <div className="text-3xl mb-2">{feature.icon}</div>
              <div className="text-white font-medium text-sm">{feature.label}</div>
            </div>
          ))}
        </div>

        {/* Tenant Selection */}
        <section>
          <h2 className="text-2xl font-semibold text-white text-center mb-8">
            Select a Demo Bank
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {tenants.map((slug) => {
              const config = getTenantBySlug(slug);
              if (!config) return null;

              return (
                <Link
                  key={slug}
                  href={`/${slug}`}
                  className="group relative bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all hover:border-white/30 hover:-translate-y-1"
                >
                  {/* Bank Logo */}
                  <div
                    className="w-14 h-14 rounded-xl flex items-center justify-center text-white text-2xl font-bold mb-4"
                    style={{ backgroundColor: config.branding.primary_color }}
                  >
                    {config.name.charAt(0)}
                  </div>

                  {/* Bank Info */}
                  <h3 className="text-xl font-semibold text-white mb-1">
                    {config.branding.app_name}
                  </h3>
                  <p className="text-gray-400 text-sm mb-4">
                    {config.name}
                  </p>

                  {/* Country Badge */}
                  <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${config.country === 'SA'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-blue-500/20 text-blue-400'
                    }`}>
                    {config.country === 'SA' ? '🇸🇦 Saudi Arabia' : '🇦🇪 UAE'}
                  </div>

                  {/* Features */}
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <div className="flex flex-wrap gap-2">
                      {config.features.sharia_products && (
                        <span className="text-xs text-gray-500">🕌 Sharia</span>
                      )}
                      {config.features.zakat_calculator && (
                        <span className="text-xs text-gray-500">💰 Zakat</span>
                      )}
                      {config.features.goal_based_investing && (
                        <span className="text-xs text-gray-500">🎯 Goals</span>
                      )}
                    </div>
                  </div>

                  {/* Arrow */}
                  <div
                    className="absolute top-6 right-6 w-8 h-8 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                    style={{ backgroundColor: config.branding.primary_color }}
                  >
                    <span className="text-white">→</span>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* Tech Stack */}
        <footer className="mt-20 pt-10 border-t border-white/10">
          <div className="text-center">
            <p className="text-gray-500 text-sm mb-4">Built with</p>
            <div className="flex justify-center gap-6 text-gray-400">
              <span>Next.js 14</span>
              <span>•</span>
              <span>TypeScript</span>
              <span>•</span>
              <span>Tailwind CSS</span>
              <span>•</span>
              <span>FastAPI</span>
            </div>
            <p className="text-gray-600 text-xs mt-6">
              © 2026 GCC Wealth Platform. Demo Application.
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
