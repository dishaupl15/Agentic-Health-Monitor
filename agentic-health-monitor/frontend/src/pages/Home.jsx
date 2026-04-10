import { Link } from 'react-router-dom'
import PageShell from '../components/PageShell.jsx'

const features = [
  { icon: '🧬', title: 'AI Symptom Analysis', desc: 'Advanced AI analyzes your symptoms and generates targeted follow-up questions.' },
  { icon: '📋', title: 'Smart Follow-Ups', desc: 'Dynamic questions adapt based on your reported symptoms for accurate assessment.' },
  { icon: '⚡', title: 'Instant Risk Report', desc: 'Get a detailed risk assessment with urgency level and medical recommendations.' },
  { icon: '📊', title: 'History Tracking', desc: 'All reports are saved so you can monitor health trends over time.' },
]

const steps = [
  { num: '01', title: 'Enter Symptoms', desc: 'Fill in your personal details, symptoms, and vitals.' },
  { num: '02', title: 'Answer Follow-Ups', desc: 'Respond to AI-generated questions for deeper analysis.' },
  { num: '03', title: 'Get Your Report', desc: 'Receive a full risk assessment with recommendations.' },
]

const cardStyle = { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '1rem' }

export default function Home() {
  return (
    <PageShell title="AI-Powered Health Assessment" description="Get an intelligent symptom analysis and personalized health report in minutes.">

      {/* Hero CTA */}
      <div className="relative overflow-hidden rounded-2xl p-8 mb-8"
        style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
        <div className="absolute inset-0 pointer-events-none rounded-2xl"
          style={{ background: 'linear-gradient(90deg, rgba(6,148,162,0.12) 0%, transparent 60%)' }} />
        <div className="relative flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">Ready to start your assessment?</h2>
            <p className="text-slate-400 text-sm max-w-lg">Our AI analyzes your symptoms using medical knowledge to provide accurate risk levels and actionable recommendations.</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 shrink-0">
            <Link to="/symptom-form" className="btn-primary whitespace-nowrap">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Start Assessment
            </Link>
            <Link to="/history" className="btn-secondary whitespace-nowrap">View History</Link>
          </div>
        </div>
      </div>

      {/* How it works */}
      <div className="mb-8">
        <h2 className="section-title mb-4">How it works</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {steps.map((step) => (
            <div key={step.num} className="relative overflow-hidden rounded-2xl p-6 transition-all duration-300 group"
              style={cardStyle}>
              <div className="absolute top-4 right-4 text-4xl font-black select-none"
                style={{ color: 'rgba(255,255,255,0.04)' }}>{step.num}</div>
              <div className="text-brand-400 text-2xl font-black mb-3">{step.num}</div>
              <h3 className="font-semibold text-white mb-1">{step.title}</h3>
              <p className="text-sm text-slate-400">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Features */}
      <div>
        <h2 className="section-title mb-4">Features</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <div key={f.title} className="glass-card-hover p-6">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-semibold text-white mb-1 text-sm">{f.title}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </PageShell>
  )
}
