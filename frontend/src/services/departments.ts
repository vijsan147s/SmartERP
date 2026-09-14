import api from './api'
import { Department, DepartmentCreate, PaginatedResponse, PaginationParams } from '../types'

export const departmentsApi = {
  getDepartments: (params?: PaginationParams) =>
    api.get<PaginatedResponse<Department>>('/departments', { params }),

  getAllDepartments: () =>
    api.get<Department[]>('/departments/all'),

  getDepartment: (id: number) =>
    api.get<Department>(`/departments/${id}`),

  createDepartment: (data: DepartmentCreate) =>
    api.post<Department>('/departments', data),

  updateDepartment: (id: number, data: Partial<DepartmentCreate>) =>
    api.put<Department>(`/departments/${id}`, data),

  deleteDepartment: (id: number) =>
    api.delete(`/departments/${id}`),
}
