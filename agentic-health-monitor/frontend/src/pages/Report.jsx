import { useState, useEffect, useRef } from 'react'
import { useLocation, useNavigate, Navigate } from 'react-router-dom'
import PageShell from '../components/PageShell.jsx'
import { supabase } from '../lib/supabaseClient.js'

const riskConfig = {
  Emergency: { color: '#f87171', bg: 'rgba(239,68,68,0.15)', border: 'rgba(239,68,68,0.3)', dot: '#f87171', icon: '🚨' },
  High:      { color: '#fb923c', bg: 'rgba(249,115,22,0.15)', border: 'rgba(249,115,22,0.3)', dot: '#fb923c', icon: '⚠️' },
  Medium:    { color: '#fbbf24', bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)', dot: '#fbbf24', icon: '🔶' },
  Low:       { color: '#34d399', bg: 'rgba(16,185,129,0.15)', border: 'rgba(16,185,129,0.3)', dot: '#34d399', icon: '✅' },
}

const cardStyle = { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '1rem' }
const innerCard = { background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '0.75rem' }

function ScoreBar({ score }) {
  const pct = Math.round(score * 100)
  const grad = pct >= 80 ? 'linear-gradient(90deg,#ef4444,#f87171)' : pct >= 60 ? 'linear-gradient(90deg,#f59e0b,#fbbf24)' : 'linear-gradient(90deg,#0694a2,#16bdca)'
  return (
    <div className="mt-2">
      <div className="flex justify-between mb-1">
        <span className="text-xs text-slate-500">Risk score</span>
        <span className="text-xs font-bold text-slate-300">{pct}%</span>
      </div>
      <div className="h-1.5 w-full rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.1)' }}>
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: grad }} />
      </div>
    </div>
  )
}

export default function Report() {
  const location = useLocation()
  const navigate = useNavigate()
  const state = location.state
  const [isSaved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const saveCalledRef = useRef(false)

  if (!state?.report || !state?.form) return <Navigate to="/" replace />

  const { report, form } = state
  const followUpAnswers = report.follow_up_answers || state.follow_up_answers || {}
  const risk = riskConfig[report.risk_level] || riskConfig.Low

  // Auto-save once on load
  useEffect(() => {
    if (saveCalledRef.current) return
    saveCalledRef.current = true
    const autoSave = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session?.user?.id) return
      const { error: insertErr } = await supabase.from('assessments').insert({
        user_id: session.user.id,
        symptoms: form.symptoms,
        summary: report.explanation || '',
        risk_level: report.risk_level || 'Unknown',
        possible_conditions: report.possible_conditions || [],
        follow_up_questions: followUpAnswers,
      })
      if (!insertErr) setSaved(true)
    }
    autoSave()
  }, [])

  const handleSave = async () => {
    if (isSaved || loading) return
    setLoading(true)
    setError('')
    const { data: { session } } = await supabase.auth.getSession()
    if (!session?.user?.id) {
      setError('You must be logged in to save.')
      setLoading(false)
      return
    }
    const { error: insertErr } = await supabase.from('assessments').insert({
      user_id: session.user.id,
      symptoms: form.symptoms,
      summary: report.explanation || '',
      risk_level: report.risk_level || 'Unknown',
      possible_conditions: report.possible_conditions || [],
      follow_up_questions: followUpAnswers,
    })
    if (insertErr) setError(insertErr.message)
    else setSaved(true)
    setLoading(false)
  }

  return (
    <PageShell title="Final Assessment Report" description="Your AI-generated health assessment based on symptoms and follow-up answers.">
      <div className="space-y-6">

        {/* Risk banner */}
        <div className="rounded-2xl p-6" style={{ background: risk.bg, border: `1px solid ${risk.border}` }}>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="text-4xl">{risk.icon}</div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Overall Risk Level</p>
                <p className="text-3xl font-black" style={{ color: risk.color }}>{report.risk_level}</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-6">
              {[['Urgency', report.urgency || 'Routine monitoring'], ['Confidence', report.confidence], ['Patient', `${form.name}, ${form.age}`]].map(([label, val]) => (
                <div key={label} className="text-right">
                  <p className="text-xs text-slate-500 mb-1">{label}</p>
                  <p className="text-sm font-bold text-white">{val}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Conditions + Explanation */}
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="p-6" style={cardStyle}>
            <h2 className="section-title mb-4 flex items-center gap-2">
              <svg className="h-4 w-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Possible Conditions
            </h2>
            {report.possible_conditions?.length > 0 ? (
              <div className="space-y-4">
                {report.possible_conditions.map((c, i) => (
                  <div key={i} className="p-4" style={innerCard}>
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-semibold text-white">{c.name}</p>
                      <span className="text-xs font-bold text-brand-400">{Math.round(c.score * 100)}%</span>
                    </div>
                    <ScoreBar score={c.score} />
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-400">No specific conditions identified.</p>
            )}
          </div>

          <div className="space-y-4">
            <div className="p-6" style={cardStyle}>
              <h2 className="section-title mb-3 flex items-center gap-2">
                <svg className="h-4 w-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Explanation
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">{report.explanation}</p>
            </div>
            <div className="p-6" style={{ ...cardStyle, borderColor: 'rgba(22,189,202,0.2)' }}>
              <h2 className="section-title mb-3 flex items-center gap-2">
                <svg className="h-4 w-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recommendation
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">{report.recommendation}</p>
              {report.next_steps?.length > 0 && (
                <ul className="mt-3 space-y-1.5">
                  {report.next_steps.map((step, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="mt-0.5 h-4 w-4 shrink-0 rounded-full flex items-center justify-center text-xs font-bold"
                        style={{ background: 'rgba(6,148,162,0.25)', color: '#16bdca' }}>{i + 1}</span>
                      {step}
                    </li>
                  ))}
                </ul>
              )}
            </div>
            {report.disclaimer && (
              <div className="p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                <p className="text-xs text-slate-500 leading-relaxed">⚕️ {report.disclaimer}</p>
              </div>
            )}
          </div>
        </div>

        {/* Follow-up answers */}
        {Object.keys(followUpAnswers).length > 0 && (
          <div className="p-6" style={cardStyle}>
            <h2 className="section-title mb-4 flex items-center gap-2">
              <svg className="h-4 w-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              Follow-Up Answers
            </h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {Object.entries(followUpAnswers).map(([q, a]) => (
                <div key={q} className="p-4" style={innerCard}>
                  <p className="text-xs font-medium text-slate-400 mb-1">{q.replace(/_/g, ' ')}</p>
                  <p className="text-sm text-white font-medium">{String(a)}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-red-400"
            style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}>
            <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        {isSaved && (
          <div className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-emerald-400"
            style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)' }}>
            <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Report saved successfully to history.
          </div>
        )}

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button onClick={handleSave} disabled={loading || isSaved} className="btn-primary px-8 py-3.5">
            {loading ? (
              <><svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>Saving...</>
            ) : isSaved ? '✓ Saved' : (
              <><svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" /></svg>Save Report</>
            )}
          </button>
          <button onClick={() => navigate('/history')} className="btn-secondary px-6 py-3.5">View History</button>
          <button onClick={() => navigate('/symptom-form')} className="btn-secondary px-6 py-3.5">New Assessment</button>
        </div>
      </div>
    </PageShell>
  )
}
