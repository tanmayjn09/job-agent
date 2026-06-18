import { useNavigate } from 'react-router-dom'
import MatchScore from './MatchScore'

function formatPostedAt(raw) {
  if (!raw) return null
  // Already a relative string like "3 days ago" or "1 week ago"
  if (/ago|hour|day|week|month|year/i.test(raw)) return raw
  // ISO date like "2024-05-10"
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
  hn_jobs: { label: 'HN', color: 'bg-orange-50 text-orange-700' },
  greenhouse: { label: 'Greenhouse', color: 'bg-emerald-50 text-emerald-700' },
  lever: { label: 'Lever', color: 'bg-violet-50 text-violet-700' },
}

export default function JobCard({ match, candidateId }) {
  const navigate = useNavigate()
  const { job, match_score, match_reasoning, skill_matches, skill_gaps } = match

  const skillMatchList = (() => {
    try { return JSON.parse(skill_matches || '[]') } catch { return [] }
  })()
  const skillGapList = (() => {
    try { return JSON.parse(skill_gaps || '[]') } catch { return [] }
  })()

  const sourceInfo = SOURCE_LABELS[job.source] || { label: job.source || 'Job Board', color: 'bg-gray-100 text-gray-500' }
  const postedLabel = formatPostedAt(job.posted_at)

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5 flex-wrap">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sourceInfo.color}`}>{sourceInfo.label}</span>
            {job.remote && <span className="bg-blue-50 text-blue-600 text-xs px-2 py-0.5 rounded-full">Remote</span>}
            {postedLabel && <span className="text-xs text-gray-400">{postedLabel}</span>}
          </div>
          <h3 className="font-semibold text-gray-900 truncate">{job.title}</h3>
          <p className="text-gray-500 text-sm mt-0.5">
            {job.company}{job.location ? ` · ${job.location}` : ''}
          </p>
          {job.employment_type && (
            <span className="text-xs text-gray-400 mt-1 block">{job.employment_type}</span>
          )}
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

      {skillGapList.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1">
          {skillGapList.slice(0, 2).map((s, i) => (
            <span key={i} className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full">Missing: {s}</span>
          ))}
        </div>
      )}

      <div className="flex gap-2 mt-4">
        <button
          onClick={() => navigate(`/resume/${candidateId}/${job.id}`)}
          className="flex-1 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium py-2 rounded-lg transition-colors"
        >
          Tailor Resume
        </button>
        {job.url && (
          <a href={job.url} target="_blank" rel="noopener noreferrer"
            className="px-4 py-2 border border-gray-200 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors">
            View Job
          </a>
        )}
      </div>
    </div>
  )
}
