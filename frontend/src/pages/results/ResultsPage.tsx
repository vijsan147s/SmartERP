import { useState, useEffect, useCallback } from 'react'
import { Plus, Search, Pencil, Trash2, Award } from 'lucide-react'
import { resultsApi } from '@/services/results'
import { studentsApi } from '@/services/students'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable, type Column } from '@/components/common/DataTable'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import type { Result, Student, Subject } from '@/types'

export default function ResultsPage() {
  const [results, setResults] = useState<Result[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [subjects, setSubjects] = useState<Subject[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editResult, setEditResult] = useState<Result | null>(null)
  const { success, error: toastError } = useToast()

  const fetchResults = useCallback(async () => {
    try {
      setLoading(true)
      const res = await resultsApi.getResults({ search: search || undefined, page_size: 100 })
      setResults(res.data.items)
    } catch {
      toastError('Failed to load results')
    } finally {
      setLoading(false)
    }
  }, [search])

  const fetchRelated = useCallback(async () => {
    try {
      const [sRes, subRes] = await Promise.all([
        studentsApi.getStudents({ page_size: 100 }),
        resultsApi.getSubjects({ page_size: 100 }),
      ])
      setStudents(sRes.data.items)
      setSubjects(subRes.data.items)
    } catch {}
  }, [])

  useEffect(() => { fetchResults() }, [fetchResults])
  useEffect(() => { fetchRelated() }, [fetchRelated])

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleting(true)
    try {
      await resultsApi.deleteResult(deleteId)
      success('Result deleted successfully')
      setDeleteId(null)
      fetchResults()
    } catch {
      toastError('Failed to delete result')
    } finally {
      setDeleting(false)
    }
  }

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      student_id: Number(formData.get('student_id')),
      subject_id: Number(formData.get('subject_id')),
      internal_marks: Number(formData.get('internal_marks')),
      external_marks: Number(formData.get('external_marks')),
      semester: Number(formData.get('semester')),
      exam_date: (formData.get('exam_date') as string) || undefined,
      remarks: (formData.get('remarks') as string) || undefined,
    }
    try {
      if (editResult) {
        await resultsApi.updateResult(editResult.id, data)
        success('Result updated successfully')
      } else {
        await resultsApi.createResult(data)
        success('Result created successfully')
      }
      setShowForm(false)
      setEditResult(null)
      fetchResults()
    } catch {
      toastError(editResult ? 'Failed to update result' : 'Failed to create result')
    }
  }

  const columns: Column<Result>[] = [
    { key: 'student_student_id', header: 'Student ID' },
    { key: 'student_name', header: 'Student' },
    { key: 'subject_code', header: 'Subject' },
    { key: 'internal_marks', header: 'Internal', sortable: true, render: (r) => `${r.internal_marks}/${r.max_internal_marks}` },
    { key: 'external_marks', header: 'External', sortable: true, render: (r) => `${r.external_marks}/${r.max_external_marks}` },
    { key: 'total_marks', header: 'Total', sortable: true },
    { key: 'grade', header: 'Grade', render: (r) => r.grade ?? '-' },
    { key: 'is_passed', header: 'Result', render: (r) => r.is_passed ? <span className="text-emerald-600 font-medium">Pass</span> : <span className="text-red-600 font-medium">Fail</span> },
    { key: 'semester', header: 'Sem' },
    {
      key: 'actions',
      header: '',
      className: 'w-24',
      render: (r) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => { e.stopPropagation(); setEditResult(r); setShowForm(true) }}
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setDeleteId(r.id) }}
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
        title="Results"
        description="Manage student examination results"
        action={
          <Button onClick={() => { setEditResult(null); setShowForm(true) }}>
            <Plus className="mr-2 h-4 w-4" /> Add Result
          </Button>
        }
      />

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search results..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />
      </div>

      {loading ? (
        <PageLoader />
      ) : results.length === 0 ? (
        <EmptyState
          icon={Award}
          title="No results found"
          description={search ? 'Try adjusting your search terms.' : 'Get started by adding a result record.'}
          action={
            !search && (
              <Button onClick={() => { setEditResult(null); setShowForm(true) }}>
                <Plus className="mr-2 h-4 w-4" /> Add Result
              </Button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={results as any} />
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Delete Result"
        description="Are you sure you want to delete this result record?"
        onConfirm={handleDelete}
        isLoading={deleting}
      />

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl border bg-background p-6 shadow-xl animate-scale-in">
            <h2 className="text-lg font-semibold mb-4">{editResult ? 'Edit Result' : 'Add Result'}</h2>
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Student *</label>
                  <select name="student_id" required defaultValue={editResult?.student_id} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                    <option value="">Select student</option>
                    {students.map((s) => (
                      <option key={s.id} value={s.id}>{s.full_name} ({s.student_id})</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Subject *</label>
                  <select name="subject_id" required defaultValue={editResult?.subject_id} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                    <option value="">Select subject</option>
                    {subjects.map((s) => (
                      <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Internal Marks *</label>
                  <input name="internal_marks" type="number" required min={0} defaultValue={editResult?.internal_marks} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">External Marks *</label>
                  <input name="external_marks" type="number" required min={0} defaultValue={editResult?.external_marks} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Semester *</label>
                  <input name="semester" type="number" required min={1} max={10} defaultValue={editResult?.semester} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Exam Date</label>
                <input name="exam_date" type="date" defaultValue={editResult?.exam_date?.split('T')[0]} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Remarks</label>
                <input name="remarks" defaultValue={editResult?.remarks} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditResult(null) }}>Cancel</Button>
                <Button type="submit">{editResult ? 'Update' : 'Create'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
