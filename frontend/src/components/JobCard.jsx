import { useNavigate } from 'react-router-dom'
import MatchScore from './MatchScore'

export default function JobCard({ match, candidateId }) {
  const navigate = useNavigate()
  const { job, match_score, match_reasoning, skill_matches, skill_gaps } = match

  const skillMatchList = (() => {
    try { return JSON.parse(skill_matches || '[]') } catch { return [] }
  })()
  const skillGapList = (() => {
    try { return JSON.parse(skill_gaps || '[]') } catch { return [] }
  })()

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{job.title}</h3>
          <p className="text-gray-500 text-sm mt-0.5">
            {job.company}{job.location ? ` · ${job.location}` : ''}
            {job.remote && <span className="ml-2 bg-blue-50 text-blue-600 text-xs px-2 py-0.5 rounded-full">Remote</span>}
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
