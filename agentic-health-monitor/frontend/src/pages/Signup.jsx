import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import PageShell from '../components/PageShell.jsx'
import { supabase } from '../lib/supabaseClient.js'

const cardStyle = { background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '1rem' }

function Field({ label, required, children }) {
  return (
    <label className="block">
      <span className="label-text mb-2 block">
        {label} {required && <span className="text-brand-400">*</span>}
      </span>
      {children}
    </label>
  )
}

export default function Signup() {
  const [form, setForm] = useState({ full_name: '', age: '', email: '', password: '' })
  const [isLoading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((c) => ({ ...c, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const { data, error: signUpError } = await supabase.auth.signUp({
      email: form.email,
      password: form.password,
    })

    if (signUpError) {
      setError(signUpError.message)
      setLoading(false)
      return
    }

    const userId = data.user?.id
    if (userId) {
      const { error: profileError } = await supabase
        .from('profiles')
        .insert({ id: userId, full_name: form.full_name, age: Number(form.age) })

      if (profileError) {
        setError(profileError.message)
        setLoading(false)
        return
      }
    }

    setSuccess(true)
    setLoading(false)
    setTimeout(() => navigate('/login'), 2500)
  }

  return (
    <PageShell title="Create Account" description="Sign up to start your AI-powered health assessments.">
      <div className="mx-auto max-w-md">
        <div className="p-8" style={cardStyle}>

          {success ? (
            <div className="flex flex-col items-center gap-4 py-6 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-full"
                style={{ background: 'rgba(6,148,162,0.15)', border: '1px solid rgba(22,189,202,0.3)' }}>
                <svg className="h-7 w-7 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="text-white font-semibold text-lg">Account created!</p>
                <p className="text-slate-400 text-sm mt-1">Check your email to confirm, then log in.</p>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <Field label="Full Name" required>
                <input
                  name="full_name" value={form.full_name} onChange={handleChange}
                  required placeholder="Enter your full name" className="input-field"
                />
              </Field>

              <Field label="Age" required>
                <input
                  type="number" name="age" value={form.age} onChange={handleChange}
                  required min="1" max="120" placeholder="e.g. 28" className="input-field"
                />
              </Field>

              <Field label="Email" required>
                <input
                  type="email" name="email" value={form.email} onChange={handleChange}
                  required placeholder="you@example.com" className="input-field"
                />
              </Field>

              <Field label="Password" required>
                <input
                  type="password" name="password" value={form.password} onChange={handleChange}
                  required minLength={6} placeholder="Min. 6 characters" className="input-field"
                />
              </Field>

              {error && (
                <div className="flex items-center gap-3 rounded-xl px-4 py-3 text-sm text-red-400"
                  style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)' }}>
                  <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {error}
                </div>
              )}

              <button type="submit" disabled={isLoading} className="btn-primary w-full py-3.5">
                {isLoading ? (
                  <>
                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Creating account...
                  </>
                ) : 'Create Account'}
              </button>

              <p className="text-center text-sm text-slate-400">
                Already have an account?{' '}
                <Link to="/login" className="text-brand-400 hover:text-white transition-colors">Log in</Link>
              </p>
            </form>
          )}

        </div>
      </div>
    </PageShell>
  )
}
