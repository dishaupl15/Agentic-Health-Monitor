import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageShell from '../components/PageShell.jsx'
import { getHistory } from '../services/api.js'

const riskConfig = {
  Emergency: { color: '#f87171', bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.3)', dot: '#f87171' },
  High:      { color: '#fb923c', bg: 'rgba(249,115,22,0.15)', border: 'rgba(249,115,22,0.3)', dot: '#fb923c' },
  Medium:    { color: '#fbbf24', bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)', dot: '#fbbf24' },
  Low:       { color: '#34d399', bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.3)', dot: '#34d399' },
}

const cardStyle = { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '1rem' }
const innerCard = { background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '0.75rem' }

function StatCard({ label, value, sub }) {
  return (
    <div className="p-5 text-center" style={cardStyle}>
      <p className="text-2xl font-black text-white">{value}</p>
      <p className="text-xs font-semibold text-brand-400 mt-1">{label}</p>
      {sub && <p className="text-xs text-slate-500 mt-0.5">{sub}</p>}
    </div>
  )
}

export default function History() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState(null)
  const [filter, setFilter] = useState('All')
  const navigate = useNavigate()

  useEffect(() => {
    getHistory()
      .then((data) => setHistory(data.reports || []))
      .catch((err) => setError(err.message || 'Unable to load history'))
      .finally(() => setLoading(false))
  }, [])

  const riskLevels = ['All', 'Emergency', 'High', 'Medium', 'Low']
  const filtered = filter === 'All' ? history : history.filter((r) => r.risk_level === filter)
  const stats = {
    total: history.length,
    high: history.filter((r) => ['Emergency', 'High'].includes(r.risk_level)).length,
    latest: history[0] ? new Date(history[0].created_at).toLocaleDateString() : '—',
  }

  return (
    <PageShell title="Assessment History" description="Browse all saved health reports and track your assessment history over time.">
      <div className="space-y-6">

        {!loading && !error && history.length > 0 && (
          <div className="grid grid-cols-3 gap-4">
            <StatCard label="Total Reports" value={stats.total} />
            <StatCard label="High Risk" value={stats.high} sub="Emergency + High" />
            <StatCard label="Latest" value={stats.latest} />
          </div>
        )}

        {/* Filter tabs */}
        {!loading && !error && history.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {riskLevels.map((level) => {
              const cfg = riskConfig[level]
              const count = level === 'All' ? history.length : history.filter((r) => r.risk_level === level).length
              const isActive = filter === level
              const activeStyle = level === 'All'
                ? { background: 'rgba(6,148,162,0.2)', border: '1px solid rgba(22,189,202,0.4)', color: '#7edce2' }
                : cfg ? { background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.color } : {}
              const inactiveStyle = { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }
              return (
                <button
                  key={level}
                  onClick={() => setFilter(level)}
                  className="rounded-lg px-4 py-2 text-xs font-semibold transition-all duration-200"
                  style={isActive ? activeStyle : inactiveStyle}
                >
                  {level} {count > 0 && <span className="ml-1 opacity-70">({count})</span>}
                </button>
              )
            })}
          </div>
        )}

        {loading ? (
          <div className="p-12 text-center" style={cardStyle}>
            <svg className="h-8 w-8 animate-spin text-brand-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p className="text-slate-400 text-sm">Loading reports...</p>
          </div>
        ) : error ? (
          <div className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-red-400"
            style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}>
            <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center" style={cardStyle}>
            <div className="text-5xl mb-4">📋</div>
            <p className="text-white font-semibold mb-2">
              {history.length === 0 ? 'No reports yet' : `No ${filter} risk reports`}
            </p>
            <p className="text-sm text-slate-400 mb-6">
              {history.length === 0 ? 'Complete an assessment to start tracking your health history.' : 'Try a different filter.'}
            </p>
            {history.length === 0 && (
              <button onClick={() => navigate('/symptom-form')} className="btn-primary">Start Assessment</button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((report) => {
              const cfg = riskConfig[report.risk_level] || riskConfig.Low
              const isOpen = expanded === report.id
              return (
                <article key={report.id} className="overflow-hidden transition-all duration-300"
                  style={{ ...cardStyle, borderColor: isOpen ? 'rgba(22,189,202,0.25)' : 'rgba(255,255,255,0.1)' }}>
                  <button className="w-full text-left p-5" onClick={() => setExpanded(isOpen ? null : report.id)}>
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="h-2.5 w-2.5 rounded-full shrink-0" style={{ background: cfg.dot }} />
                        <div>
                          <p className="text-sm font-bold text-white">{report.name}</p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            {report.age} yrs · {report.gender} · {new Date(report.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
                          style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.color }}>
                          {report.risk_level}
                        </span>
                        <span className="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold text-slate-300"
                          style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.1)' }}>
                          {report.confidence}
                        </span>
                        <svg className={`h-4 w-4 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </div>
                    {!isOpen && <p className="mt-2 text-xs text-slate-500 truncate pl-5">{report.symptoms}</p>}
                  </button>

                  {isOpen && (
                    <div className="px-5 pb-5 pt-4 space-y-4 animate-fade-in"
                      style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                      <div className="grid gap-4 sm:grid-cols-2">
                        <div>
                          <p className="label-text mb-1">Symptoms</p>
                          <p className="text-sm text-slate-300">{report.symptoms}</p>
                        </div>
                        <div>
                          <p className="label-text mb-1">Urgency</p>
                          <p className="text-sm font-semibold" style={{ color: cfg.color }}>{report.urgency}</p>
                        </div>
                        <div>
                          <p className="label-text mb-2">Possible Conditions</p>
                          <div className="flex flex-wrap gap-1.5">
                            {report.possible_conditions?.map((c, i) => (
                              <span key={i} className="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
                                style={{ background: 'rgba(6,148,162,0.15)', border: '1px solid rgba(22,189,202,0.25)', color: '#7edce2' }}>
                                {c.name}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div>
                          <p className="label-text mb-1">Duration · Severity</p>
                          <p className="text-sm text-slate-300">{report.duration} · {report.severity}</p>
                        </div>
                      </div>
                      <div className="p-4" style={innerCard}>
                        <p className="label-text mb-1">Recommendation</p>
                        <p className="text-sm text-slate-300">{report.recommendation}</p>
                      </div>
                    </div>
                  )}
                </article>
              )
            })}
          </div>
        )}
      </div>
    </PageShell>
  )
}
