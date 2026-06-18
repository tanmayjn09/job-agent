import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ProgressSteps from '../components/ProgressSteps'
import FileUpload from '../components/FileUpload'
import { candidatesApi } from '../utils/api'
import { setCandidateId } from '../utils/candidate'

const STEPS = ['Upload Resume', 'Add Context', 'Set Expectations']

const CITY_SUGGESTIONS = [
  'Bengaluru', 'Mumbai', 'Delhi', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata', 'Ahmedabad', 'Noida', 'Gurugram',
  'Singapore', 'London', 'New York', 'San Francisco', 'Austin', 'Seattle', 'Toronto', 'Berlin', 'Amsterdam', 'Dubai',
  'Remote', 'India', 'United States', 'United Kingdom',
]

const SENIORITY_OPTIONS = ['Internship', 'Entry Level', 'Mid Level', 'Senior', 'Lead', 'Manager', 'Director', 'VP', 'C-Level']
const REMOTE_OPTIONS = [
  { value: 'any', label: 'Any' },
  { value: 'remote', label: 'Remote only' },
  { value: 'hybrid', label: 'Hybrid' },
  { value: 'onsite', label: 'On-site only' },
]
const INDUSTRIES = ['Technology', 'Finance', 'Healthcare', 'E-commerce', 'SaaS', 'Consulting', 'Media', 'Education', 'Manufacturing', 'Government']

