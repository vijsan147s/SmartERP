import { useState, useEffect, useCallback } from 'react'
import { Plus, Search, Pencil, Trash2, Users, Download } from 'lucide-react'
import { employeesApi } from '@/services/employees'
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
import { formatDate, formatCurrency } from '@/lib/utils'
import type { Employee, Department } from '@/types'

export default function EmployeesList() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editEmployee, setEditEmployee] = useState<Employee | null>(null)
  const { success, error: toastError } = useToast()

  const fetchEmployees = useCallback(async () => {
    try {
      setLoading(true)
      const res = await employeesApi.getEmployees({ search: search || undefined, page_size: 100 })
      setEmployees(res.data.items)
    } catch {
      toastError('Failed to load employees')
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

  useEffect(() => { fetchEmployees() }, [fetchEmployees])
  useEffect(() => { fetchDepartments() }, [fetchDepartments])

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleting(true)
    try {
      await employeesApi.deleteEmployee(deleteId)
      success('Employee deleted successfully')
      setDeleteId(null)
      fetchEmployees()
    } catch {
      toastError('Failed to delete employee')
    } finally {
      setDeleting(false)
    }
  }

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      employee_id: formData.get('employee_id') as string,
      email: formData.get('email') as string,
      username: formData.get('username') as string,
      full_name: formData.get('full_name') as string,
      phone: (formData.get('phone') as string) || undefined,
      department_id: formData.get('department_id') ? Number(formData.get('department_id')) : undefined,
      designation: formData.get('designation') as string,
      joining_date: formData.get('joining_date') as string,
      salary: Number(formData.get('salary')),
      date_of_birth: (formData.get('date_of_birth') as string) || undefined,
      gender: (formData.get('gender') as string) || undefined,
      address: (formData.get('address') as string) || undefined,
      emergency_contact: (formData.get('emergency_contact') as string) || undefined,
      password: editEmployee ? (formData.get('password') as string) || 'ChangeMe@123' : formData.get('password') as string,
    }
    try {
      if (editEmployee) {
        await employeesApi.updateEmployee(editEmployee.id, data)
        success('Employee updated successfully')
      } else {
        await employeesApi.createEmployee(data)
        success('Employee created successfully')
      }
      setShowForm(false)
      setEditEmployee(null)
      fetchEmployees()
    } catch {
      toastError(editEmployee ? 'Failed to update employee' : 'Failed to create employee')
    }
  }

  const handleExport = async () => {
    try {
      const res = await reportsApi.getEmployeesReport({ format: 'csv' })
      downloadCSV(res.data, 'employees_report.csv')
      success('Export downloaded')
    } catch {
      toastError('Failed to export')
    }
  }

  const columns: Column<Employee>[] = [
    { key: 'employee_id', header: 'Employee ID', sortable: true },
    { key: 'full_name', header: 'Name', sortable: true },
    { key: 'email', header: 'Email', sortable: true },
    { key: 'designation', header: 'Designation' },
    { key: 'joining_date', header: 'Joining Date', render: (e) => formatDate(e.joining_date) },
    { key: 'salary', header: 'Salary', render: (e) => formatCurrency(e.salary) },
    {
      key: 'status',
      header: 'Status',
      render: (e) => <StatusBadge label={e.status} variant={getStatusVariant(e.status)} />,
    },
    {
      key: 'actions',
      header: '',
      className: 'w-24',
      render: (e) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(ev) => { ev.stopPropagation(); setEditEmployee(e); setShowForm(true) }}
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={(ev) => { ev.stopPropagation(); setDeleteId(e.id) }}
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
        title="Employees"
        description="Manage employee records"
        action={
          <Button onClick={() => { setEditEmployee(null); setShowForm(true) }}>
            <Plus className="mr-2 h-4 w-4" /> Add Employee
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
          placeholder="Search employees..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />
      </div>

      {loading ? (
        <PageLoader />
      ) : employees.length === 0 ? (
        <EmptyState
          icon={Users}
          title="No employees found"
          description={search ? 'Try adjusting your search terms.' : 'Get started by adding a new employee.'}
          action={
            !search && (
              <Button onClick={() => { setEditEmployee(null); setShowForm(true) }}>
                <Plus className="mr-2 h-4 w-4" /> Add Employee
              </Button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={employees as any} />
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Delete Employee"
        description="Are you sure you want to delete this employee? This action cannot be undone."
        onConfirm={handleDelete}
        isLoading={deleting}
      />

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl border bg-background p-6 shadow-xl animate-scale-in max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4">{editEmployee ? 'Edit Employee' : 'Add Employee'}</h2>
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Employee ID *</label>
                  <input name="employee_id" required defaultValue={editEmployee?.employee_id} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Full Name *</label>
                  <input name="full_name" required defaultValue={editEmployee?.full_name} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Email *</label>
                  <input name="email" type="email" required defaultValue={editEmployee?.email} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Username *</label>
                  <input name="username" required defaultValue={editEmployee?.username} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              {!editEmployee && (
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Password *</label>
                  <input name="password" type="password" required minLength={8} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Designation *</label>
                  <input name="designation" required defaultValue={editEmployee?.designation} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Department</label>
                  <select name="department_id" defaultValue={editEmployee?.department_id ?? ''} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                    <option value="">Select department</option>
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Joining Date *</label>
                  <input name="joining_date" type="date" required defaultValue={editEmployee?.joining_date?.split('T')[0]} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Salary *</label>
                  <input name="salary" type="number" required min={0} defaultValue={editEmployee?.salary} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Phone</label>
                  <input name="phone" defaultValue={editEmployee?.phone} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Gender</label>
                  <select name="gender" defaultValue={editEmployee?.gender ?? ''} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                    <option value="">Select</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditEmployee(null) }}>Cancel</Button>
                <Button type="submit">{editEmployee ? 'Update' : 'Create'}</Button>
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
