import api from './api'
import {
  DashboardResponse,
  StudentReportRow,
  EmployeeReportRow,
  AttendanceReportRow,
  FeeReportRow,
  DepartmentReportRow,
  AcademicPerformanceRow,
} from '../types'

export const reportsApi = {
  getDashboard: () =>
    api.get<DashboardResponse>('/reports/dashboard'),

  getStudentsReport: (params?: { format?: string }) =>
    api.get<StudentReportRow[]>('/reports/students', { params }),

  getEmployeesReport: (params?: { format?: string }) =>
    api.get<EmployeeReportRow[]>('/reports/employees', { params }),

  getAttendanceReport: (params?: { date_from?: string; date_to?: string; format?: string }) =>
    api.get<AttendanceReportRow[]>('/reports/attendance', { params }),

  getFeesReport: (params?: { academic_year?: string; format?: string }) =>
    api.get<FeeReportRow[]>('/reports/fees', { params }),

  getDepartmentsReport: () =>
    api.get<DepartmentReportRow[]>('/reports/departments'),

  getAcademicReport: (params?: { semester?: number; format?: string }) =>
    api.get<AcademicPerformanceRow[]>('/reports/academic-performance', { params }),
}
