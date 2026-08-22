import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen">
      <header className="border-b border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <svg className="h-8 w-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              <span className="text-xl font-bold text-slate-900 dark:text-white">GovFlow AI</span>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/apply" className="btn-primary">
                Apply for Service
              </Link>
              <Link href="/documents" className="btn-secondary">
                My Documents
              </Link>
              <Link href="/applications" className="btn-secondary">
                My Applications
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden bg-gradient-to-b from-slate-50 to-white dark:from-slate-900 dark:to-slate-800 py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 dark:text-white tracking-tight mb-6">
              Government Services, <span className="text-primary-600">Simplified</span>
            </h1>
            <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-300 mb-10 max-w-2xl mx-auto">
              Tell GovFlow what you need. Our AI browser agent discovers the right government service,
              navigates official websites, fills forms, and submits applications — all with your approval.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <Link href="/apply" className="btn-primary text-lg px-8 py-3">
                Get Started
              </Link>
              <Link href="#how-it-works" className="btn-secondary text-lg px-8 py-3">
                How It Works
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16" id="how-it-works">
            <div className="card text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center">
                <svg className="w-8 h-8 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Discover</h3>
              <p className="text-slate-600 dark:text-slate-300">Describe what you need in plain language. GovFlow finds the right service, department, and official portal.</p>
            </div>
            <div className="card text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center">
                <svg className="w-8 h-8 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Execute</h3>
              <p className="text-slate-600 dark:text-slate-300">Our browser agent navigates real government websites, fills forms, uploads documents, and handles unexpected changes.</p>
            </div>
            <div className="card text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center">
                <svg className="w-8 h-8 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Approve & Track</h3>
              <p className="text-slate-600 dark:text-slate-300">Review everything before submission. Track status, raise grievances, and manage all applications in one place.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 lg:py-32 bg-white dark:bg-slate-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-slate-900 dark:text-white mb-12">Supported Services</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { name: "Income Certificate", icon: "📄", category: "Revenue" },
              { name: "Birth Certificate", icon: "📜", category: "Civil Registration" },
              { name: "Driving License", icon: "🚗", category: "Transport" },
              { name: "Aadhaar Update", icon: "🆔", category: "Identity" },
              { name: "Pension Services", icon: "👴", category: "Social Welfare" },
              { name: "Property Tax", icon: "🏠", category: "Municipal" },
              { name: "Scholarships", icon: "🎓", category: "Education" },
              { name: "Caste Certificate", icon: "📋", category: "Social Welfare" },
              { name: "Domicile Certificate", icon: "🏘️", category: "Revenue" },
            ].map((service) => (
              <Link key={service.name} href="/apply" className="card hover:shadow-md transition-shadow group">
                <div className="flex items-center gap-4">
                  <span className="text-3xl">{service.icon}</span>
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white group-hover:text-primary-600 transition-colors">{service.name}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{service.category}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 lg:py-32 bg-slate-50 dark:bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-6">Ready to Start?</h2>
          <p className="text-lg text-slate-600 dark:text-slate-300 mb-8 max-w-2xl mx-auto">
            Join thousands of citizens who use GovFlow to navigate government services effortlessly.
          </p>
          <Link href="/apply" className="btn-primary text-lg px-8 py-3 inline-block">
            Try GovFlow AI Now
          </Link>
        </div>
      </section>

      <footer className="border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="font-semibold text-slate-900 dark:text-white mb-4">GovFlow AI</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Universal government service browser agent. Making government services accessible to every citizen.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-slate-900 dark:text-white mb-4">Quick Links</h4>
              <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                <li><Link href="/apply" className="hover:text-primary-600">Apply for Service</Link></li>
                <li><Link href="/documents" className="hover:text-primary-600">Document Vault</Link></li>
                <li><Link href="/applications" className="hover:text-primary-600">Track Applications</Link></li>
                <li><Link href="/grievances" className="hover:text-primary-600">Raise Grievance</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-slate-900 dark:text-white mb-4">Languages</h4>
              <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                <li>English</li>
                <li>ಕನ್ನಡ (Kannada)</li>
                <li>हिन्दी (Hindi)</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-slate-900 dark:text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                <li><Link href="/privacy" className="hover:text-primary-600">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-primary-600">Terms of Service</Link></li>
                <li><Link href="/security" className="hover:text-primary-600">Security</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-slate-200 dark:border-slate-700 text-center text-sm text-slate-500 dark:text-slate-400">
            © 2024 GovFlow AI. Not affiliated with any government agency.
          </div>
        </div>
      </footer>
    </main>
  );
}