import { useState } from 'react'
import { Save, User, Lock, Bell } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/toast'
import api from '@/services/api'

export default function SettingsPage() {
  const { user } = useAuth()
  const { success, error: toastError } = useToast()
  const [activeTab, setActiveTab] = useState<'profile' | 'password' | 'notifications'>('profile')
  const [saving, setSaving] = useState(false)

  const handleProfileUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setSaving(true)
    const formData = new FormData(e.currentTarget)
    try {
      await api.put(`/users/${user?.id}`, {
        full_name: formData.get('full_name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
      })
      success('Profile updated successfully')
    } catch {
      toastError('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordChange = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setSaving(true)
    const formData = new FormData(e.currentTarget)
    const newPassword = formData.get('new_password') as string
    const confirmPassword = formData.get('confirm_password') as string

    if (newPassword !== confirmPassword) {
      toastError('Passwords do not match')
      setSaving(false)
      return
    }

    try {
      await api.post('/auth/change-password', {
        current_password: formData.get('current_password'),
        new_password: newPassword,
      })
      success('Password changed successfully')
      ;(e.target as HTMLFormElement).reset()
    } catch {
      toastError('Failed to change password. Check your current password.')
    } finally {
      setSaving(false)
    }
  }

  const tabs = [
    { key: 'profile', label: 'Profile', icon: User },
    { key: 'password', label: 'Password', icon: Lock },
    { key: 'notifications', label: 'Notifications', icon: Bell },
  ] as const

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Settings"
        description="Manage your account settings"
      />

      <div className="flex flex-col gap-6 lg:flex-row">
        <nav className="w-full lg:w-56">
          <div className="flex gap-1 rounded-lg border bg-muted p-1 lg:flex-col">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                    activeTab === tab.key
                      ? 'bg-background text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </nav>

        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-semibold">Profile Information</h3>
              <form onSubmit={handleProfileUpdate} className="space-y-4 max-w-lg">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Username</label>
                  <input
                    value={user?.username ?? ''}
                    disabled
                    className="h-10 w-full rounded-lg border bg-muted px-3 text-sm text-muted-foreground"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Full Name</label>
                  <input
                    name="full_name"
                    defaultValue={user?.full_name}
                    className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Email</label>
                  <input
                    name="email"
                    type="email"
                    defaultValue={user?.email}
                    className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Phone</label>
                  <input
                    name="phone"
                    defaultValue={user?.phone}
                    className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Role</label>
                  <input
                    value={user?.roles?.[0]?.name ?? 'User'}
                    disabled
                    className="h-10 w-full rounded-lg border bg-muted px-3 text-sm text-muted-foreground"
                  />
                </div>
                <Button type="submit" disabled={saving}>
                  <Save className="mr-2 h-4 w-4" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </form>
            </div>
          )}

          {activeTab === 'password' && (
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-semibold">Change Password</h3>
              <form onSubmit={handlePasswordChange} className="space-y-4 max-w-lg">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Current Password</label>
                  <input
                    name="current_password"
                    type="password"
                    required
                    className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">New Password</label>
                  <input
                    name="new_password"
                    type="password"
                    required
                    minLength={8}
                    className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-sm font-medium">Confirm New Password</label>
                  <input
                    name="confirm_password"
                    type="password"
                    required
                    minLength={8}
                    className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
                <Button type="submit" disabled={saving}>
                  <Lock className="mr-2 h-4 w-4" />
                  {saving ? 'Changing...' : 'Change Password'}
                </Button>
              </form>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="rounded-xl border bg-card p-6 shadow-sm">
              <h3 className="mb-4 text-lg font-semibold">Notification Preferences</h3>
              <div className="space-y-4 max-w-lg">
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <p className="text-sm font-medium">Email Notifications</p>
                    <p className="text-xs text-muted-foreground">Receive email updates about important events</p>
                  </div>
                  <input type="checkbox" defaultChecked className="h-4 w-4 rounded" />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <p className="text-sm font-medium">Fee Reminders</p>
                    <p className="text-xs text-muted-foreground">Get notified about pending fee payments</p>
                  </div>
                  <input type="checkbox" defaultChecked className="h-4 w-4 rounded" />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <p className="text-sm font-medium">Attendance Alerts</p>
                    <p className="text-xs text-muted-foreground">Receive alerts for attendance irregularities</p>
                  </div>
                  <input type="checkbox" className="h-4 w-4 rounded" />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
