import { useState, useEffect, useCallback } from 'react'
import { BarChart3, Download, TrendingUp, Users, GraduationCap, Award } from 'lucide-react'
import { reportsApi } from '@/services/reports'
import { PageHeader } from '@/components/common/PageHeader'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import type { DashboardResponse, StudentReportRow, EmployeeReportRow, AttendanceReportRow, FeeReportRow, AcademicPerformanceRow } from '@/types'

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'attendance' | 'fees' | 'results'>('overview')
  const [loading, setLoading] = useState(true)
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null)
  const [studentReport, setStudentReport] = useState<StudentReportRow[]>([])
  const [employeeReport, setEmployeeReport] = useState<EmployeeReportRow[]>([])
  const [attendanceReport, setAttendanceReport] = useState<AttendanceReportRow[]>([])
  const [feeReport, setFeeReport] = useState<FeeReportRow[]>([])
  const [academicReport, setAcademicReport] = useState<AcademicPerformanceRow[]>([])
  const { success, error: toastError } = useToast()

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true)
      const [dashRes, sRes, eRes, aRes, fRes, acRes] = await Promise.allSettled([
        reportsApi.getDashboard(),
        reportsApi.getStudentsReport(),
        reportsApi.getEmployeesReport(),
        reportsApi.getAttendanceReport(),
        reportsApi.getFeesReport(),
        reportsApi.getAcademicReport(),
      ])
      if (dashRes.status === 'fulfilled') setDashboard(dashRes.value.data)
      if (sRes.status === 'fulfilled') setStudentReport(sRes.value.data)
      if (eRes.status === 'fulfilled') setEmployeeReport(eRes.value.data)
      if (aRes.status === 'fulfilled') setAttendanceReport(aRes.value.data)
      if (fRes.status === 'fulfilled') setFeeReport(fRes.value.data)
      if (acRes.status === 'fulfilled') setAcademicReport(acRes.value.data)
    } catch {
      toastError('Failed to load report data')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchAll() }, [fetchAll])

  const handleExport = async (type: 'students' | 'employees' | 'attendance' | 'fees' | 'results') => {
    try {
      let res
      switch (type) {
        case 'students': res = await reportsApi.getStudentsReport({ format: 'csv' }); break
        case 'employees': res = await reportsApi.getEmployeesReport({ format: 'csv' }); break
        case 'attendance': res = await reportsApi.getAttendanceReport({ format: 'csv' }); break
        case 'fees': res = await reportsApi.getFeesReport({ format: 'csv' }); break
        case 'results': res = await reportsApi.getAcademicReport({ format: 'csv' }); break
      }
      if (res?.data) downloadCSV(res.data, `${type}_report.csv`)
      success(`Exported ${type} report`)
    } catch {
      toastError(`Failed to export ${type} report`)
    }
  }

  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'attendance', label: 'Attendance' },
    { key: 'fees', label: 'Fees' },
    { key: 'results', label: 'Results' },
  ] as const

  if (loading) return <PageLoader text="Loading reports..." />

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Reports"
        description="Analytics and report generation"
        action={
          <Button variant="outline" onClick={() => handleExport(activeTab === 'overview' ? 'students' : activeTab as any)}>
            <Download className="mr-2 h-4 w-4" /> Export CSV
          </Button>
        }
      />

      <div className="flex gap-1 rounded-lg border bg-muted p-1">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatBox icon={GraduationCap} label="Total Students" value={dashboard?.stats.total_students ?? 0} sub={`${dashboard?.employee_student_distribution?.students ?? 0} active`} color="bg-blue-500" />
            <StatBox icon={Users} label="Total Employees" value={dashboard?.stats.total_employees ?? 0} sub={`${dashboard?.employee_student_distribution?.employees ?? 0} active`} color="bg-emerald-500" />
            <StatBox icon={BarChart3} label="Departments" value={dashboard?.stats.total_departments ?? 0} sub="Total" color="bg-amber-500" />
            <StatBox icon={TrendingUp} label="Attendance Rate" value={`${dashboard?.stats.attendance_rate?.toFixed(1) ?? 0}%`} sub="This period" color="bg-purple-500" />
          </div>

          {dashboard?.department_distribution && dashboard.department_distribution.length > 0 && (
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="mb-4 font-semibold">Department Distribution</h3>
              <div className="space-y-3">
                {dashboard.department_distribution.map((dept) => {
                  const total = dept.student_count + dept.employee_count
                  const maxCount = Math.max(...dashboard.department_distribution.map(d => d.student_count + d.employee_count))
                  const width = maxCount > 0 ? (total / maxCount) * 100 : 0
                  return (
                    <div key={dept.department_id} className="flex items-center gap-4">
                      <span className="w-32 truncate text-sm text-muted-foreground">{dept.department_name}</span>
                      <div className="flex-1">
                        <div className="h-2.5 rounded-full bg-muted">
                          <div className="h-2.5 rounded-full bg-primary" style={{ width: `${width}%` }} />
                        </div>
                      </div>
                      <span className="text-sm font-medium">{total}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {studentReport.length > 0 && (
            <ReportTable
              title="Students Report"
              headers={['Student ID', 'Name', 'Email', 'Department', 'Course', 'Sem', 'Status']}
              rows={studentReport.map(r => [r.student_id, r.full_name, r.email, r.department, r.course, String(r.semester), r.status])}
            />
          )}

          {employeeReport.length > 0 && (
            <ReportTable
              title="Employees Report"
              headers={['Employee ID', 'Name', 'Email', 'Department', 'Designation', 'Status']}
              rows={employeeReport.map(r => [r.employee_id, r.full_name, r.email, r.department, r.designation, r.status])}
            />
          )}
        </div>
      )}

      {activeTab === 'attendance' && (
        <div className="space-y-4">
          {dashboard?.attendance_trend && dashboard.attendance_trend.length > 0 && (
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="mb-4 font-semibold">Attendance Trend</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left font-medium text-muted-foreground">Month</th>
                      <th className="px-4 py-2 text-right font-medium text-muted-foreground">Present</th>
                      <th className="px-4 py-2 text-right font-medium text-muted-foreground">Absent</th>
                      <th className="px-4 py-2 text-right font-medium text-muted-foreground">Late</th>
                      <th className="px-4 py-2 text-right font-medium text-muted-foreground">Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.attendance_trend.map((item, i) => (
                      <tr key={i} className="border-b last:border-b-0">
                        <td className="px-4 py-2">{item.month}</td>
                        <td className="px-4 py-2 text-right text-emerald-600 font-medium">{item.present}</td>
                        <td className="px-4 py-2 text-right text-red-600 font-medium">{item.absent}</td>
                        <td className="px-4 py-2 text-right text-amber-600 font-medium">{item.late}</td>
                        <td className="px-4 py-2 text-right font-medium">{item.rate.toFixed(1)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {attendanceReport.length > 0 && (
            <ReportTable
              title="Attendance Details"
              headers={['Date', 'Student', 'Employee', 'Department', 'Status']}
              rows={attendanceReport.map(r => [r.date, r.student_name ?? '-', r.employee_name ?? '-', r.department, r.status])}
            />
          )}
        </div>
      )}

      {activeTab === 'fees' && (
        <div className="space-y-4">
          {dashboard?.fee_collection && dashboard.fee_collection.length > 0 && (
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="mb-4 font-semibold">Fee Collection Trend</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="px-4 py-2 text-left font-medium text-muted-foreground">Month</th>
                      <th className="px-4 py-2 text-right font-medium text-muted-foreground">Collected</th>
                      <th className="px-4 py-2 text-right font-medium text-muted-foreground">Pending</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.fee_collection.map((item, i) => (
                      <tr key={i} className="border-b last:border-b-0">
                        <td className="px-4 py-2">{item.month}</td>
                        <td className="px-4 py-2 text-right text-emerald-600 font-medium">{formatINR(item.collected)}</td>
                        <td className="px-4 py-2 text-right text-amber-600 font-medium">{formatINR(item.pending)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {feeReport.length > 0 && (
            <ReportTable
              title="Fee Details"
              headers={['Student ID', 'Name', 'Course', 'Year', 'Sem', 'Total', 'Paid', 'Pending', 'Status']}
              rows={feeReport.map(r => [r.student_id, r.student_name, r.course, r.academic_year, String(r.semester), formatINR(r.total_amount), formatINR(r.paid_amount), formatINR(r.pending_amount), r.status])}
            />
          )}
        </div>
      )}

      {activeTab === 'results' && (
        <div className="space-y-4">
          {academicReport.length > 0 ? (
            <ReportTable
              title="Academic Performance"
              headers={['Student ID', 'Name', 'Subject', 'Internal', 'External', 'Total', 'Grade', 'Result']}
              rows={academicReport.map(r => [r.student_id, r.student_name, `${r.subject_code} - ${r.subject_name}`, String(r.internal_marks), String(r.external_marks), String(r.total_marks), r.grade ?? '-', r.is_passed ? 'Pass' : 'Fail'])}
            />
          ) : (
            <div className="rounded-xl border bg-card p-12 text-center text-muted-foreground">
              <Award className="mx-auto mb-4 h-8 w-8 text-muted-foreground/50" />
              <p>No academic performance data available.</p>
              <p className="mt-1 text-xs">Add results to see performance reports here.</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function StatBox({ icon: Icon, label, value, sub, color }: { icon: React.ElementType; label: string; value: string | number; sub: string; color: string }) {
  return (
    <div className="rounded-xl border bg-card p-5 shadow-sm">
      <div className="flex items-center gap-3 mb-3">
        <div className={`rounded-lg p-2 ${color}`}>
          <Icon className="h-4 w-4 text-white" />
        </div>
        <span className="text-sm text-muted-foreground">{label}</span>
      </div>
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground mt-1">{sub}</p>
    </div>
  )
}

function ReportTable({ title, headers, rows }: { title: string; headers: string[]; rows: string[][] }) {
  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <h3 className="mb-4 font-semibold">{title}</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              {headers.map(h => (
                <th key={h} className="px-4 py-2 text-left font-medium text-muted-foreground">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 50).map((row, i) => (
              <tr key={i} className="border-b last:border-b-0">
                {row.map((cell, j) => (
                  <td key={j} className="px-4 py-2">{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length > 50 && (
          <p className="mt-2 text-xs text-muted-foreground text-center">Showing 50 of {rows.length} rows. Export CSV for full data.</p>
        )}
      </div>
    </div>
  )
}

function formatINR(val: number | string) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(val))
}

function downloadCSV(data: any[], filename: string) {
  if (!data || data.length === 0) return
  const headers = Object.keys(data[0])
  const csv = [headers.join(','), ...data.map(row => headers.map(h => `"${row[h] ?? ''}"`).join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
}