export default function Onboarding() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [resume, setResume] = useState(null)
  const [extraFiles, setExtraFiles] = useState([])
  const [githubUrl, setGithubUrl] = useState('')
  const [linkedinUrl, setLinkedinUrl] = useState('')
  const [portfolioUrl, setPortfolioUrl] = useState('')
  const [aboutText, setAboutText] = useState('')

  const [expectations, setExpectations] = useState({
    target_role: '',
    seniority: 'Mid Level',
    locations: [],
    salary_min: '',
    salary_max: '',
    remote_preference: 'any',
    industries: [],
    employment_types: ['full-time'],
  })
  const [locationInput, setLocationInput] = useState('')
  const [showLocationDrop, setShowLocationDrop] = useState(false)

  const addLocation = () => {
    if (locationInput.trim() && !expectations.locations.includes(locationInput.trim())) {
      setExpectations(e => ({ ...e, locations: [...e.locations, locationInput.trim()] }))
      setLocationInput('')
    }
  }

  const toggleIndustry = (ind) => {
    setExpectations(e => ({
      ...e,
      industries: e.industries.includes(ind) ? e.industries.filter(i => i !== ind) : [...e.industries, ind]
    }))
  }

  const handleSubmit = async () => {
    if (!resume) return setError('Please upload your resume')
    setLoading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('resume', resume)
      formData.append('expectations', JSON.stringify({
        ...expectations,
        salary_min: expectations.salary_min ? parseInt(expectations.salary_min) : null,
        salary_max: expectations.salary_max ? parseInt(expectations.salary_max) : null,
      }))
      if (githubUrl) formData.append('github_url', githubUrl)
      if (linkedinUrl) formData.append('linkedin_url', linkedinUrl)
      if (portfolioUrl) formData.append('portfolio_url', portfolioUrl)
      if (aboutText) formData.append('about_text', aboutText)
      extraFiles.forEach(f => formData.append('extra_files', f))

      const data = await candidatesApi.onboard(formData)
      setCandidateId(data.data.id)
      navigate('/profile')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process resume. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4">
      <div className="w-full max-w-2xl">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Job Agent</h1>
          <p className="text-gray-500 text-sm mt-1">AI-powered job search and resume tailoring</p>
        </div>

        <ProgressSteps steps={STEPS} current={step} />

        <div className="bg-white rounded-2xl border border-gray-100 p-8 shadow-sm">
          {step === 0 && (
            <div>
              <h2 className="text-lg font-semibold mb-1">Upload your resume</h2>
              <p className="text-gray-400 text-sm mb-6">We'll extract your profile and find jobs where you're the strongest candidate.</p>
              <FileUpload
                onFile={setResume}
                accept=".pdf,.doc,.docx,.txt"
                label="Drop your resume here"
                sublabel="PDF, Word, or text file"
              />
              {error && <p className="text-red-500 text-sm mt-3">{error}</p>}
              <button onClick={() => { if (!resume) { setError('Upload your resume first'); return; } setError(''); setStep(1) }}
                className="w-full mt-6 bg-brand-500 hover:bg-brand-600 text-white font-medium py-3 rounded-xl transition-colors">
                Continue
              </button>
            </div>
          )}

          {step === 1 && (
            <div>
              <h2 className="text-lg font-semibold mb-1">Add more context (optional)</h2>
              <p className="text-gray-400 text-sm mb-6">The more context you give, the better your matches.</p>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-1">About yourself</label>
                  <textarea
                    value={aboutText}
                    onChange={e => setAboutText(e.target.value)}
                    placeholder="Anything you want employers to know. Goals, preferences, what you're looking for next..."
                    rows={4}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-1">GitHub</label>
                    <input value={githubUrl} onChange={e => setGithubUrl(e.target.value)}
                      placeholder="github.com/username"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-1">LinkedIn</label>
                    <input value={linkedinUrl} onChange={e => setLinkedinUrl(e.target.value)}
                      placeholder="linkedin.com/in/username"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-1">Portfolio</label>
                    <input value={portfolioUrl} onChange={e => setPortfolioUrl(e.target.value)}
                      placeholder="yoursite.com"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-1">Additional files</label>
                  <FileUpload
                    onFile={setExtraFiles}
                    accept=".pdf,.doc,.docx,.txt,.md"
                    multiple
                    label="Projects, portfolios, case studies"
                    sublabel="Optional - any files that support your application"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button onClick={() => setStep(0)} className="flex-1 border border-gray-200 text-gray-600 font-medium py-3 rounded-xl hover:bg-gray-50 transition-colors">Back</button>
                <button onClick={() => setStep(2)} className="flex-1 bg-brand-500 hover:bg-brand-600 text-white font-medium py-3 rounded-xl transition-colors">Continue</button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-lg font-semibold mb-1">What are you looking for?</h2>
              <p className="text-gray-400 text-sm mb-6">This helps us narrow down the best-fit jobs for you.</p>

              <div className="space-y-5">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-1">Target role</label>
                    <input value={expectations.target_role} onChange={e => setExpectations(ex => ({ ...ex, target_role: e.target.value }))}
                      placeholder="e.g. Product Manager, Software Engineer"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-1">Seniority</label>
                    <select value={expectations.seniority} onChange={e => setExpectations(ex => ({ ...ex, seniority: e.target.value }))}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
                      {SENIORITY_OPTIONS.map(s => <option key={s}>{s}</option>)}
                    </select>
                  </div>
                </div>

                <div className="relative">
                  <label className="text-sm font-medium text-gray-700 block mb-1">Locations</label>
                  <div className="flex gap-2">
                    <input value={locationInput}
                      onChange={e => { setLocationInput(e.target.value); setShowLocationDrop(true) }}
                      onFocus={() => setShowLocationDrop(true)}
                      onBlur={() => setTimeout(() => setShowLocationDrop(false), 150)}
                      onKeyDown={e => { if (e.key === 'Enter') { addLocation(); setShowLocationDrop(false) } }}
                      placeholder="Type a city or country and press Enter"
                      className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                    <button onClick={() => { addLocation(); setShowLocationDrop(false) }} className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-lg">Add</button>
                  </div>
                  {showLocationDrop && (
                    <div className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 max-h-44 overflow-y-auto">
                      {CITY_SUGGESTIONS.filter(c => c.toLowerCase().includes(locationInput.toLowerCase()) && !expectations.locations.includes(c)).map(city => (
                        <button key={city} onMouseDown={() => {
                          setExpectations(e => ({ ...e, locations: [...e.locations, city] }))
                          setLocationInput('')
                          setShowLocationDrop(false)
                        }} className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50">{city}</button>
                      ))}
                    </div>
                  )}
                  {expectations.locations.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {expectations.locations.map((loc, i) => (
                        <span key={i} className="bg-brand-50 text-brand-600 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                          {loc}
                          <button onClick={() => setExpectations(e => ({ ...e, locations: e.locations.filter((_, j) => j !== i) }))} className="hover:text-red-500">×</button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-1">Work preference</label>
                  <div className="flex gap-2">
                    {REMOTE_OPTIONS.map(opt => (
                      <button key={opt.value} onClick={() => setExpectations(e => ({ ...e, remote_preference: opt.value }))}
                        className={`flex-1 py-2 text-sm rounded-lg border transition-colors ${expectations.remote_preference === opt.value ? 'bg-brand-500 text-white border-brand-500' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-1">Min salary (annual)</label>
                    <input value={expectations.salary_min} onChange={e => setExpectations(ex => ({ ...ex, salary_min: e.target.value }))}
                      type="number" placeholder="e.g. 80000"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700 block mb-1">Max salary</label>
                    <input value={expectations.salary_max} onChange={e => setExpectations(ex => ({ ...ex, salary_max: e.target.value }))}
                      type="number" placeholder="e.g. 120000"
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-2">Industries (select all that apply)</label>
                  <div className="flex flex-wrap gap-2">
                    {INDUSTRIES.map(ind => (
                      <button key={ind} onClick={() => toggleIndustry(ind)}
                        className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${expectations.industries.includes(ind) ? 'bg-brand-500 text-white border-brand-500' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                        {ind}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {error && <p className="text-red-500 text-sm mt-3">{error}</p>}

              <div className="flex gap-3 mt-6">
                <button onClick={() => setStep(1)} className="flex-1 border border-gray-200 text-gray-600 font-medium py-3 rounded-xl hover:bg-gray-50 transition-colors">Back</button>
                <button onClick={handleSubmit} disabled={loading}
                  className="flex-1 bg-brand-500 hover:bg-brand-600 disabled:opacity-60 text-white font-medium py-3 rounded-xl transition-colors flex items-center justify-center gap-2">
                  {loading ? (
                    <>
                      <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                      </svg>
                      Analyzing resume...
                    </>
                  ) : 'Build My Profile'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
