const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const handleResponse = async (response) => {
  const json = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(json.message || response.statusText || 'API request failed')
  }
  return json
}

export const analyzeSymptoms = async (payload) => {
  const response = await fetch(`${API_URL}/analyze-symptoms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return handleResponse(response)
}

export const finalAssessment = async (payload) => {
  const response = await fetch(`${API_URL}/final-assessment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return handleResponse(response)
}

export const saveReport = async (payload) => {
  const response = await fetch(`${API_URL}/save-report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return handleResponse(response)
}

export const getHistory = async () => {
  const response = await fetch(`${API_URL}/history`)
  return handleResponse(response)
}
