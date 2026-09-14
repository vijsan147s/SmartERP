import { useState, useEffect, useCallback } from 'react'
import { Search, CalendarCheck, Download, CheckCircle2, XCircle, Clock } from 'lucide-react'
import { attendanceApi } from '@/services/attendance'
import { studentsApi } from '@/services/students'
import { employeesApi } from '@/services/employees'
import { reportsApi } from '@/services/reports'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable, type Column } from '@/components/common/DataTable'
import { StatusBadge, getStatusVariant } from '@/components/common/StatusBadge'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import type { Attendance, Student, Employee } from '@/types'

export default function AttendancePage() {
  const [attendance, setAttendance] = useState<Attendance[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [stats, setStats] = useState<{ total: number; present: number; absent: number; late: number } | null>(null)
  const { success, error: toastError } = useToast()

  const fetchAttendance = useCallback(async () => {
    try {
      setLoading(true)
      const res = await attendanceApi.getAttendance({ search: search || undefined, page_size: 100 })
      const items = res.data.items
      setAttendance(items)
      const total = items.length
      const present = items.filter(a => a.status === 'PRESENT').length
      const absent = items.filter(a => a.status === 'ABSENT').length
      const late = items.filter(a => a.status === 'LATE').length
      setStats({ total, present, absent, late })
    } catch {
      toastError('Failed to load attendance')
    } finally {
      setLoading(false)
    }
  }, [search])

  const fetchRelated = useCallback(async () => {
    try {
      const [sRes, eRes] = await Promise.all([
        studentsApi.getStudents({ page_size: 100 }),
        employeesApi.getEmployees({ page_size: 100 }),
      ])
      setStudents(sRes.data.items)
      setEmployees(eRes.data.items)
    } catch {}
  }, [])

  useEffect(() => { fetchAttendance() }, [fetchAttendance])
  useEffect(() => { fetchRelated() }, [fetchRelated])

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const studentId = formData.get('student_id') ? Number(formData.get('student_id')) : undefined
    const employeeId = formData.get('employee_id') ? Number(formData.get('employee_id')) : undefined

    if (!studentId && !employeeId) {
      toastError('Please select a student or employee')
      return
    }

    const data = {
      student_id: studentId,
      employee_id: employeeId,
      date: formData.get('date') as string,
      status: formData.get('status') as 'PRESENT' | 'ABSENT' | 'LATE' | 'EXCUSED',
      remarks: (formData.get('remarks') as string) || undefined,
    }
    try {
      await attendanceApi.createAttendance(data)
      success('Attendance recorded successfully')
      setShowForm(false)
      fetchAttendance()
    } catch {
      toastError('Failed to record attendance')
    }
  }

  const handleExport = async () => {
    try {
      const res = await reportsApi.getAttendanceReport({ format: 'csv' })
      downloadCSV(res.data, 'attendance_report.csv')
      success('Export downloaded')
    } catch {
      toastError('Failed to export')
    }
  }

  const summaryCards = [
    { label: 'Total', value: stats?.total ?? 0, icon: CalendarCheck, color: 'bg-blue-500' },
    { label: 'Present', value: stats?.present ?? 0, icon: CheckCircle2, color: 'bg-emerald-500' },
    { label: 'Absent', value: stats?.absent ?? 0, icon: XCircle, color: 'bg-red-500' },
    { label: 'Late', value: stats?.late ?? 0, icon: Clock, color: 'bg-amber-500' },
  ]

  const columns: Column<Attendance>[] = [
    { key: 'student_name', header: 'Name', render: (a) => a.student_name || a.employee_name || '-' },
    { key: 'student_id', header: 'Type', render: (a) => a.student_id ? 'Student' : 'Employee' },
    { key: 'date', header: 'Date' },
    {
      key: 'status',
      header: 'Status',
      render: (a) => <StatusBadge label={a.status} variant={getStatusVariant(a.status)} />,
    },
    { key: 'remarks', header: 'Remarks', render: (a) => a.remarks ?? '-' },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Attendance"
        description="Track daily attendance records"
        action={
          <Button onClick={() => setShowForm(true)}>
            <CalendarCheck className="mr-2 h-4 w-4" /> Mark Attendance
          </Button>
        }
        secondaryAction={
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" /> Export
          </Button>
        }
      />

      {stats && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {summaryCards.map((card) => {
            const Icon = card.icon
            return (
              <div key={card.label} className="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
                <div className={`rounded-lg p-2.5 ${card.color}`}>
                  <Icon className="h-4 w-4 text-white" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{card.value}</p>
                  <p className="text-xs text-muted-foreground">{card.label}</p>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search attendance..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />
      </div>

      {loading ? (
        <PageLoader />
      ) : attendance.length === 0 ? (
        <EmptyState
          icon={CalendarCheck}
          title="No attendance records found"
          description="Start by marking attendance for today."
          action={
            <Button onClick={() => setShowForm(true)}>
              <CalendarCheck className="mr-2 h-4 w-4" /> Mark Attendance
            </Button>
          }
        />
      ) : (
        <DataTable columns={columns} data={attendance as any} />
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl border bg-background p-6 shadow-xl animate-scale-in">
            <h2 className="text-lg font-semibold mb-4">Mark Attendance</h2>
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Date *</label>
                <input name="date" type="date" required defaultValue={new Date().toISOString().split('T')[0]} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Student</label>
                <select name="student_id" className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                  <option value="">Select student</option>
                  {students.map((s) => (
                    <option key={s.id} value={s.id}>{s.full_name} ({s.student_id})</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Employee</label>
                <select name="employee_id" className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                  <option value="">Select employee</option>
                  {employees.map((e) => (
                    <option key={e.id} value={e.id}>{e.full_name} ({e.employee_id})</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Status *</label>
                <select name="status" required className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                  <option value="PRESENT">Present</option>
                  <option value="ABSENT">Absent</option>
                  <option value="LATE">Late</option>
                  <option value="EXCUSED">Excused</option>
                </select>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Remarks</label>
                <input name="remarks" className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" placeholder="Optional remarks" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
                <Button type="submit">Save</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
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
