import { useState, useEffect } from 'react'
import {
  Users,
  GraduationCap,
  Building2,
  CalendarCheck,
  IndianRupee,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  Activity,
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { reportsApi } from '@/services/reports'
import { PageLoader } from '@/components/common/LoadingSpinner'
import { useToast } from '@/components/ui/toast'
import type { DashboardResponse } from '@/types'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ElementType
  trend?: { value: number; isPositive: boolean }
  color: string
}

function StatCard({ title, value, subtitle, icon: Icon, trend, color }: StatCardProps) {
  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold tracking-tight">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
          {trend && (
            <div className="flex items-center gap-1 text-xs">
              {trend.isPositive ? (
                <TrendingUp className="h-3 w-3 text-emerald-500" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-500" />
              )}
              <span className={trend.isPositive ? 'text-emerald-500' : 'text-red-500'}>
                {Math.abs(trend.value)}%
              </span>
              <span className="text-muted-foreground">vs last month</span>
            </div>
          )}
        </div>
        <div className={`rounded-lg p-3 ${color}`}>
          <Icon className="h-5 w-5 text-white" />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const { error: toastError } = useToast()

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await reportsApi.getDashboard()
        setData(res.data)
      } catch {
        toastError('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <PageLoader text="Loading dashboard..." />

  const stats = data?.stats
  const attendanceRate = stats?.attendance_rate ?? 0
  const pendingFees = stats?.pending_fees ?? 0
  const feeStatus = data?.fee_status
  const latestTrend = data?.attendance_trend?.[data.attendance_trend.length - 1]

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Welcome back! Here's an overview of your institution.
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Students"
          value={stats?.total_students ?? 0}
          icon={GraduationCap}
          color="bg-blue-500"
        />
        <StatCard
          title="Total Employees"
          value={stats?.total_employees ?? 0}
          icon={Users}
          color="bg-emerald-500"
        />
        <StatCard
          title="Departments"
          value={stats?.total_departments ?? 0}
          icon={Building2}
          color="bg-amber-500"
        />
        <StatCard
          title="Attendance Rate"
          value={`${attendanceRate.toFixed(1)}%`}
          subtitle={latestTrend ? `${latestTrend.present} present this month` : 'No data'}
          icon={CalendarCheck}
          color="bg-purple-500"
        />
      </div>

      {/* Second row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="rounded-lg bg-emerald-500 p-2">
              <IndianRupee className="h-4 w-4 text-white" />
            </div>
            <h3 className="font-semibold">Fee Collection</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total Fees</span>
              <span className="text-sm font-semibold">
                {formatIndian(pendingFees)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Paid</span>
              <span className="text-sm font-semibold text-emerald-600">
                {feeStatus?.paid ?? 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Partial</span>
              <span className="text-sm font-semibold text-amber-600">
                {feeStatus?.partial ?? 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Pending</span>
              <span className="text-sm font-semibold text-red-600">
                {feeStatus?.pending ?? 0}
              </span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-4">
            <div className="rounded-lg bg-blue-500 p-2">
              <Activity className="h-4 w-4 text-white" />
            </div>
            <h3 className="font-semibold">Distribution</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Students</span>
              <span className="text-sm font-semibold text-blue-600">
                {data?.employee_student_distribution?.students ?? 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Employees</span>
              <span className="text-sm font-semibold text-emerald-600">
                {data?.employee_student_distribution?.employees ?? 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Active Users</span>
              <span className="text-sm font-semibold text-purple-600">
                {stats?.active_users ?? 0}
              </span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-6 shadow-sm sm:col-span-2 lg:col-span-1">
          <div className="flex items-center gap-3 mb-4">
            <div className="rounded-lg bg-purple-500 p-2">
              <ArrowUpRight className="h-4 w-4 text-white" />
            </div>
            <h3 className="font-semibold">Quick Actions</h3>
          </div>
          <div className="space-y-2">
            <a href="/students" className="flex items-center rounded-lg px-3 py-2 text-sm hover:bg-muted transition-colors">
              View Students
            </a>
            <a href="/attendance" className="flex items-center rounded-lg px-3 py-2 text-sm hover:bg-muted transition-colors">
              Mark Attendance
            </a>
            <a href="/fees" className="flex items-center rounded-lg px-3 py-2 text-sm hover:bg-muted transition-colors">
              Manage Fees
            </a>
            <a href="/reports" className="flex items-center rounded-lg px-3 py-2 text-sm hover:bg-muted transition-colors">
              View Reports
            </a>
          </div>
        </div>
      </div>

      {/* Department Distribution */}
      {data?.department_distribution && data.department_distribution.length > 0 && (
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h3 className="mb-4 font-semibold">Department Distribution</h3>
          <div className="space-y-3">
            {data.department_distribution.map((dept) => {
              const maxCount = Math.max(...data.department_distribution.map(d => d.student_count + d.employee_count))
              const total = dept.student_count + dept.employee_count
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

      {/* Charts Row */}
      <div className="grid gap-4 lg:grid-cols-2">
        {/* Attendance Trend Bar Chart */}
        {data?.attendance_trend && data.attendance_trend.length > 0 && (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <h3 className="mb-4 font-semibold">Attendance Trend</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={data.attendance_trend}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="present" fill="#10b981" name="Present" radius={[4, 4, 0, 0]} />
                <Bar dataKey="absent" fill="#ef4444" name="Absent" radius={[4, 4, 0, 0]} />
                <Bar dataKey="late" fill="#f59e0b" name="Late" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Fee Status Pie Chart */}
        {data?.fee_status && (
          <div className="rounded-xl border bg-card p-6 shadow-sm">
            <h3 className="mb-4 font-semibold">Fee Status</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'Paid', value: data.fee_status.paid },
                    { name: 'Partial', value: data.fee_status.partial },
                    { name: 'Pending', value: data.fee_status.pending },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={3}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  <Cell fill="#10b981" />
                  <Cell fill="#f59e0b" />
                  <Cell fill="#ef4444" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Department Student/Employee Bar Chart */}
      {data?.department_distribution && data.department_distribution.length > 0 && (
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h3 className="mb-4 font-semibold">Students vs Employees by Department</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.department_distribution}>
              <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
              <XAxis dataKey="department_name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="student_count" fill="#3b82f6" name="Students" radius={[4, 4, 0, 0]} />
              <Bar dataKey="employee_count" fill="#8b5cf6" name="Employees" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

function formatIndian(val: number) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(val)
}
