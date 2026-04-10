import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey || !supabaseUrl.startsWith('https://')) {
  throw new Error(
    'Invalid or missing VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY in frontend .env. ' +
    'Replace placeholder values with your real Supabase project URL and anon key.'
  )
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
