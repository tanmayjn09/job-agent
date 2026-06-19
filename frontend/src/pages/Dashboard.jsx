import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { candidatesApi, jobsApi, resumesApi } from '../utils/api'
import { getCandidateIdInt, clearCandidateId } from '../utils/candidate'

function StatCard({ label, value, sub, color = 'text-gray-900' }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5">
      <p className={`text-3xl font-bold ${color}`}>{value}</p>
      <p className="text-sm font-medium text-gray-700 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const candidateId = getCandidateIdInt()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [candidate, setCandidate] = useState(null)
  const [matches, setMatches] = useState([])
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (!candidateId) { clearCandidateId(); navigate('/', { replace: true }); return }

    Promise.all([
      candidatesApi.get(candidateId),
      jobsApi.saved(candidateId),
      candidatesApi.dashboard(candidateId).catch(() => null),
    ]).then(([candRes, matchesRes, dashRes]) => {
      setCandidate(candRes.data)
      try { setProfile(JSON.parse(candRes.data.profile_json || '{}')) } catch {}
      setMatches(matchesRes.data.matches || [])
      if (dashRes?.data?.recent_resumes) setResumes(dashRes.data.recent_resumes)
      setLoading(false)
    }).catch(() => { clearCandidateId(); navigate('/', { replace: true }) })
  }, [candidateId])

  const handleApplyToggle = async (matchId, currentVal) => {
    try {
      const res = await jobsApi.toggleApply(matchId)
      setMatches(prev => prev.map(m => m.id === matchId ? { ...m, is_applied: res.data.is_applied } : m))
    } catch {}
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
    </div>
  )

  const appliedMatches = matches.filter(m => m.is_applied)
  const unappliedMatches = matches.filter(m => !m.is_applied)
  const topMatches = unappliedMatches.slice(0, 6)
  const avgScore = matches.length ? Math.round(matches.reduce((s, m) => s + m.match_score, 0) / matches.length) : 0

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'applied', label: `Applied (${appliedMatches.length})` },
    { id: 'matches', label: `All Matches (${matches.length})` },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">{profile?.name || candidate?.name || 'Dashboard'}</h1>
            <p className="text-gray-400 text-sm mt-0.5">{profile?.current_title}</p>
          </div>
          <button onClick={() => navigate("/jobs")}
            className="bg-brand-500 hover:bg-brand-600 text-white font-medium px-5 py-2.5 rounded-xl transition-colors">
            Search Jobs
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatCard label="Total Matches" value={matches.length} sub="jobs scored" />
          <StatCard label="Applied" value={appliedMatches.length} sub="jobs applied to" color="text-green-600" />
          <StatCard label="Not Applied" value={unappliedMatches.length} sub="still to review" />
          <StatCard label="Avg Match" value={`${avgScore}%`} sub="fit score" color={avgScore >= 70 ? 'text-green-600' : avgScore >= 50 ? 'text-yellow-600' : 'text-gray-900'} />
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6 w-fit">
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-4 py-2 text-sm rounded-lg transition-colors ${activeTab === t.id ? 'bg-white shadow-sm font-medium' : 'text-gray-500 hover:text-gray-700'}`}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Applied jobs */}
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-700">Applied Jobs</h3>
                {appliedMatches.length > 0 && (
                  <button onClick={() => setActiveTab('applied')} className="text-sm text-brand-500 hover:text-brand-600">View all</button>
                )}
              </div>
              {appliedMatches.length === 0 ? (
                <p className="text-gray-400 text-sm py-4 text-center">No applications yet. Mark jobs as applied from the search page.</p>
              ) : (
                <div className="space-y-2">
                  {appliedMatches.slice(0, 5).map(m => (
                    <div key={m.id} className="flex items-center justify-between py-2.5 border-b border-gray-50 last:border-0">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{m.job?.title}</p>
                        <p className="text-xs text-gray-400">{m.job?.company}{m.job?.location ? ` · ${m.job.location}` : ''}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`text-sm font-semibold ${m.match_score >= 75 ? 'text-green-600' : m.match_score >= 50 ? 'text-yellow-600' : 'text-red-500'}`}>
                          {Math.round(m.match_score)}%
                        </span>
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Applied</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Top unaplied matches */}
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-700">Top Matches — Not Applied Yet</h3>
                <button onClick={() => navigate('/jobs')} className="text-sm text-brand-500 hover:text-brand-600">View all</button>
              </div>
              {topMatches.length === 0 ? (
                <p className="text-gray-400 text-sm py-4 text-center">
                  {matches.length === 0 ? 'Search for jobs to get started.' : 'You\'ve applied to all your top matches!'}
                </p>
              ) : (
                <div className="space-y-2">
                  {topMatches.map(m => (
                    <div key={m.id} className="flex items-center justify-between py-2.5 border-b border-gray-50 last:border-0">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{m.job?.title}</p>
                        <p className="text-xs text-gray-400">{m.job?.company}{m.job?.location ? ` · ${m.job.location}` : ''}</p>
                      </div>
                      <div className="flex items-center gap-2 ml-3">
                        <span className={`text-sm font-semibold ${m.match_score >= 75 ? 'text-green-600' : m.match_score >= 50 ? 'text-yellow-600' : 'text-red-500'}`}>
                          {Math.round(m.match_score)}%
                        </span>
                        <button onClick={() => handleApplyToggle(m.id, m.is_applied)}
                          className="text-xs border border-gray-200 text-gray-500 px-2 py-0.5 rounded-full hover:bg-green-50 hover:border-green-200 hover:text-green-600 transition-colors">
                          Mark Applied
                        </button>
                        <button onClick={() => navigate(`/resume/${m.job?.id}`)}
                          className="text-xs bg-brand-500 text-white px-2 py-0.5 rounded-full hover:bg-brand-600">
                          Tailor
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Resumes */}
            {resumes.length > 0 && (
              <div className="bg-white rounded-xl border border-gray-100 p-5">
                <h3 className="font-semibold text-gray-700 mb-4">Generated Resumes</h3>
                <div className="space-y-2">
                  {resumes.slice(0, 5).map(r => (
                    <div key={r.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                      <div>
                        <p className="text-sm font-medium text-gray-900">{r.job_title}</p>
                        <p className="text-xs text-gray-400">{r.company}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${r.status === 'complete' ? 'bg-green-50 text-green-600' : 'bg-yellow-50 text-yellow-600'}`}>
                          {r.status}
                        </span>
                        {r.pdf_ready && (
                          <a href={resumesApi.downloadUrl(r.id)} download className="text-xs text-brand-500 hover:text-brand-600">PDF</a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Applied Tab */}
        {activeTab === 'applied' && (
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="font-semibold text-gray-700 mb-4">All Applied Jobs ({appliedMatches.length})</h3>
            {appliedMatches.length === 0 ? (
              <p className="text-gray-400 text-sm py-8 text-center">No applications yet.</p>
            ) : (
              <div className="space-y-2">
                {appliedMatches.map(m => (
                  <div key={m.id} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{m.job?.title}</p>
                      <p className="text-xs text-gray-400">{m.job?.company}{m.job?.location ? ` · ${m.job.location}` : ''}</p>
                      {m.applied_at && (
                        <p className="text-xs text-gray-300 mt-0.5">Applied {new Date(m.applied_at).toLocaleDateString()}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-3 ml-3">
                      <span className={`text-sm font-semibold ${m.match_score >= 75 ? 'text-green-600' : m.match_score >= 50 ? 'text-yellow-600' : 'text-red-500'}`}>
                        {Math.round(m.match_score)}%
                      </span>
                      <button onClick={() => handleApplyToggle(m.id, m.is_applied)}
                        className="text-xs border border-red-100 text-red-400 px-2 py-0.5 rounded-full hover:bg-red-50 transition-colors">
                        Undo
                      </button>
                      {m.job?.url && (
                        <a href={m.job.url} target="_blank" rel="noopener noreferrer"
                          className="text-xs text-brand-500 hover:text-brand-600">View</a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* All Matches Tab */}
        {activeTab === 'matches' && (
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="font-semibold text-gray-700 mb-4">All Matches ({matches.length})</h3>
            {matches.length === 0 ? (
              <p className="text-gray-400 text-sm py-8 text-center">No matches yet. <button onClick={() => navigate('/jobs')} className="text-brand-500">Search for jobs →</button></p>
            ) : (
              <div className="space-y-2">
                {[...matches].sort((a, b) => b.match_score - a.match_score).map(m => (
                  <div key={m.id} className={`flex items-center justify-between py-3 border-b border-gray-50 last:border-0 ${m.is_applied ? 'opacity-60' : ''}`}>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-gray-900 truncate">{m.job?.title}</p>
                        {m.is_applied && <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full shrink-0">Applied</span>}
                      </div>
                      <p className="text-xs text-gray-400">{m.job?.company}{m.job?.location ? ` · ${m.job.location}` : ''}</p>
                    </div>
                    <div className="flex items-center gap-3 ml-3">
                      <span className={`text-sm font-semibold ${m.match_score >= 75 ? 'text-green-600' : m.match_score >= 50 ? 'text-yellow-600' : 'text-red-500'}`}>
                        {Math.round(m.match_score)}%
                      </span>
                      <button onClick={() => handleApplyToggle(m.id, m.is_applied)}
                        className={`text-xs border px-2 py-0.5 rounded-full transition-colors ${m.is_applied ? 'border-red-100 text-red-400 hover:bg-red-50' : 'border-gray-200 text-gray-500 hover:bg-green-50 hover:border-green-200 hover:text-green-600'}`}>
                        {m.is_applied ? 'Undo' : 'Mark Applied'}
                      </button>
                      <button onClick={() => navigate(`/resume/${m.job?.id}`)}
                        className="text-xs bg-brand-500 text-white px-2 py-0.5 rounded-full hover:bg-brand-600">
                        Tailor
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="flex gap-3 mt-6">
          <button onClick={() => navigate("/profile")}
            className="flex-1 border border-gray-200 text-gray-600 font-medium py-3 rounded-xl hover:bg-gray-50 transition-colors">
            My Profile
          </button>
          <button onClick={() => navigate("/jobs")}
            className="flex-1 bg-brand-500 hover:bg-brand-600 text-white font-medium py-3 rounded-xl transition-colors">
            Search Jobs →
          </button>
        </div>
      </div>
    </div>
  )
}
