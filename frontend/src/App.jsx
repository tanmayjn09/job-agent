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
        <Route path="/profile" element={<Profile />} />
        <Route path="/jobs" element={<JobSearch />} />
        <Route path="/resume/:jobId" element={<ResumeBuilder />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
