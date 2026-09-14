import { useState, useRef, useEffect } from 'react'
import { useAuth } from '@/context/AuthContext'
import { getInitials } from '@/lib/utils'
import { Menu, Bell, LogOut, ChevronDown, User } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TopNavProps {
  onMenuClick: () => void
}

export default function TopNav({ onMenuClick }: TopNavProps) {
  const { user, logout } = useAuth()
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const displayName = user
    ? user.full_name || user.username
    : 'User'

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      {/* Left side */}
      <div className="flex items-center gap-3 pl-4 lg:pl-0">
        <button
          onClick={onMenuClick}
          className="rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-accent-foreground lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right side */}
      <div className="flex items-center gap-2 pr-4">
        {/* Notifications */}
        <button className="relative rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-accent-foreground">
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary" />
        </button>

        {/* User dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-accent"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
              <span className="text-xs font-semibold">
                {user ? getInitials(displayName) : '?'}
              </span>
            </div>
            <div className="hidden text-left sm:block">
              <p className="text-sm font-medium leading-tight">{displayName}</p>
              <p className="text-xs text-muted-foreground">
                {user?.roles?.[0]?.name || (user?.is_superuser ? 'Super Admin' : 'User')}
              </p>
            </div>
            <ChevronDown
              className={cn(
                'h-4 w-4 text-muted-foreground transition-transform',
                isDropdownOpen && 'rotate-180'
              )}
            />
          </button>

          {isDropdownOpen && (
            <div className="absolute right-0 top-full z-50 mt-1 w-56 origin-top-right animate-fade-in-down rounded-lg border bg-background py-1 shadow-md">
              <div className="border-b px-4 py-3">
                <p className="text-sm font-medium">{displayName}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
              <button
                onClick={() => {
                  setIsDropdownOpen(false)
                  logout()
                }}
                className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-destructive hover:bg-destructive/10"
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
