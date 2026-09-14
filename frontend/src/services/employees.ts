import api from './api'
import { Employee, EmployeeCreate, PaginatedResponse, PaginationParams } from '../types'

export const employeesApi = {
  getEmployees: (params?: PaginationParams) =>
    api.get<PaginatedResponse<Employee>>('/employees', { params }),

  getEmployee: (id: number) =>
    api.get<Employee>(`/employees/${id}`),

  createEmployee: (data: EmployeeCreate) =>
    api.post<Employee>('/employees', data),

  updateEmployee: (id: number, data: Partial<EmployeeCreate>) =>
    api.put<Employee>(`/employees/${id}`, data),

  deleteEmployee: (id: number) =>
    api.delete(`/employees/${id}`),

  getMyProfile: () =>
    api.get<Employee>('/employees/me/profile'),
}
