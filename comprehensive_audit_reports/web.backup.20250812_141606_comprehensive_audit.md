# 📊 COMPREHENSIVE AUDIT REPORT: web.backup.20250812_141606

> **Generated**: Tue Aug 12 14:16:40 EDT 2025
> **Service**: web.backup.20250812_141606
> **Assigned Port**: UNKNOWN
> **Standards Version**: 1.0.0

## 📋 COMPLIANCE SUMMARY

## 📋 FILE STRUCTURE COMPLIANCE

### 1. File Structure Requirements

❌ Dockerfile missing
✅ Dependencies file exists
✅ start.sh exists
✅ start.sh is executable
✅ src directory exists
❌ src/__init__.py missing
❌ src/main.py missing
❌ src/config.py missing
❌ src/api.py missing
❌ tests directory missing
❌ logs directory missing
❌ .env.example missing

### I/O Variables & Dependencies

#### Node.js Dependencies (package.json):
```json
{
  "name": "openpolicy-frontend",
  "version": "1.0.0",
  "description": "OpenPolicy Frontend Application",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "react-plotly.js": "^2.6.0",
    "plotly.js": "^2.27.0",
    "@heroicons/react": "^2.0.18",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "date-fns": "^2.30.0",
    "recharts": "^2.8.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/plotly.js": "^2.12.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "14.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

#### Environment Variables (.env.example):
❌ MISSING - No environment configuration found

## 🔌 PORT ASSIGNMENT

**Current Assigned Port**: UNKNOWN

❌ Port does NOT follow OpenPolicy standards (should be 9000 series)

## 📊 COMPLIANCE SCORE

**Total Checks**: 12
**Passed**: 4
**Failed**: 8
**Compliance**: 33%

**Status**: ❌ NON-COMPLIANT

## 🚀 RECOMMENDATIONS

### Missing Components:

- Review the audit output above for specific missing components
- Implement missing components according to priority order
- Re-run audit after implementation
