import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import MatchScore from './MatchScore'
import { jobsApi } from '../utils/api'

function formatPostedAt(raw) {
  if (!raw) return null
  if (/ago|hour|day|week|month|year/i.test(raw)) return raw
  const d = new Date(raw)
  if (isNaN(d)) return raw
  const days = Math.floor((Date.now() - d) / 86400000)
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days}d ago`
  if (days < 30) return `${Math.floor(days / 7)}w ago`
  if (days < 365) return `${Math.floor(days / 30)}mo ago`
  return `${Math.floor(days / 365)}y ago`
}

const SOURCE_LABELS = {
  google_jobs: { label: 'Google', color: 'bg-blue-50 text-blue-600' },
  linkedin: { label: 'LinkedIn', color: 'bg-sky-50 text-sky-700' },
  naukri: { label: 'Naukri', color: 'bg-orange-50 text-orange-600' },
  indeed: { label: 'Indeed', color: 'bg-indigo-50 text-indigo-600' },
  remotive: { label: 'Remotive', color: 'bg-purple-50 text-purple-600' },
  remoteok: { label: 'RemoteOK', color: 'bg-green-50 text-green-700' },
  weworkremotely: { label: 'WWR', color: 'bg-teal-50 text-teal-700' },
  wellfound: { label: 'Wellfound', color: 'bg-pink-50 text-pink-600' },
  yc_jobs: { label: 'YC', color: 'bg-amber-50 text-amber-700' },
  ycombinator: { label: 'YC', color: 'bg-amber-50 text-amber-700' },
  hackernews: { label: 'HN', color: 'bg-orange-50 text-orange-700' },
  greenhouse: { label: 'Greenhouse', color: 'bg-emerald-50 text-emerald-700' },
  lever: { label: 'Lever', color: 'bg-violet-50 text-violet-700' },
}

export default function JobCard({ match, onAppliedChange }) {
  const navigate = useNavigate()
  const { job, match_score, match_reasoning, skill_matches } = match
  const [isApplied, setIsApplied] = useState(Boolean(match.is_applied))
  const [applying, setApplying] = useState(false)

  const skillMatchList = (() => {
    try { return JSON.parse(skill_matches || '[]') } catch { return [] }
  })()

  const sourceInfo = SOURCE_LABELS[job.source] || { label: job.source || 'Job Board', color: 'bg-gray-100 text-gray-500' }
  const postedLabel = formatPostedAt(job.posted_at)

  const handleApply = async (e) => {
    e.stopPropagation()
    setApplying(true)
    try {
      const res = await jobsApi.toggleApply(match.id)
      const newVal = res.data.is_applied
      setIsApplied(newVal)
      onAppliedChange?.(match.id, newVal)
    } catch {}
    setApplying(false)
  }

  return (
    <div className={`bg-white border rounded-xl p-5 hover:shadow-md transition-shadow ${isApplied ? 'border-green-200 bg-green-50/30' : 'border-gray-100'}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5 flex-wrap">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sourceInfo.color}`}>{sourceInfo.label}</span>
            {job.remote && <span className="bg-blue-50 text-blue-600 text-xs px-2 py-0.5 rounded-full">Remote</span>}
            {isApplied && <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full font-medium">Applied</span>}
            {postedLabel && <span className="text-xs text-gray-400">{postedLabel}</span>}
          </div>
          <h3 className="font-semibold text-gray-900 truncate">{job.title}</h3>
          <p className="text-gray-500 text-sm mt-0.5">
            {job.company}{job.location ? ` · ${job.location}` : ''}
          </p>
        </div>
        <MatchScore score={match_score} />
      </div>

      {match_reasoning && (
        <p className="text-sm text-gray-600 mt-3 line-clamp-2">{match_reasoning}</p>
      )}

      {skillMatchList.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-3">
          {skillMatchList.slice(0, 4).map((s, i) => (
            <span key={i} className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full">{s}</span>
          ))}
          {skillMatchList.length > 4 && (
            <span className="text-xs text-gray-400">+{skillMatchList.length - 4} more</span>
          )}
        </div>
      )}

      <div className="flex gap-2 mt-4">
        <button
          onClick={() => navigate(`/resume/${job.id}`)}
          className="flex-1 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium py-2 rounded-lg transition-colors"
        >
          Tailor Resume
        </button>
        <button
          onClick={handleApply}
          disabled={applying}
          className={`px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${
            isApplied
              ? 'bg-green-50 border-green-200 text-green-700 hover:bg-red-50 hover:border-red-200 hover:text-red-600'
              : 'border-gray-200 text-gray-600 hover:bg-gray-50'
          }`}
        >
          {applying ? '...' : isApplied ? '✓ Applied' : 'Apply'}
        </button>
        {job.url && (
          <a href={job.url} target="_blank" rel="noopener noreferrer"
            className="px-3 py-2 border border-gray-200 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors">
            View
          </a>
        )}
      </div>
    </div>
  )
}
