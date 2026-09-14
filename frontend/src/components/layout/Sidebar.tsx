import { NavLink } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import {
  LayoutDashboard,
  GraduationCap,
  Users,
  Building2,
  CalendarCheck,
  IndianRupee,
  Award,
  BarChart3,
  UserCog,
  Settings,
  X,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  to: string
  label: string
  icon: React.ElementType
  adminOnly?: boolean
}

const navItems: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/students', label: 'Students', icon: GraduationCap },
  { to: '/employees', label: 'Employees', icon: Users },
  { to: '/departments', label: 'Departments', icon: Building2 },
  { to: '/attendance', label: 'Attendance', icon: CalendarCheck },
  { to: '/fees', label: 'Fees', icon: IndianRupee },
  { to: '/results', label: 'Results', icon: Award },
  { to: '/reports', label: 'Reports', icon: BarChart3 },
  { to: '/users', label: 'Users', icon: UserCog, adminOnly: true },
  { to: '/settings', label: 'Settings', icon: Settings },
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { hasRole } = useAuth()

  const filteredItems = navItems.filter(
    (item) => !item.adminOnly || hasRole('ADMIN')
  )

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 transition-opacity lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-60 flex-col bg-slate-900 transition-transform duration-300 ease-in-out lg:static lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Logo area */}
        <div className="flex h-16 items-center justify-between border-b border-slate-700/50 px-5">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <span className="text-sm font-bold text-white">S</span>
            </div>
            <span className="text-lg font-semibold text-white">SmartERP</span>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-slate-400 hover:text-white lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4 scrollbar-thin">
          {filteredItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  )
                }
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-slate-700/50 px-5 py-4">
          <p className="text-xs text-slate-500">SmartERP v1.0</p>
        </div>
      </aside>
    </>
  )
}
