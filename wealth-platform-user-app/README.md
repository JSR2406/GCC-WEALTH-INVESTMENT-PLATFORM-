# GCC Wealth Platform - User Application

A modern, white-labeled wealth management application for affluent expats in UAE and Saudi Arabia.

## 🌟 Features

### Multi-Tenant Architecture
- **Dynamic Tenant Resolution**: Supports subdomain, path, and custom domain routing
- **White-Label Branding**: Each bank gets custom colors, logos, and app names
- **Feature Flags**: Enable/disable features per bank (Sharia, Zakat, etc.)

### Portfolio Management
- **Account Aggregation**: Connect multiple banks and brokerages
- **Asset Allocation**: Visual breakdown of investments
- **Performance Tracking**: Real-time portfolio value updates
- **Multi-Currency Support**: USD, AED, SAR with automatic conversion

### Goal-Based Investing
- **Goal Creation Wizard**: Step-by-step goal setup
- **Progress Tracking**: Visual milestones and projections
- **Risk Profiles**: Conservative, Moderate, Aggressive options
- **Sharia Compliance**: Optional Islamic investment filtering

### Tax Compliance
- **FATCA Reporting**: For US persons
- **CRS Reporting**: Common Reporting Standard support
- **Zakat Calculator**: Interactive Islamic alms calculation

### User Experience
- **Mobile-First Design**: Optimized for smartphones
- **RTL Support**: Full Arabic language support
- **PWA Ready**: Installable as native app
- **Offline Capability**: Core features work offline

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Navigate to the app directory
cd wealth-platform-user-app

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Demo Banks

Visit these URLs to see different bank themes:
- **FAB (UAE)**: http://localhost:3000/fab
- **HSBC (UAE)**: http://localhost:3000/hsbc
- **Al Rajhi (Saudi)**: http://localhost:3000/rajhi

## 📁 Project Structure

```
src/
├── app/
│   ├── page.tsx                    # Home page (bank selector)
│   ├── layout.tsx                  # Root layout
│   ├── globals.css                 # Global styles
│   └── [tenant]/                   # Dynamic tenant routes
│       ├── layout.tsx              # Tenant layout with branding
│       ├── page.tsx                # Portfolio dashboard
│       ├── (auth)/
│       │   ├── login/page.tsx
│       │   └── kyc/
│       │       ├── personal-info/page.tsx
│       │       ├── documents/page.tsx
│       │       └── verification/page.tsx
│       ├── goals/
│       │   ├── page.tsx            # Goals list
│       │   ├── create/page.tsx     # Goal wizard
│       │   └── [id]/page.tsx       # Goal detail
│       ├── portfolio/
│       │   └── accounts/page.tsx   # Account list
│       ├── tax/
│       │   ├── page.tsx            # Tax overview
│       │   └── zakat/page.tsx      # Zakat calculator
│       ├── documents/page.tsx      # Document center
│       └── settings/page.tsx       # User settings
├── components/
│   ├── tenant/
│   │   ├── TenantProvider.tsx      # Theme context
│   │   └── ThemedButton.tsx        # Dynamic button
│   └── portfolio/
│       └── index.tsx               # Charts & cards
└── lib/
    ├── tenant.ts                   # Tenant resolution
    ├── api-client.ts               # API client
    └── i18n/
        └── index.ts                # Translations
```

## 🎨 Theming

Each tenant has dynamic theming via CSS variables:

```css
:root {
  --primary-color: #00A651;    /* Bank's primary color */
  --secondary-color: #003366;  /* Bank's secondary color */
  --font-family: 'Inter';      /* Bank's font */
}
```

These are set dynamically by the `TenantProvider` based on the bank's configuration.

## 🔗 API Integration

Configure the API endpoint in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The API client (`lib/api-client.ts`) handles:
- Authentication (JWT tokens)
- Portfolio data
- Goals management
- Tax calculations
- Document uploads

## 🌐 Internationalization

RTL and Arabic support is automatic for Saudi Arabian tenants:

```typescript
// Automatically applied based on tenant country
if (config.country === 'SA') {
  document.documentElement.dir = 'rtl';
  document.documentElement.lang = 'ar';
}
```

## 📱 Progressive Web App

The app is PWA-ready with:
- `manifest.json` for installation
- Service worker for offline support
- App-like navigation

## 🔒 Security

- JWT token-based authentication
- Secure cookie handling
- XSS protection headers
- HTTPS enforcement in production

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

## 📦 Building for Production

```bash
# Create production build
npm run build

# Start production server
npm start
```

## 🐳 Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

Proprietary - GCC Wealth Platform

---

Built with ❤️ for the Gulf region
