import { useState, useEffect, useCallback } from 'react'
import { Plus, Search, Pencil, Trash2, GraduationCap, Download } from 'lucide-react'
import { studentsApi } from '@/services/students'
import { departmentsApi } from '@/services/departments'
import { reportsApi } from '@/services/reports'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable, type Column } from '@/components/common/DataTable'
import { StatusBadge, getStatusVariant } from '@/components/common/StatusBadge'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import { formatDate } from '@/lib/utils'
import type { Student, Department } from '@/types'

export default function StudentsList() {
  const [students, setStudents] = useState<Student[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editStudent, setEditStudent] = useState<Student | null>(null)
  const { success, error: toastError } = useToast()

  const fetchStudents = useCallback(async () => {
    try {
      setLoading(true)
      const res = await studentsApi.getStudents({ search: search || undefined, page_size: 100 })
      setStudents(res.data.items)
    } catch {
      toastError('Failed to load students')
    } finally {
      setLoading(false)
    }
  }, [search])

  const fetchDepartments = useCallback(async () => {
    try {
      const res = await departmentsApi.getAllDepartments()
      setDepartments(res.data)
    } catch {}
  }, [])

  useEffect(() => { fetchStudents() }, [fetchStudents])
  useEffect(() => { fetchDepartments() }, [fetchDepartments])

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleting(true)
    try {
      await studentsApi.deleteStudent(deleteId)
      success('Student deleted successfully')
      setDeleteId(null)
      fetchStudents()
    } catch {
      toastError('Failed to delete student')
    } finally {
      setDeleting(false)
    }
  }

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      student_id: formData.get('student_id') as string,
      email: formData.get('email') as string,
      username: formData.get('username') as string,
      full_name: formData.get('full_name') as string,
      phone: (formData.get('phone') as string) || undefined,
      department_id: formData.get('department_id') ? Number(formData.get('department_id')) : undefined,
      course: formData.get('course') as string,
      semester: Number(formData.get('semester')),
      enrollment_date: formData.get('enrollment_date') as string,
      date_of_birth: (formData.get('date_of_birth') as string) || undefined,
      gender: (formData.get('gender') as string) || undefined,
      address: (formData.get('address') as string) || undefined,
      emergency_contact: (formData.get('emergency_contact') as string) || undefined,
      password: editStudent ? (formData.get('password') as string) || 'ChangeMe@123' : formData.get('password') as string,
    }
    try {
      if (editStudent) {
        await studentsApi.updateStudent(editStudent.id, data)
        success('Student updated successfully')
      } else {
        await studentsApi.createStudent(data)
        success('Student created successfully')
      }
      setShowForm(false)
      setEditStudent(null)
      fetchStudents()
    } catch {
      toastError(editStudent ? 'Failed to update student' : 'Failed to create student')
    }
  }

  const handleExport = async () => {
    try {
      const res = await reportsApi.getStudentsReport({ format: 'csv' })
      downloadCSV(res.data, 'students_report.csv')
      success('Export downloaded')
    } catch {
      toastError('Failed to export')
    }
  }

  const columns: Column<Student>[] = [
    { key: 'student_id', header: 'Student ID', sortable: true },
    { key: 'full_name', header: 'Name', sortable: true },
    { key: 'email', header: 'Email', sortable: true },
    { key: 'course', header: 'Course' },
    { key: 'semester', header: 'Sem', sortable: true },
    { key: 'enrollment_date', header: 'Enrollment', render: (s) => formatDate(s.enrollment_date) },
    {
      key: 'status',
      header: 'Status',
      render: (s) => <StatusBadge label={s.status} variant={getStatusVariant(s.status)} />,
    },
    {
      key: 'actions',
      header: '',
      className: 'w-24',
      render: (s) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => { e.stopPropagation(); setEditStudent(s); setShowForm(true) }}
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setDeleteId(s.id) }}
            className="rounded p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Students"
        description="Manage student records"
        action={
          <Button onClick={() => { setEditStudent(null); setShowForm(true) }}>
            <Plus className="mr-2 h-4 w-4" /> Add Student
          </Button>
        }
        secondaryAction={
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" /> Export
          </Button>
        }
      />

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search students..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />
      </div>

      {loading ? (
        <PageLoader />
      ) : students.length === 0 ? (
        <EmptyState
          icon={GraduationCap}
          title="No students found"
          description={search ? 'Try adjusting your search terms.' : 'Get started by adding a new student.'}
          action={
            !search && (
              <Button onClick={() => { setEditStudent(null); setShowForm(true) }}>
                <Plus className="mr-2 h-4 w-4" /> Add Student
              </Button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={students as any} />
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Delete Student"
        description="Are you sure you want to delete this student? This action cannot be undone."
        onConfirm={handleDelete}
        isLoading={deleting}
      />

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl border bg-background p-6 shadow-xl animate-scale-in max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4">{editStudent ? 'Edit Student' : 'Add Student'}</h2>
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Student ID *</label>
                  <input name="student_id" required defaultValue={editStudent?.student_id} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Full Name *</label>
                  <input name="full_name" required defaultValue={editStudent?.full_name} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Email *</label>
                  <input name="email" type="email" required defaultValue={editStudent?.email} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Username *</label>
                  <input name="username" required defaultValue={editStudent?.username} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              {!editStudent && (
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Password *</label>
                  <input name="password" type="password" required minLength={8} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Course *</label>
                  <input name="course" required defaultValue={editStudent?.course} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Semester *</label>
                  <input name="semester" type="number" required min={1} max={10} defaultValue={editStudent?.semester} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Department</label>
                  <select name="department_id" defaultValue={editStudent?.department_id ?? ''} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                    <option value="">Select department</option>
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Enrollment Date *</label>
                  <input name="enrollment_date" type="date" required defaultValue={editStudent?.enrollment_date?.split('T')[0]} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Phone</label>
                  <input name="phone" defaultValue={editStudent?.phone} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Gender</label>
                  <select name="gender" defaultValue={editStudent?.gender ?? ''} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                    <option value="">Select</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditStudent(null) }}>Cancel</Button>
                <Button type="submit">{editStudent ? 'Update' : 'Create'}</Button>
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
