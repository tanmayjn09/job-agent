import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { candidatesApi } from '../utils/api'
import { getCandidateIdInt as getCandidateId } from "../utils/candidate"

export default function Profile() {
  const candidateId = getCandidateIdInt()
  const navigate = useNavigate()
  const [candidate, setCandidate] = useState(null)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [editingSection, setEditingSection] = useState(null)

  useEffect(() => {
    candidatesApi.get(candidateId).then(res => {
      setCandidate(res.data)
      try { setProfile(JSON.parse(res.data.profile_json)) } catch {}
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [candidateId])

  const saveProfile = async () => {
    setSaving(true)
    try {
      await candidatesApi.update(candidateId, { profile_json: JSON.stringify(profile) })
      setEditingSection(null)
    } finally {
      setSaving(false)
    }
  }

  const addSkill = (category, value) => {
    if (!value.trim()) return
    setProfile(p => ({ ...p, skills: { ...p.skills, [category]: [...(p.skills[category] || []), value.trim()] } }))
  }

  const removeSkill = (category, idx) => {
    setProfile(p => ({ ...p, skills: { ...p.skills, [category]: p.skills[category].filter((_, i) => i !== idx) } }))
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full" />
    </div>
  )

  if (!profile) return (
    <div className="min-h-screen flex items-center justify-center text-gray-400">Profile not found</div>
  )

  return (
    <div className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">{profile.name || 'Your Profile'}</h1>
            <p className="text-gray-400 text-sm mt-0.5">{profile.current_title} · {profile.years_experience} years experience</p>
          </div>
          <button onClick={() => navigate("/jobs")}
            className="bg-brand-500 hover:bg-brand-600 text-white font-medium px-6 py-2.5 rounded-xl transition-colors">
            Find Jobs →
          </button>
        </div>

        <div className="space-y-4">
          {/* Summary */}
          {profile.summary && (
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-700 mb-2">Summary</h3>
              <p className="text-sm text-gray-600 leading-relaxed">{profile.summary}</p>
            </div>
          )}

          {/* Strong Areas */}
          {profile.strong_areas?.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-700 mb-3">Strong Areas</h3>
              <div className="flex flex-wrap gap-2">
                {profile.strong_areas.map((area, i) => (
                  <span key={i} className="bg-brand-50 text-brand-600 text-sm px-3 py-1 rounded-full font-medium">{area}</span>
                ))}
              </div>
            </div>
          )}

          {/* Skills */}
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-700">Skills</h3>
              <button onClick={() => setEditingSection(editingSection === 'skills' ? null : 'skills')}
                className="text-sm text-brand-500 hover:text-brand-600">
                {editingSection === 'skills' ? 'Done' : 'Edit'}
              </button>
            </div>
            {['technical', 'tools', 'soft'].map(cat => (
              profile.skills?.[cat]?.length > 0 && (
                <div key={cat} className="mb-3">
                  <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">{cat}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.skills[cat].map((skill, i) => (
                      <span key={i} className="bg-gray-100 text-gray-700 text-sm px-2.5 py-1 rounded-full flex items-center gap-1">
                        {skill}
                        {editingSection === 'skills' && (
                          <button onClick={() => removeSkill(cat, i)} className="text-red-400 hover:text-red-600 text-xs">×</button>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              )
            ))}
            {editingSection === 'skills' && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <button onClick={saveProfile} disabled={saving}
                  className="w-full bg-brand-500 hover:bg-brand-600 text-white text-sm py-2 rounded-lg transition-colors">
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            )}
          </div>

          {/* Experience */}
          <div className="bg-white rounded-xl border border-gray-100 p-5">
            <h3 className="font-semibold text-gray-700 mb-4">Experience</h3>
            <div className="space-y-5">
              {profile.experience?.map((exp, i) => (
                <div key={i} className="border-l-2 border-gray-100 pl-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{exp.title}</p>
                      <p className="text-sm text-gray-500">{exp.company}{exp.location ? ` · ${exp.location}` : ''}</p>
                    </div>
                    <p className="text-xs text-gray-400 whitespace-nowrap ml-4">{exp.start_date} - {exp.end_date || 'Present'}</p>
                  </div>
                  {exp.bullets?.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {exp.bullets.map((b, j) => <li key={j} className="text-sm text-gray-600 flex gap-2"><span className="text-gray-300 mt-1">•</span>{b}</li>)}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Achievements */}
          {profile.achievements?.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-700 mb-3">Key Achievements</h3>
              <ul className="space-y-1.5">
                {profile.achievements.map((ach, i) => (
                  <li key={i} className="text-sm text-gray-600 flex gap-2"><span className="text-green-500">✓</span>{ach}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Education */}
          {profile.education?.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-700 mb-3">Education</h3>
              {profile.education.map((edu, i) => (
                <div key={i}>
                  <p className="font-medium text-gray-900">{edu.degree}{edu.field ? ` in ${edu.field}` : ''}</p>
                  <p className="text-sm text-gray-500">{edu.institution}{edu.year ? ` · ${edu.year}` : ''}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <button onClick={() => navigate("/dashboard")}
            className="flex-1 border border-gray-200 text-gray-600 font-medium py-3 rounded-xl hover:bg-gray-50 transition-colors">
            Dashboard
          </button>
          <button onClick={() => navigate("/jobs")}
            className="flex-1 bg-brand-500 hover:bg-brand-600 text-white font-medium py-3 rounded-xl transition-colors">
            Find Jobs →
          </button>
        </div>
      </div>
    </div>
  )
}
