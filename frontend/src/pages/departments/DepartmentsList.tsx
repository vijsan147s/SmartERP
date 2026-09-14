import { useState, useEffect, useCallback } from 'react'
import { Plus, Search, Pencil, Trash2, Building2 } from 'lucide-react'
import { departmentsApi } from '@/services/departments'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable, type Column } from '@/components/common/DataTable'
import { StatusBadge, getStatusVariant } from '@/components/common/StatusBadge'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import type { Department } from '@/types'

export default function DepartmentsList() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editDept, setEditDept] = useState<Department | null>(null)
  const { success, error: toastError } = useToast()

  const fetchDepartments = useCallback(async () => {
    try {
      setLoading(true)
      const res = await departmentsApi.getDepartments({ search: search || undefined, page_size: 100 })
      setDepartments(res.data.items)
    } catch {
      toastError('Failed to load departments')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { fetchDepartments() }, [fetchDepartments])

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleting(true)
    try {
      await departmentsApi.deleteDepartment(deleteId)
      success('Department deleted successfully')
      setDeleteId(null)
      fetchDepartments()
    } catch {
      toastError('Failed to delete department')
    } finally {
      setDeleting(false)
    }
  }

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      name: formData.get('name') as string,
      code: formData.get('code') as string,
      description: (formData.get('description') as string) || undefined,
      is_active: formData.get('is_active') === 'on',
    }
    try {
      if (editDept) {
        await departmentsApi.updateDepartment(editDept.id, data)
        success('Department updated successfully')
      } else {
        await departmentsApi.createDepartment(data)
        success('Department created successfully')
      }
      setShowForm(false)
      setEditDept(null)
      fetchDepartments()
    } catch {
      toastError(editDept ? 'Failed to update department' : 'Failed to create department')
    }
  }

  const columns: Column<Department>[] = [
    { key: 'code', header: 'Code', sortable: true },
    { key: 'name', header: 'Name', sortable: true },
    { key: 'description', header: 'Description', render: (d) => d.description ?? '-' },
    {
      key: 'student_count',
      header: 'Students',
      render: (d) => String(d.student_count ?? 0),
    },
    {
      key: 'employee_count',
      header: 'Employees',
      render: (d) => String(d.employee_count ?? 0),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (d) => (
        <StatusBadge
          label={d.is_active ? 'Active' : 'Inactive'}
          variant={getStatusVariant(d.is_active ? 'ACTIVE' : 'INACTIVE')}
        />
      ),
    },
    {
      key: 'actions',
      header: '',
      className: 'w-24',
      render: (d) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => { e.stopPropagation(); setEditDept(d); setShowForm(true) }}
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setDeleteId(d.id) }}
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
        title="Departments"
        description="Manage institutional departments"
        action={
          <Button onClick={() => { setEditDept(null); setShowForm(true) }}>
            <Plus className="mr-2 h-4 w-4" /> Add Department
          </Button>
        }
      />

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search departments..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />
      </div>

      {loading ? (
        <PageLoader />
      ) : departments.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No departments found"
          description={search ? 'Try adjusting your search terms.' : 'Get started by adding a new department.'}
          action={
            !search && (
              <Button onClick={() => { setEditDept(null); setShowForm(true) }}>
                <Plus className="mr-2 h-4 w-4" /> Add Department
              </Button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={departments as any} />
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Delete Department"
        description="Are you sure you want to delete this department? This action cannot be undone."
        onConfirm={handleDelete}
        isLoading={deleting}
      />

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl border bg-background p-6 shadow-xl animate-scale-in">
            <h2 className="text-lg font-semibold mb-4">{editDept ? 'Edit Department' : 'Add Department'}</h2>
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Name *</label>
                  <input name="name" required defaultValue={editDept?.name} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Code *</label>
                  <input name="code" required defaultValue={editDept?.code} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Description</label>
                <textarea
                  name="description"
                  rows={3}
                  defaultValue={editDept?.description}
                  className="w-full rounded-lg border bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  name="is_active"
                  defaultChecked={editDept?.is_active ?? true}
                  className="h-4 w-4 rounded border-gray-300"
                />
                <label className="text-sm font-medium">Active</label>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditDept(null) }}>Cancel</Button>
                <Button type="submit">{editDept ? 'Update' : 'Create'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
