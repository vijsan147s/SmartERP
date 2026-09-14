import { useState, useEffect, useCallback } from 'react'
import { Plus, Search, Pencil, Trash2, IndianRupee } from 'lucide-react'
import { feesApi } from '@/services/fees'
import { studentsApi } from '@/services/students'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable, type Column } from '@/components/common/DataTable'
import { StatusBadge, getStatusVariant } from '@/components/common/StatusBadge'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { Fee, Student, FeeDashboardStats } from '@/types'

export default function FeesPage() {
  const [fees, setFees] = useState<Fee[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editFee, setEditFee] = useState<Fee | null>(null)
  const [stats, setStats] = useState<FeeDashboardStats | null>(null)
  const { success, error: toastError } = useToast()

  const fetchFees = useCallback(async () => {
    try {
      setLoading(true)
      const res = await feesApi.getFees({ search: search || undefined, page_size: 100 })
      setFees(res.data.items)
    } catch {
      toastError('Failed to load fees')
    } finally {
      setLoading(false)
    }
  }, [search])

  const fetchStats = useCallback(async () => {
    try {
      const res = await feesApi.getDashboardStats()
      setStats(res.data)
    } catch {}
  }, [])

  const fetchStudents = useCallback(async () => {
    try {
      const res = await studentsApi.getStudents({ page_size: 100 })
      setStudents(res.data.items)
    } catch {}
  }, [])

  useEffect(() => { fetchFees() }, [fetchFees])
  useEffect(() => { fetchStats() }, [fetchStats])
  useEffect(() => { fetchStudents() }, [fetchStudents])

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleting(true)
    try {
      await feesApi.deleteFee(deleteId)
      success('Fee record deleted successfully')
      setDeleteId(null)
      fetchFees()
      fetchStats()
    } catch {
      toastError('Failed to delete fee record')
    } finally {
      setDeleting(false)
    }
  }

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      student_id: Number(formData.get('student_id')),
      academic_year: formData.get('academic_year') as string,
      semester: Number(formData.get('semester')),
      total_amount: Number(formData.get('total_amount')),
      due_date: (formData.get('due_date') as string) || undefined,
      remarks: (formData.get('remarks') as string) || undefined,
    }
    try {
      if (editFee) {
        await feesApi.updateFee(editFee.id, data)
        success('Fee record updated successfully')
      } else {
        await feesApi.createFee(data)
        success('Fee record created successfully')
      }
      setShowForm(false)
      setEditFee(null)
      fetchFees()
      fetchStats()
    } catch {
      toastError(editFee ? 'Failed to update fee record' : 'Failed to create fee record')
    }
  }

  const columns: Column<Fee>[] = [
    { key: 'student_student_id', header: 'Student ID' },
    { key: 'student_name', header: 'Student', sortable: true },
    { key: 'academic_year', header: 'Year' },
    { key: 'semester', header: 'Sem' },
    { key: 'total_amount', header: 'Amount', sortable: true, render: (f) => formatCurrency(f.total_amount) },
    { key: 'paid_amount', header: 'Paid', render: (f) => formatCurrency(f.paid_amount) },
    { key: 'pending_amount', header: 'Pending', render: (f) => formatCurrency(f.pending_amount) },
    { key: 'due_date', header: 'Due Date', render: (f) => f.due_date ? formatDate(f.due_date) : '-' },
    {
      key: 'status',
      header: 'Status',
      render: (f) => <StatusBadge label={f.status} variant={getStatusVariant(f.status)} />,
    },
    {
      key: 'actions',
      header: '',
      className: 'w-24',
      render: (f) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => { e.stopPropagation(); setEditFee(f); setShowForm(true) }}
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setDeleteId(f.id) }}
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
        title="Fees"
        description="Manage fee collections and payments"
        action={
          <Button onClick={() => { setEditFee(null); setShowForm(true) }}>
            <Plus className="mr-2 h-4 w-4" /> Add Fee
          </Button>
        }
      />

      {stats && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
            <div className="rounded-lg bg-emerald-500 p-2.5">
              <IndianRupee className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold">{formatCurrency(stats.total_collected)}</p>
              <p className="text-xs text-muted-foreground">Total Collected</p>
            </div>
          </div>
          <div className="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
            <div className="rounded-lg bg-amber-500 p-2.5">
              <IndianRupee className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold">{formatCurrency(stats.total_pending)}</p>
              <p className="text-xs text-muted-foreground">Total Pending</p>
            </div>
          </div>
          <div className="flex items-center gap-4 rounded-xl border bg-card p-4 shadow-sm">
            <div className="rounded-lg bg-blue-500 p-2.5">
              <IndianRupee className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.collection_rate.toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground">Collection Rate</p>
            </div>
          </div>
        </div>
      )}

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search fees..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />
      </div>

      {loading ? (
        <PageLoader />
      ) : fees.length === 0 ? (
        <EmptyState
          icon={IndianRupee}
          title="No fee records found"
          description={search ? 'Try adjusting your search terms.' : 'Get started by adding a fee record.'}
          action={
            !search && (
              <Button onClick={() => { setEditFee(null); setShowForm(true) }}>
                <Plus className="mr-2 h-4 w-4" /> Add Fee
              </Button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={fees as any} />
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Delete Fee Record"
        description="Are you sure you want to delete this fee record?"
        onConfirm={handleDelete}
        isLoading={deleting}
      />

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl border bg-background p-6 shadow-xl animate-scale-in">
            <h2 className="text-lg font-semibold mb-4">{editFee ? 'Edit Fee' : 'Add Fee'}</h2>
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Student *</label>
                <select name="student_id" required defaultValue={editFee?.student_id} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                  <option value="">Select student</option>
                  {students.map((s) => (
                    <option key={s.id} value={s.id}>{s.full_name} ({s.student_id})</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Academic Year *</label>
                  <input name="academic_year" required defaultValue={editFee?.academic_year} placeholder="2025-2026" className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Semester *</label>
                  <input name="semester" type="number" required min={1} max={10} defaultValue={editFee?.semester} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Total Amount *</label>
                  <input name="total_amount" type="number" required min={0} defaultValue={editFee?.total_amount} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Due Date</label>
                  <input name="due_date" type="date" defaultValue={editFee?.due_date?.split('T')[0]} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Remarks</label>
                <input name="remarks" defaultValue={editFee?.remarks} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditFee(null) }}>Cancel</Button>
                <Button type="submit">{editFee ? 'Update' : 'Create'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
