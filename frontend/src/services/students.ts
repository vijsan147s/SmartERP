import api from './api'
import { Student, StudentCreate, PaginatedResponse, PaginationParams } from '../types'

export const studentsApi = {
  getStudents: (params?: PaginationParams) =>
    api.get<PaginatedResponse<Student>>('/students', { params }),

  getStudent: (id: number) =>
    api.get<Student>(`/students/${id}`),

  createStudent: (data: StudentCreate) =>
    api.post<Student>('/students', data),

  updateStudent: (id: number, data: Partial<StudentCreate>) =>
    api.put<Student>(`/students/${id}`, data),

  deleteStudent: (id: number) =>
    api.delete(`/students/${id}`),

  getMyProfile: () =>
    api.get<Student>('/students/me/profile'),
}
