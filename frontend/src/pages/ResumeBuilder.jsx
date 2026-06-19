import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { resumesApi, jobsApi } from '../utils/api'
import { getCandidateIdInt } from '../utils/candidate'

export default function ResumeBuilder() {
  const { jobId } = useParams()
  const candidateId = getCandidateIdInt()
  const navigate = useNavigate()

  useEffect(() => {
    if (!candidateId) navigate('/', { replace: true })
  }, [])
  const [job, setJob] = useState(null)
  const [resume, setResume] = useState(null)
  const [resumeContent, setResumeContent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('preview')
  const [pastedDescription, setPastedDescription] = useState('')

  useEffect(() => {
    jobsApi.get(jobId, candidateId).then(res => {
      setJob(res.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [jobId, candidateId])

  const generate = async () => {
    setGenerating(true)
    setError('')
    try {
      const res = await resumesApi.tailor(candidateId, parseInt(jobId), pastedDescription || null)
      setResume(res.data)
      try { setResumeContent(JSON.parse(res.data.content_json)) } catch {}
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate resume. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  const keywords = resume ? (() => {
    try { const k = JSON.parse(resume.ats_keywords || '{}'); return [...(k.required_keywords || []), ...(k.preferred_keywords || [])] } catch { return [] }
  })() : []

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <button onClick={() => navigate(-1)}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1">
            ← Back to jobs
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-bold">{job?.job?.title}</h1>
            <p className="text-gray-400 text-sm">{job?.job?.company}{job?.job?.location ? ` · ${job?.job?.location}` : ''}</p>
          </div>
          {resume?.pdf_ready && (
            <a href={resumesApi.downloadUrl(resume.id)} download
              className="bg-green-500 hover:bg-green-600 text-white font-medium px-6 py-2.5 rounded-xl transition-colors flex items-center gap-2">
              ↓ Download PDF
            </a>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Job Details */}
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="font-semibold text-gray-700 mb-3">Job Description</h3>
            {job?.match && (
              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl font-bold text-brand-500">{Math.round(job.match.match_score)}%</span>
                  <span className="text-sm text-gray-500">match score</span>
                </div>
                {job.match.skill_matches?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {job.match.skill_matches.slice(0, 6).map((s, i) => (
                      <span key={i} className="text-xs bg-green-50 text-green-700 px-2 py-0.5 rounded-full">{s}</span>
                    ))}
                  </div>
                )}
              </div>
            )}
            <div
              className="text-sm text-gray-600 leading-relaxed max-h-96 overflow-y-auto [&_p]:mb-2 [&_strong]:font-semibold [&_ul]:list-disc [&_ul]:pl-4 [&_li]:mb-1 [&_h3]:font-semibold [&_h3]:mt-2"
              dangerouslySetInnerHTML={{
                __html: (job?.job?.description || '<span style="color:#9ca3af">Description will be fetched automatically when you generate the resume.</span>')
                  .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
              }}
            />
            {job?.job?.url && (
              <a href={job.job.url} target="_blank" rel="noopener noreferrer"
                className="text-brand-500 hover:text-brand-600 text-sm mt-3 block">
                View original posting →
              </a>
            )}
          </div>

          {/* Right: Resume */}
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            {!resume && !generating && (
              <div className="flex flex-col items-center justify-center h-full py-12">
                <div className="text-5xl mb-4">✨</div>
                <h3 className="font-semibold text-gray-800 mb-2">Generate Tailored Resume</h3>
                <p className="text-gray-400 text-sm text-center max-w-xs mb-6">
                  Claude will rewrite your resume with ATS-optimized language specific to this job.
                </p>
                {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
                <button onClick={generate}
                  className="bg-brand-500 hover:bg-brand-600 text-white font-medium px-8 py-3 rounded-xl transition-colors">
                  Generate Resume
                </button>
              </div>
            )}

            {generating && (
              <div className="flex flex-col items-center justify-center h-full py-12">
                <svg className="animate-spin w-10 h-10 text-brand-500 mb-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                <p className="font-medium text-gray-700">Tailoring your resume...</p>
                <p className="text-sm text-gray-400 mt-1">Extracting keywords, rewriting bullets, optimizing for ATS</p>
              </div>
            )}

            {resume && resumeContent && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex gap-1 bg-gray-100 rounded-lg p-0.5">
                    {['preview', 'keywords'].map(tab => (
                      <button key={tab} onClick={() => setActiveTab(tab)}
                        className={`px-3 py-1.5 text-sm rounded-md transition-colors capitalize ${activeTab === tab ? 'bg-white shadow-sm font-medium' : 'text-gray-500'}`}>
                        {tab}
                      </button>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={generate} className="text-xs text-gray-400 hover:text-gray-600">Regenerate</button>
                    {resume.pdf_ready && (
                      <a href={resumesApi.downloadUrl(resume.id)} download
                        className="text-xs text-brand-500 hover:text-brand-600 font-medium">Download PDF</a>
                    )}
                  </div>
                </div>

                {activeTab === 'preview' && (
                  <div className="max-h-[600px] overflow-y-auto text-sm space-y-4">
                    {resumeContent.summary && (
                      <div>
                        <h4 className="font-bold text-xs text-gray-400 uppercase tracking-wider mb-1">Summary</h4>
                        <p className="text-gray-700 leading-relaxed">{resumeContent.summary}</p>
                      </div>
                    )}

                    {resumeContent.experience?.map((exp, i) => (
                      <div key={i}>
                        <h4 className="font-bold text-xs text-gray-400 uppercase tracking-wider mb-2">
                          {i === 0 ? 'Experience' : ''}
                        </h4>
                        <div className="border-l-2 border-gray-100 pl-3">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="font-semibold text-gray-900">{exp.title}</p>
                              <p className="text-gray-500 text-xs">{exp.company} · {exp.start_date} - {exp.end_date || 'Present'}</p>
                            </div>
                          </div>
                          <ul className="mt-1 space-y-1">
                            {exp.bullets?.map((b, j) => (
                              <li key={j} className="text-gray-600 flex gap-2"><span className="text-gray-300">•</span>{b}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ))}

                    {resumeContent.skills && (
                      <div>
                        <h4 className="font-bold text-xs text-gray-400 uppercase tracking-wider mb-2">Skills</h4>
                        {resumeContent.skills.technical?.length > 0 && (
                          <p className="text-gray-600 mb-1"><strong>Technical:</strong> {resumeContent.skills.technical.join(', ')}</p>
                        )}
                        {resumeContent.skills.tools?.length > 0 && (
                          <p className="text-gray-600 mb-1"><strong>Tools:</strong> {resumeContent.skills.tools.join(', ')}</p>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'keywords' && (
                  <div>
                    <p className="text-sm text-gray-500 mb-3">Keywords from the JD included in your resume:</p>
                    <div className="flex flex-wrap gap-2">
                      {keywords.map((kw, i) => (
                        <span key={i} className="bg-brand-50 text-brand-600 text-sm px-3 py-1 rounded-full">{kw}</span>
                      ))}
                    </div>
                    {resumeContent.ats_score_estimate && (
                      <div className="mt-4 p-3 bg-green-50 rounded-lg">
                        <p className="text-sm font-medium text-green-700">Estimated ATS score: {resumeContent.ats_score_estimate}%</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
