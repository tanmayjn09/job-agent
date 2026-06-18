import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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
}

export const resumesApi = {
  tailor: (candidateId, jobId) => api.post('/resumes/tailor', { candidate_id: candidateId, job_id: jobId }),
  get: (id) => api.get(`/resumes/${id}`),
  downloadUrl: (id) => `/api/resumes/${id}/download`,
}

export default api
