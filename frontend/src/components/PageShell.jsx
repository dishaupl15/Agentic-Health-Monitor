import { Link, useLocation } from 'react-router-dom'

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/symptom-form', label: 'New Assessment' },
  { to: '/history', label: 'History' },
]

export default function PageShell({ title, description, children }) {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #040810 0%, #0a1628 50%, #062a3a 100%)' }}>
      {/* Ambient glow blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full blur-3xl"
          style={{ background: 'rgba(6,148,162,0.12)' }} />
        <div className="absolute top-1/3 -right-20 h-64 w-64 rounded-full blur-3xl"
          style={{ background: 'rgba(22,189,202,0.06)' }} />
      </div>

      {/* Navbar */}
      <header className="sticky top-0 z-50 backdrop-blur-xl"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', background: 'rgba(4,8,16,0.85)' }}>
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl transition-all"
              style={{ background: 'rgba(6,148,162,0.2)', border: '1px solid rgba(22,189,202,0.3)' }}>
              <svg className="h-5 w-5 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-bold text-white leading-none">MediAI</p>
              <p className="text-xs text-brand-400 leading-none mt-0.5">Health Monitor</p>
            </div>
          </Link>

          <nav className="flex items-center gap-1">
            {navLinks.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className="rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200"
                style={pathname === to
                  ? { background: 'rgba(6,148,162,0.2)', color: '#7edce2', border: '1px solid rgba(22,189,202,0.3)' }
                  : { color: '#94a3b8' }
                }
                onMouseEnter={e => { if (pathname !== to) { e.currentTarget.style.color = '#fff'; e.currentTarget.style.background = 'rgba(255,255,255,0.07)' } }}
                onMouseLeave={e => { if (pathname !== to) { e.currentTarget.style.color = '#94a3b8'; e.currentTarget.style.background = 'transparent' } }}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      {/* Page heading */}
      <div className="mx-auto max-w-6xl px-4 pt-10 pb-6 sm:px-6">
        <div className="animate-fade-in">
          <p className="text-xs font-semibold uppercase tracking-widest text-brand-400 mb-2">Hospital AI Monitor</p>
          <h1 className="text-3xl font-bold text-white sm:text-4xl">{title}</h1>
          {description && <p className="mt-2 max-w-2xl text-slate-400 text-sm leading-relaxed">{description}</p>}
        </div>
      </div>

      <main className="mx-auto max-w-6xl px-4 pb-16 sm:px-6 animate-slide-up">
        {children}
      </main>
    </div>
  )
}
