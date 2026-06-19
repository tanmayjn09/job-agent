import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import JobCard from '../components/JobCard'
import { jobsApi, candidatesApi } from '../utils/api'
import { getCandidateIdInt, clearCandidateId } from '../utils/candidate'

const DATE_OPTIONS = [
  { value: 'all', label: 'All time' },
  { value: '24h', label: 'Last 24 hours' },
  { value: 'week', label: 'Last week' },
  { value: 'month', label: 'Last month' },
]

const COMPANY_TYPE_OPTIONS = [
  { value: '', label: 'Any' },
  { value: 'product', label: 'Product' },
  { value: 'service', label: 'Service/IT' },
  { value: 'startup', label: 'Startup' },
]

const CITY_SUGGESTIONS = [
  'Bengaluru', 'Mumbai', 'Delhi', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata', 'Ahmedabad', 'Noida', 'Gurugram',
  'Singapore', 'London', 'New York', 'San Francisco', 'Austin', 'Seattle', 'Toronto', 'Berlin', 'Amsterdam', 'Dubai',
  'Remote', 'India', 'United States', 'United Kingdom',
]

function parsePostedAt(str) {
  if (!str) return 0
  const m = str.match(/(\d+)\s*(hour|day|week|month)/i)
  if (!m) return 0
  const n = parseInt(m[1])
  const u = m[2].toLowerCase()
  if (u.startsWith('hour')) return Date.now() - n * 3600000
  if (u.startsWith('day')) return Date.now() - n * 86400000
  if (u.startsWith('week')) return Date.now() - n * 604800000
  return Date.now() - n * 2592000000
}

