const KEY = 'candidate_id'

export const getCandidateId = () => localStorage.getItem(KEY)
export const setCandidateId = (id) => localStorage.setItem(KEY, String(id))
export const clearCandidateId = () => localStorage.removeItem(KEY)
