const KEY = 'candidate_id'

export const getCandidateId = () => localStorage.getItem(KEY)
export const setCandidateId = (id) => localStorage.setItem(KEY, String(id))
export const clearCandidateId = () => localStorage.removeItem(KEY)

// Returns integer or null
export const getCandidateIdInt = () => {
  const v = localStorage.getItem(KEY)
  const n = parseInt(v)
  return isNaN(n) ? null : n
}
