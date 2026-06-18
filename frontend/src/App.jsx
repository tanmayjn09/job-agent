import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Onboarding from './pages/Onboarding'
import Profile from './pages/Profile'
import JobSearch from './pages/JobSearch'
import ResumeBuilder from './pages/ResumeBuilder'
import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Onboarding />} />
        <Route path="/profile/:candidateId" element={<Profile />} />
        <Route path="/jobs/:candidateId" element={<JobSearch />} />
        <Route path="/resume/:candidateId/:jobId" element={<ResumeBuilder />} />
        <Route path="/dashboard/:candidateId" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
