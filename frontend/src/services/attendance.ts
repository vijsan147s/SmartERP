import api from './api'
import { Attendance, AttendanceCreate, PaginatedResponse, PaginationParams } from '../types'

export const attendanceApi = {
  getAttendance: (params?: PaginationParams) =>
    api.get<PaginatedResponse<Attendance>>('/attendance', { params }),

  createAttendance: (data: AttendanceCreate) =>
    api.post<Attendance>('/attendance', data),

  bulkCreateAttendance: (data: { date: string; records: AttendanceCreate[] }) =>
    api.post<Attendance[]>('/attendance/bulk', data),

  updateAttendance: (id: number, data: Partial<AttendanceCreate>) =>
    api.put<Attendance>(`/attendance/${id}`, data),

  getDailyAttendance: (params?: { date?: string }) =>
    api.get<Attendance[]>('/attendance/daily', { params }),

  getStudentStats: (studentId: number) =>
    api.get<any>(`/attendance/stats/student/${studentId}`),

  getEmployeeStats: (employeeId: number) =>
    api.get<any>(`/attendance/stats/employee/${employeeId}`),

  getMonthlyReport: (params?: { month?: number; year?: number }) =>
    api.get<any[]>('/attendance/report/monthly', { params }),

  getMyStats: () =>
    api.get<any>('/attendance/me/stats'),
}