export default function JobSearch() {
  const candidateId = getCandidateIdInt()
  const navigate = useNavigate()
  const cacheKey = `job_search_${candidateId}`

  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [candidate, setCandidate] = useState(null)

  const [filters, setFilters] = useState({
    query: '',
    locations: [],
    remote: null,
    date_posted: 'month',
    company_type: '',
    seniority: '',
    page: 1,
    per_page: 40,
  })
  const [locationInput, setLocationInput] = useState('')
  const [showCitySuggestions, setShowCitySuggestions] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [sortBy, setSortBy] = useState('match')

  useEffect(() => {
    // Restore cached search results if coming back from resume builder
    const cached = sessionStorage.getItem(cacheKey)
    if (cached) {
      try {
        const { savedFilters, savedMatches, savedSort } = JSON.parse(cached)
        setFilters(savedFilters)
        setMatches(savedMatches)
        setSortBy(savedSort || 'match')
        setHasSearched(true)
        return
      } catch {}
    }

    candidatesApi.get(candidateId).then(res => {
      setCandidate(res.data)
      try {
        const exp = JSON.parse(res.data.expectations_json || '{}')
        const prof = JSON.parse(res.data.profile_json || '{}')
        setFilters(f => ({
          ...f,
          query: exp.target_role || prof.current_title || '',
          locations: exp.locations || [],
          remote: exp.remote_preference === 'remote' ? true : null,
        }))
      } catch {}
    })
  }, [candidateId])

  const search = async () => {
    if (!candidateId) { clearCandidateId(); navigate('/', { replace: true }); return }
    setLoading(true)
    setError('')
    setHasSearched(true)
    sessionStorage.removeItem(cacheKey)
    try {
      const res = await jobsApi.search({ ...filters, candidate_id: parseInt(candidateId) })
      const results = res.data.matches || []
      setMatches(results)
      sessionStorage.setItem(cacheKey, JSON.stringify({ savedFilters: filters, savedMatches: results, savedSort: sortBy }))
    } catch (err) {
      const detail = err.response?.data?.detail || ''
      if (err.response?.status === 404 && detail.toLowerCase().includes('candidate')) {
        clearCandidateId()
        navigate('/', { replace: true })
        return
      }
      setError(detail || 'Search failed. Check your API keys and try again.')
    } finally {
      setLoading(false)
    }
  }

  const addLocation = () => {
    if (locationInput.trim() && !filters.locations.includes(locationInput.trim())) {
      setFilters(f => ({ ...f, locations: [...f.locations, locationInput.trim()] }))
      setLocationInput('')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Find Jobs</h1>
            <p className="text-gray-400 text-sm mt-0.5">AI-ranked by your fit score</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => navigate("/profile")}
              className="text-sm border border-gray-200 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-50">
              My Profile
            </button>
            <button onClick={() => navigate("/dashboard")}
              className="text-sm border border-gray-200 text-gray-600 px-4 py-2 rounded-lg hover:bg-gray-50">
              Dashboard
            </button>
          </div>
        </div>

        {/* Filter Bar */}
        <div className="bg-white rounded-xl border border-gray-100 p-4 mb-6 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-3">
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">Role / Keywords</label>
              <input value={filters.query} onChange={e => setFilters(f => ({ ...f, query: e.target.value }))}
                onKeyDown={e => e.key === 'Enter' && search()}
                placeholder="e.g. Product Manager, Backend Engineer"
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>

            <div className="relative">
              <label className="text-xs font-medium text-gray-500 block mb-1">Locations</label>
              <div className="flex gap-1">
                <input value={locationInput}
                  onChange={e => { setLocationInput(e.target.value); setShowCitySuggestions(true) }}
                  onKeyDown={e => { if (e.key === 'Enter') { addLocation(); setShowCitySuggestions(false) } }}
                  onFocus={() => setShowCitySuggestions(true)}
                  onBlur={() => setTimeout(() => setShowCitySuggestions(false), 150)}
                  placeholder="City, country..."
                  className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
                <button onClick={() => { addLocation(); setShowCitySuggestions(false) }} className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm">+</button>
              </div>
              {showCitySuggestions && (
                <div className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 max-h-48 overflow-y-auto">
                  {CITY_SUGGESTIONS
                    .filter(c => c.toLowerCase().includes(locationInput.toLowerCase()) && !filters.locations.includes(c))
                    .map(city => (
                      <button key={city} onMouseDown={() => {
                        setFilters(f => ({ ...f, locations: [...f.locations, city] }))
                        setLocationInput('')
                        setShowCitySuggestions(false)
                      }} className="w-full text-left px-3 py-2 text-sm hover:bg-gray-50">
                        {city}
                      </button>
                    ))}
                </div>
              )}
              {filters.locations.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {filters.locations.map((loc, i) => (
                    <span key={i} className="bg-brand-50 text-brand-600 text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
                      {loc}
                      <button onClick={() => setFilters(f => ({ ...f, locations: f.locations.filter((_, j) => j !== i) }))}>×</button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">Date Posted</label>
              <select value={filters.date_posted} onChange={e => setFilters(f => ({ ...f, date_posted: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500">
                {DATE_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
            <div>
              <label className="text-xs font-medium text-gray-500 block mb-1">Company Type</label>
              <div className="flex gap-1 flex-wrap">
                {COMPANY_TYPE_OPTIONS.map(opt => (
                  <button key={opt.value} onClick={() => setFilters(f => ({ ...f, company_type: opt.value }))}
                    className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${filters.company_type === opt.value ? 'bg-brand-500 text-white border-brand-500' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-end">
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" checked={filters.remote === true}
                  onChange={e => setFilters(f => ({ ...f, remote: e.target.checked ? true : null }))}
                  className="rounded border-gray-300 text-brand-500" />
                Remote only
              </label>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex-1" />
            <button onClick={search} disabled={loading}
              className="bg-brand-500 hover:bg-brand-600 disabled:opacity-60 text-white font-medium px-8 py-2 rounded-lg transition-colors flex items-center gap-2">
              {loading ? (
                <>
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  Searching & scoring...
                </>
              ) : 'Search Jobs'}
            </button>
          </div>
        </div>

        {/* Results */}
        {error && (
          <div className="bg-red-50 border border-red-100 text-red-600 rounded-xl p-4 mb-4 text-sm">{error}</div>
        )}

        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-100 p-5 animate-pulse">
                <div className="h-4 bg-gray-100 rounded w-3/4 mb-2" />
                <div className="h-3 bg-gray-100 rounded w-1/2 mb-4" />
                <div className="h-3 bg-gray-100 rounded w-full mb-2" />
                <div className="h-3 bg-gray-100 rounded w-5/6" />
                <div className="h-8 bg-gray-100 rounded-lg mt-4" />
              </div>
            ))}
          </div>
        )}

        {!loading && hasSearched && matches.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <div className="text-4xl mb-3">🔍</div>
            <p className="font-medium">No jobs found</p>
            <p className="text-sm mt-1">Try broader search terms or different locations</p>
          </div>
        )}

        {!loading && !hasSearched && (
          <div className="text-center py-16 text-gray-400">
            <div className="text-4xl mb-3">💼</div>
            <p className="font-medium">Ready to search</p>
            <p className="text-sm mt-1">Set your filters and hit Search to find your best-fit jobs</p>
          </div>
        )}

        {!loading && matches.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-gray-500">{matches.length} jobs found</p>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">Sort by:</span>
                <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                  className="text-sm border border-gray-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-brand-500">
                  <option value="match">Best match</option>
                  <option value="recent">Most recent</option>
                  <option value="company">Company A–Z</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[...matches].sort((a, b) => {
                if (sortBy === 'recent') return parsePostedAt(b.job?.posted_at) - parsePostedAt(a.job?.posted_at)
                if (sortBy === 'company') return (a.job?.company || '').localeCompare(b.job?.company || '')
                return b.match_score - a.match_score
              }).map(match => (
                <JobCard key={match.id} match={match} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
