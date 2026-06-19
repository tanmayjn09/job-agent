import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
})

export const candidatesApi = {
  onboard: (formData) => api.post('/candidates/onboard', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  get: (id) => api.get(`/candidates/${id}`),
  update: (id, data) => api.patch(`/candidates/${id}`, data),
  dashboard: (id) => api.get(`/candidates/${id}/dashboard`),
}

export const jobsApi = {
  search: (filters) => api.post('/jobs/search', filters),
  get: (jobId, candidateId) => api.get(`/jobs/${jobId}?candidate_id=${candidateId}`),
  saved: (candidateId) => api.get(`/jobs/saved?candidate_id=${candidateId}`),
  toggleApply: (matchId) => api.patch(`/jobs/job-matches/${matchId}/apply`),
}

export const resumesApi = {
  tailor: (candidateId, jobId, extraDescription) => api.post('/resumes/tailor', { candidate_id: candidateId, job_id: jobId, extra_description: extraDescription || null }),
  get: (id) => api.get(`/resumes/${id}`),
  downloadUrl: (id) => `${BASE_URL}/resumes/${id}/download`,
}

export default api
