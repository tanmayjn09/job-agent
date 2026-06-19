import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { candidatesApi, resumesApi } from '../utils/api'
import { getCandidateIdInt } from '../utils/candidate'

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5">
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      <p className="text-sm font-medium text-gray-700 mt-0.5">{label}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const candidateId = getCandidateIdInt()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!candidateId) { navigate('/', { replace: true }); return }
    candidatesApi.dashboard(candidateId).then(res => {
      setData(res.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [candidateId])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
    </div>
  )

  if (!data) return (
    <div className="min-h-screen flex items-center justify-center text-gray-400">Not found</div>
  )

  const profile = (() => {
    try { return JSON.parse(data.candidate.profile_json || '{}') } catch { return {} }
  })()

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">{data.candidate.name || 'Dashboard'}</h1>
            <p className="text-gray-400 text-sm">{profile.current_title}</p>
          </div>
          <button onClick={() => navigate("/jobs")}
            className="bg-brand-500 hover:bg-brand-600 text-white font-medium px-5 py-2.5 rounded-xl transition-colors">
            Search Jobs
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <StatCard label="Job Matches" value={data.total_job_matches} sub="jobs scored and ranked" />
          <StatCard label="Resumes Generated" value={data.total_resumes_generated} sub="tailored for specific jobs" />
          <StatCard label="Avg Match Score" value={`${data.avg_match_score}%`} sub="across all matched jobs" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Recent Matches */}
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-700">Recent Matches</h3>
              <button onClick={() => navigate("/jobs")}
                className="text-sm text-brand-500 hover:text-brand-600">View all</button>
            </div>
            {data.recent_matches.length === 0 ? (
              <p className="text-gray-400 text-sm py-4 text-center">No matches yet. Search for jobs to get started.</p>
            ) : (
              <div className="space-y-3">
                {data.recent_matches.map(m => (
                  <div key={m.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{m.job_title}</p>
                      <p className="text-xs text-gray-400">{m.company}</p>
                    </div>
                    <div className={`text-sm font-semibold ${m.match_score >= 75 ? 'text-green-600' : m.match_score >= 50 ? 'text-yellow-600' : 'text-red-500'}`}>
                      {Math.round(m.match_score)}%
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Generated Resumes */}
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="font-semibold text-gray-700 mb-4">Generated Resumes</h3>
            {data.recent_resumes.length === 0 ? (
              <p className="text-gray-400 text-sm py-4 text-center">No resumes yet. Click "Tailor Resume" on any job match.</p>
            ) : (
              <div className="space-y-3">
                {data.recent_resumes.map(r => (
                  <div key={r.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{r.job_title}</p>
                      <p className="text-xs text-gray-400">{r.company}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${r.status === 'complete' ? 'bg-green-50 text-green-600' : r.status === 'error' ? 'bg-red-50 text-red-600' : 'bg-yellow-50 text-yellow-600'}`}>
                        {r.status}
                      </span>
                      {r.pdf_ready && (
                        <a href={resumesApi.downloadUrl(r.id)} download
                          className="text-xs text-brand-500 hover:text-brand-600">PDF</a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Profile Summary */}
        <div className="mt-6 bg-white rounded-xl border border-gray-100 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-700">Profile Summary</h3>
            <button onClick={() => navigate("/profile")}
              className="text-sm text-brand-500 hover:text-brand-600">Edit profile</button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-lg font-bold text-gray-900">{profile.years_experience || 0}</p>
              <p className="text-xs text-gray-400">Years exp</p>
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{profile.skills?.technical?.length || 0}</p>
              <p className="text-xs text-gray-400">Technical skills</p>
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{profile.experience?.length || 0}</p>
              <p className="text-xs text-gray-400">Past roles</p>
            </div>
            <div>
              <p className="text-lg font-bold text-gray-900">{profile.strong_areas?.length || 0}</p>
              <p className="text-xs text-gray-400">Strong areas</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
