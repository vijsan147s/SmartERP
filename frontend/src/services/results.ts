import api from './api'
import { Result, ResultCreate, Subject, SubjectCreate, PaginatedResponse, PaginationParams } from '../types'

export const resultsApi = {
  getResults: (params?: PaginationParams) =>
    api.get<PaginatedResponse<Result>>('/results', { params }),

  getResult: (id: number) =>
    api.get<Result>(`/results/${id}`),

  createResult: (data: ResultCreate) =>
    api.post<Result>('/results', data),

  updateResult: (id: number, data: Partial<ResultCreate>) =>
    api.put<Result>(`/results/${id}`, data),

  deleteResult: (id: number) =>
    api.delete(`/results/${id}`),

  getStudentSemesterResults: (studentId: number, semester: number) =>
    api.get<any>(`/results/student/${studentId}/semester/${semester}`),

  getMyResults: () =>
    api.get<Result[]>('/results/me/results'),

  getSubjects: (params?: PaginationParams) =>
    api.get<PaginatedResponse<Subject>>('/results/subjects', { params }),

  getSubject: (id: number) =>
    api.get<Subject>(`/results/subjects/${id}`),

  createSubject: (data: SubjectCreate) =>
    api.post<Subject>('/results/subjects', data),

  updateSubject: (id: number, data: Partial<SubjectCreate>) =>
    api.put<Subject>(`/results/subjects/${id}`, data),
}
