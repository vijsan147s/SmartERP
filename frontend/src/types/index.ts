export interface Role {
  id: number
  name: string
}

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  phone?: string
  is_active: boolean
  is_superuser: boolean
  status: 'ACTIVE' | 'INACTIVE'
  roles: Role[]
  created_at: string
  updated_at: string
}

export interface Tokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginResponse {
  user: User
  tokens: Tokens
}

export interface LoginRequest {
  username: string
  password: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface PaginationParams {
  page?: number
  page_size?: number
  search?: string
  sort_by?: string
  sort_order?: string
}

export interface ApiError {
  detail?: string
  message?: string
  error_type?: string
}

export interface Department {
  id: number
  name: string
  code: string
  description?: string
  is_active: boolean
  student_count?: number
  employee_count?: number
  created_at: string
  updated_at: string
}

export interface DepartmentCreate {
  name: string
  code: string
  description?: string
}

export interface Student {
  id: number
  student_id: string
  user_id: number
  email: string
  username: string
  full_name: string
  phone?: string
  department_id?: number
  course: string
  semester: number
  enrollment_date: string
  date_of_birth?: string
  gender?: string
  address?: string
  emergency_contact?: string
  status: 'ACTIVE' | 'INACTIVE' | 'GRADUATED' | 'SUSPENDED'
  created_at: string
  updated_at: string
  department?: Department
}

export interface StudentCreate {
  student_id: string
  email: string
  username: string
  full_name: string
  phone?: string
  department_id?: number
  course: string
  semester: number
  enrollment_date: string
  date_of_birth?: string
  gender?: string
  address?: string
  emergency_contact?: string
  password: string
}

export interface Employee {
  id: number
  employee_id: string
  user_id: number
  email: string
  username: string
  full_name: string
  phone?: string
  department_id?: number
  designation: string
  joining_date: string
  salary: number
  date_of_birth?: string
  gender?: string
  address?: string
  emergency_contact?: string
  status: 'ACTIVE' | 'INACTIVE' | 'ON_LEAVE' | 'TERMINATED'
  created_at: string
  updated_at: string
  department?: Department
}

export interface EmployeeCreate {
  employee_id: string
  email: string
  username: string
  full_name: string
  phone?: string
  department_id?: number
  designation: string
  joining_date: string
  salary: number
  date_of_birth?: string
  gender?: string
  address?: string
  emergency_contact?: string
  password: string
}

export interface Attendance {
  id: number
  student_id?: number
  employee_id?: number
  date: string
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'EXCUSED'
  remarks?: string
  marked_by_id?: number
  student_name?: string
  employee_name?: string
  created_at: string
  updated_at: string
}

export interface AttendanceCreate {
  student_id?: number
  employee_id?: number
  date: string
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'EXCUSED'
  remarks?: string
}

export interface Fee {
  id: number
  student_id: number
  student_name?: string
  student_student_id?: string
  course?: string
  academic_year: string
  semester: number
  total_amount: number
  paid_amount: number
  pending_amount: number
  due_date?: string
  status: 'PENDING' | 'PARTIAL' | 'PAID'
  remarks?: string
  created_at: string
  updated_at: string
}

export interface FeeCreate {
  student_id: number
  academic_year: string
  semester: number
  total_amount: number
  due_date?: string
  remarks?: string
}

export interface FeeDashboardStats {
  total_fees: number
  total_collected: number
  total_pending: number
  collection_rate: number
  paid_count: number
  partial_count: number
  pending_count: number
}

export interface Payment {
  id: number
  fee_id: number
  amount: number
  payment_date: string
  payment_method: string
  transaction_id?: string
  receipt_number: string
  remarks?: string
  received_by_id?: number
  received_by_name?: string
  created_at: string
  updated_at: string
}

export interface PaymentCreate {
  fee_id: number
  amount: number
  payment_date: string
  payment_method: string
  transaction_id?: string
  receipt_number: string
  remarks?: string
}

export interface Subject {
  id: number
  code: string
  name: string
  department_id?: number
  department_name?: string
  credits: number
  max_internal_marks: number
  max_external_marks: number
  semester: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface SubjectCreate {
  code: string
  name: string
  department_id?: number
  credits: number
  max_internal_marks: number
  max_external_marks: number
  semester: number
}

export interface Result {
  id: number
  student_id: number
  subject_id: number
  internal_marks: number
  external_marks: number
  total_marks: number
  grade?: string
  is_passed: boolean
  semester: number
  exam_date?: string
  remarks?: string
  student_name?: string
  student_student_id?: string
  subject_name?: string
  subject_code?: string
  max_internal_marks: number
  max_external_marks: number
  created_at: string
  updated_at: string
}

export interface ResultCreate {
  student_id: number
  subject_id: number
  internal_marks: number
  external_marks: number
  semester: number
  exam_date?: string
  remarks?: string
}

export interface AttendanceStats {
  total_days: number
  present_days: number
  absent_days: number
  late_days: number
  excused_days: number
  attendance_percentage: number
  risk_level: string
}

export interface MonthlyAttendanceReport {
  month: number
  year: number
  department_id?: number
  department_name?: string
  total_students: number
  total_working_days: number
  average_attendance: number
  low_risk_count: number
  medium_risk_count: number
  high_risk_count: number
}

export interface DashboardStats {
  total_students: number
  total_employees: number
  attendance_rate: number
  pending_fees: number
  total_departments: number
  active_users: number
}

export interface DashboardResponse {
  stats: DashboardStats
  attendance_trend: Array<{
    month: string
    present: number
    absent: number
    late: number
    rate: number
  }>
  department_distribution: Array<{
    department_id: number
    department_name: string
    student_count: number
    employee_count: number
  }>
  fee_collection: Array<{
    month: string
    collected: number
    pending: number
  }>
  fee_status: {
    paid: number
    partial: number
    pending: number
  }
  employee_student_distribution: {
    employees: number
    students: number
  }
}

export interface StudentReportRow {
  student_id: string
  full_name: string
  email: string
  phone?: string
  department: string
  course: string
  semester: number
  enrollment_date: string
  status: string
  attendance_percentage?: number
  pending_fees?: number
}

export interface EmployeeReportRow {
  employee_id: string
  full_name: string
  email: string
  phone?: string
  department: string
  designation: string
  joining_date: string
  salary: number
  status: string
  attendance_percentage?: number
}

export interface AttendanceReportRow {
  date: string
  student_id?: string
  student_name?: string
  employee_id?: string
  employee_name?: string
  department: string
  status: string
  remarks?: string
}

export interface FeeReportRow {
  student_id: string
  student_name: string
  course: string
  academic_year: string
  semester: number
  total_amount: number
  paid_amount: number
  pending_amount: number
  due_date?: string
  status: string
  last_payment_date?: string
}

export interface DepartmentReportRow {
  department_id: number
  department_name: string
  department_code: string
  head_name?: string
  student_count: number
  employee_count: number
  avg_attendance?: number
  total_fees?: number
  collected_fees?: number
  status: string
}

export interface AcademicPerformanceRow {
  student_id: string
  student_name: string
  department: string
  course: string
  semester: number
  subject_code: string
  subject_name: string
  internal_marks: number
  external_marks: number
  total_marks: number
  grade?: string
  is_passed: boolean
}
