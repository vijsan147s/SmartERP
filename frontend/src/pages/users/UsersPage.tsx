import { useState, useEffect, useCallback } from 'react'
import { Plus, Search, Pencil, Trash2, UserCog, Shield } from 'lucide-react'
import api from '@/services/api'
import { PageHeader } from '@/components/common/PageHeader'
import { DataTable, type Column } from '@/components/common/DataTable'
import { StatusBadge, getStatusVariant } from '@/components/common/StatusBadge'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { EmptyState } from '@/components/common/EmptyState'
import { ConfirmDialog } from '@/components/common/ConfirmDialog'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import type { User, PaginatedResponse } from '@/types'

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [editUser, setEditUser] = useState<User | null>(null)
  const { success, error: toastError } = useToast()

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true)
      const res = await api.get<PaginatedResponse<User>>('/users', { params: { search: search || undefined, page_size: 100 } })
      setUsers(res.data.items)
    } catch {
      toastError('Failed to load users')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => { fetchUsers() }, [fetchUsers])

  const handleDelete = async () => {
    if (!deleteId) return
    setDeleting(true)
    try {
      await api.delete(`/users/${deleteId}`)
      success('User deleted successfully')
      setDeleteId(null)
      fetchUsers()
    } catch {
      toastError('Failed to delete user')
    } finally {
      setDeleting(false)
    }
  }

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      username: formData.get('username') as string,
      email: formData.get('email') as string,
      full_name: formData.get('full_name') as string,
      phone: (formData.get('phone') as string) || undefined,
      password: (formData.get('password') as string) || undefined,
    }
    try {
      if (editUser) {
        const { password, ...updateData } = data
        await api.put(`/users/${editUser.id}`, updateData)
        success('User updated successfully')
      } else {
        await api.post('/users', data)
        success('User created successfully')
      }
      setShowForm(false)
      setEditUser(null)
      fetchUsers()
    } catch {
      toastError(editUser ? 'Failed to update user' : 'Failed to create user')
    }
  }

  const columns: Column<User>[] = [
    { key: 'username', header: 'Username', sortable: true },
    { key: 'full_name', header: 'Name', sortable: true },
    { key: 'email', header: 'Email', sortable: true },
    {
      key: 'roles',
      header: 'Role',
      render: (u) => {
        const role = u.roles?.[0]?.name
        return role ? <StatusBadge label={role} variant="info" /> : <StatusBadge label="No Role" variant="secondary" />
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (u) => <StatusBadge label={u.status} variant={getStatusVariant(u.status)} />,
    },
    {
      key: 'actions',
      header: '',
      className: 'w-24',
      render: (u) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => { e.stopPropagation(); setEditUser(u); setShowForm(true) }}
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <Pencil className="h-4 w-4" />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); setDeleteId(u.id) }}
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
        title="Users"
        description="Manage system users and access control"
        action={
          <Button onClick={() => { setEditUser(null); setShowForm(true) }}>
            <Plus className="mr-2 h-4 w-4" /> Add User
          </Button>
        }
      />

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search users..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-10 w-full rounded-lg border bg-background pl-10 pr-4 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
        />
      </div>

      {loading ? (
        <PageLoader />
      ) : users.length === 0 ? (
        <EmptyState
          icon={UserCog}
          title="No users found"
          description={search ? 'Try adjusting your search terms.' : 'Get started by adding a new user.'}
          action={
            !search && (
              <Button onClick={() => { setEditUser(null); setShowForm(true) }}>
                <Plus className="mr-2 h-4 w-4" /> Add User
              </Button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={users as any} />
      )}

      <ConfirmDialog
        open={!!deleteId}
        onOpenChange={(open) => !open && setDeleteId(null)}
        title="Delete User"
        description="Are you sure you want to delete this user? This action cannot be undone."
        onConfirm={handleDelete}
        isLoading={deleting}
      />

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-xl border bg-background p-6 shadow-xl animate-scale-in">
            <h2 className="text-lg font-semibold mb-4">{editUser ? 'Edit User' : 'Add User'}</h2>
            <form onSubmit={handleFormSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Username *</label>
                <input name="username" required defaultValue={editUser?.username} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Email *</label>
                <input name="email" type="email" required defaultValue={editUser?.email} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Full Name *</label>
                <input name="full_name" required defaultValue={editUser?.full_name} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Phone</label>
                <input name="phone" defaultValue={editUser?.phone} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">{editUser ? 'New Password (leave blank to keep)' : 'Password *'}</label>
                <input name="password" type="password" required={!editUser} className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <Button type="button" variant="outline" onClick={() => { setShowForm(false); setEditUser(null) }}>Cancel</Button>
                <Button type="submit">{editUser ? 'Update' : 'Create'}</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
