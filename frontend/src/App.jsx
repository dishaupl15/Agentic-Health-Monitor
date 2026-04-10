import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'
import SymptomForm from './pages/SymptomForm.jsx'
import FollowUp from './pages/FollowUp.jsx'
import Report from './pages/Report.jsx'
import History from './pages/History.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/symptom-form" element={<SymptomForm />} />
      <Route path="/follow-up" element={<FollowUp />} />
      <Route path="/report" element={<Report />} />
      <Route path="/history" element={<History />} />
    </Routes>
  )
}
