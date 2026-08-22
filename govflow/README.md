# GovFlow AI

Universal Government Service Browser Agent - Citizen Frontend

A modern, accessible, multilingual frontend for a Self-Learning Government Browser Agent. Built with Next.js 15, React, TypeScript, Tailwind CSS, and shadcn/ui.

![GovFlow AI](https://img.shields.io/badge/GovFlow-AI-blue?style=for-the-badge)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?style=for-the-badge)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-blue?style=for-the-badge)
![shadcn/ui](https://img.shields.io/badge/shadcn/ui-components-blue?style=for-the-badge)

## 📋 Overview

GovFlow AI is a citizen-facing portal that helps users interact with government services through an AI-powered browser agent. The frontend provides:

- **Service discovery** and application submission
- **Application tracking** with real-time status updates
- **Multi-step workflow wizards** for applying and updating records
- **AI conversation interface** with the browser agent
- **Document vault** for managing government documents
- **Grievance system** for reporting service issues
- **Human approval screens** for sensitive actions

## 🏗️ Architecture

The application follows a **feature-based architecture** with the following structure:

```
apps/web/
├── app/                    # Next.js 14 App Router
│   ├── page.tsx            # Home/dashboard page
│   ├── apply/              # Apply workflow (multi-step wizard)
│   ├── update/             # Update records workflow
│   ├── applications/       # My applications tracking
│   ├── chat/               # AI workspace
│   ├── settings/           # User settings
│   └── /[id]/              # Application detail page
├── components/             # Reusable UI components
│   ├── ui/                 # shadcn/ui components (Button, Card, etc.)
│   ├── layout/             # Sidebar, Header, Footer, DashboardLayout
│   ├── common/             # Breadcrumb, etc.
│   ├── agent/              # AI workspace components
│   ├── workflow/           # Multi-step wizard components
│   └── applications/       # Application tracking components
├── features/               # Feature-specific components
├── hooks/                  # Custom React hooks
├── lib/                    # Utility functions and types
├── styles/                 # Global styles and Tailwind config
└── i18n/                   # Multilingual support
```

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | Next.js 15 (App Router) |
| **Language** | TypeScript |
| **Styling** | Tailwind CSS |
| **UI Library** | shadcn/ui |
| **Icons** | Lucide React |
| **Forms** | React Hook Form |
| **Validation** | Zod |
| **Animation** | Framer Motion |
| **Internationalization** | next-intl (English, Kannada, Hindi) |
| **State** | React Query / next-themes |
| **HTTP** | SWR / fetch (API integration) |

## 📱 Features by Phase

### Phase 1 — Project Foundation
- ✅ Navigation system (Sidebar, Header, Footer)
- ✅ Responsive Dashboard layout
- ✅ Breadcrumb component
- ✅ Language switcher (EN, kn, HI)
- ✅ Theme toggle (light/dark/system)
- ✅ User profile dropdown
- ✅ Notification bell
- ✅ All global routes: `/`, `/apply`, `/update`, `/documents`, `/applications`, `/grievance`, `/settings`

### Phase 3 — AI Workspace
- ✅ Two-column layout (Conversation + Agent Activity)
- ✅ Conversation panel (User messages, AI messages, typing indicator)
- ✅ Suggested replies
- ✅ Agent activity panel (Current portal, step, progress, confidence, runtime)
- ✅ Progress Timeline component (7 states: Understanding → Ready)
- ✅ Browser Preview component (header, URL bar, screenshot placeholder)
- ✅ Mobile collapse behavior

### Phase 5 — Service Workflow Wizard
- ✅ Reusable multi-step wizard supporting both "Apply" and "Update" modes
- ✅ 6 steps: Service → Eligibility → Documents → Information → Review → Approval
- ✅ `ServiceStep` - Grid of service cards with selection highlight
- ✅ `EligibilityStep` + `EligibilityCard` - Criteria with met/not-met status
- ✅ `DocumentsStep` + `DocumentChecklist` - 4 statuses (required/uploaded/missing/verified), progress bar, upload/remove actions
- ✅ `InformationStep` - Multi-section form (Personal, Address, Service Details), supports text/email/phone/date/select/textarea
- ✅ `ReviewSummary` - Cards for Service, Eligibility, Documents, Personal Info, Address + declaration
- ✅ `ApprovalStep` - Success state with reference number, processing time, status badge, next-steps timeline, action buttons
- ✅ `WizardContainer` - Step indicator, navigation (Back/Continue/Submit), mode badge

### Phase 7 — My Applications Tracking
- ✅ ApplicationCard - Service, Department, Status, Date, Reference number, View/Check Status buttons
- ✅ ApplicationFilters - Status tabs (All/Draft/Submitted/Processing/Approved/Rejected) with counts, Search bar
- ✅ ApplicationTimeline - Status history with dots/line, completed/current/upcoming states
- ✅ ApplicationsPage - Filters + Search + Card grid with lazy loading
- ✅ ApplicationDetailsPage - Full view with timeline, documents, department info, back button
- ✅ Consistent status colors across all pages

## 🌐 Multilingual Support

Supported languages: English, Kannada, Hindi

- ✅ No hardcoded strings - all translation keys
- ✅ Language persists across navigation
- ✅ next-intl integration
- ✅ RTL-safe layout preparation
- ✅ Text expansion does not break UI

Language codes: `en`, `kn`, `hi`

## 🔧 Development

### Prerequisites

- Node.js 20+
- npm or pnpm

### Installation

```bash
# From root
cd govflow

# Install frontend dependencies
cd apps/web && npm install

# Install shared package
cd ../.. && npm install
```

### Development

```bash
# Start development server
npm run dev

# Frontend only
npm run dev:web

# Typecheck
npm run typecheck

# Lint
npm run lint

# Build
npm run build:web
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your settings
# Required: NEXT_PUBLIC_API_URL (backend API endpoint)
```

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start both frontend and backend |
| `npm run dev:web` | Start frontend only (port 3000) |
| `npm run dev:api` | Start backend only |
| `npm run build` | Build all packages |
| `npm run build:web` | Build frontend only |
| `npm run test` | Run all tests |
| `npm run test:unit` | Run unit tests |
| `npm run lint` | Lint all packages |
| `npm run typecheck` | TypeScript check (zero errors) |
| `npm run db:generate` | Generate database migration |
| `npm run db:push` | Push schema changes |
| `npm run db:migrate` | Run migrations |
| `npm run db:studio` | Open Prisma Studio |

## 📦 Component Inventory

### Layout Components
- `Sidebar` - Collapsible navigation with active route highlighting
- `Header` - Search, language switcher, theme toggle, notifications, user avatar
- `Footer` - 4-column footer with links, legal, languages
- `DashboardLayout` - Wraps sidebar + header + main content with mobile overlay

### UI Components (shadcn/ui)
- `Button` - Primary, secondary, dangerous, outline, ghost, icon, size variants
- `Card` - CardHeader, CardTitle, CardDescription, CardContent, CardFooter
- `Badge` - Default, secondary, success, warning, destructive, outline
- `Input` - Text, email, phone, date, textarea with validation
- `Select` - Radix-based dropdown with search
- `Tooltip` - Radix tooltip with proper positioning
- `Dialog` - Radix dialog with overlay, header, footer
- `Avatar` - User avatar with image/fallback
- `Sheet` - Radix-based slide panel
- `Separator` - Visual divider

### Workflow Components
- `WizardContainer` - Step indicator (numbered circles + progress bar), Back/Continue/Submit
- `ServiceStep` - Service selection grid
- `EligibilityStep` + `EligibilityCard` - Criteria checklist
- `DocumentsStep` + `DocumentChecklist` + `DocumentChecklistItem` - Document upload management
- `InformationStep` - Multi-section form
- `ReviewSummary` - Application review before submission
- `ApprovalStep` - Approval confirmation screen

### Application Tracking
- `ApplicationCard` - Service, Department, Status, Date, Reference, View/Check actions
- `ApplicationFilters` - Status tabs + Search bar with counts
- `ApplicationTimeline` - Status history visualization
- `ApplicationDetailsPage` - Full application view

### AI Workspace
- `ConversationPanel` - User/AI messages, typing indicator, suggested replies
- `AgentActivity` - Current portal, step, progress, confidence, runtime cards
- `Timeline` - 7-state agent progress
- `BrowserPreview` - macOS-style browser header with screenshot placeholder

## 🎨 Design Principles

| Principle | Description |
|-----------|-------------|
| **Trustworthy** | Clean, professional aesthetic; government-tech feel |
| **Accessibility-first** | WCAG AA target; keyboard navigation, ARIA labels, focus rings, color contrast |
| **Mobile-responsive** | Mobile-first; no horizontal scrolling at any breakpoint |
| **Dark/light mode** | Fully supported with `next-themes` |
| **Component-driven** | No duplicated UI; everything reusable |
| **Extensible routing** | All routes driven by API responses, not hardcoded |
| **Minimal learning curve** | Intuitive navigation, minimal interactions |

### Color Palette

- **Primary**: GovBlue (`#1e3a8a` → `#0ea5e9` → `#0284c7`)
- **Secondary**: Slate grays
- **Success**: Green
- **Warning**: Yellow/Orange
- **Danger**: Red
- **Neutral**: Slate 50-950 series

### Typography

- **Font family**: Inter, system-ui, sans-serif
- **Size scale**: Based on Tailwind's default scale with custom modifications
- **Line height**: Adequate for readability; scaled for mobile

### Spacing

- **System**: Tailwind's spacing scale (0-6+)
- **Consistent**: All padding/margins use the theme scale
- **Grid gaps**: Consistent across all layouts

## ♿ Accessibility

Target: **WCAG AA**

- **Keyboard navigation**: All interactive elements reachable via Tab
- **Focus rings**: Visible focus states on all focusable elements
- **ARIA labels**: Proper labels on buttons, inputs, complex widgets
- **Screen reader compatibility**: Semantic HTML, meaningful alt text, logical heading order
- **Color contrast**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Accessible modals**: Focus trap, escape key support, appropriate aria-modal
- **Skip links**: Hidden skip-to-main-content link

## 📱 Responsiveness

Tested at breakpoints: **320px, 375px, 768px, 1024px, 1440px**

- **No horizontal scrolling** at any width
- **Sidebar**: Collapses to icon-only on mobile; floating FAB opens sheet panel
- **Header**: Full-width on mobile; shrinks on scroll on desktop
- **Cards**: Stack vertically on mobile; show in grid on larger screens
- **Modals/sheets**: Full-width on mobile; scaled down on desktop
- **Timeline**: Single column on mobile; readable on all sizes

## 🚀 Demo Mode

The application includes a polished demo experience without backend integration:

- **Agent Activity** displays current task, active portal, workflow step, progress percentage
- **Status visualization** shows Waiting for approval, Completed state
- **Mock data** populates all pages for demonstration purposes
- **No browser automation** - all intelligence simulated via static data

## 📄 License

MIT License. See LICENSE file for details.

## � contributors

This project was built by a single frontend engineer serving as Lead Frontend Engineer, UI/UX Designer, and Product Designer.

- **Navigation & Layout** (Phase 1)
- **AI Workspace** (Phase 3)
- **Service Workflow Wizard** (Phase 5)
- **Application Tracking** (Phase 7)
- **Accessibility & Responsiveness** (all phases)
- **Multilingual support** (all phases)

---

Built with ❤️ for the GovFlow AI hackathon competition.