import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary/10 text-primary',
        success: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
        warning: 'bg-amber-50 text-amber-700 border border-amber-200',
        destructive: 'bg-red-50 text-red-700 border border-red-200',
        info: 'bg-blue-50 text-blue-700 border border-blue-200',
        secondary: 'bg-muted text-muted-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

interface StatusBadgeProps extends VariantProps<typeof badgeVariants> {
  label: string
  className?: string
}

export function StatusBadge({ label, variant, className }: StatusBadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)}>
      {label}
    </span>
  )
}

export function getStatusVariant(status: string): 'success' | 'warning' | 'destructive' | 'info' | 'secondary' {
  const s = status.toUpperCase()
  if (['ACTIVE', 'APPROVED', 'PAID', 'COMPLETED', 'PRESENT'].includes(s)) return 'success'
  if (['PENDING', 'IN_PROGRESS', 'INACTIVE'].includes(s)) return 'warning'
  if (['CANCELLED', 'REJECTED', 'FAILED', 'ABSENT'].includes(s)) return 'destructive'
  if (['DRAFT', 'SUBMITTED', 'PROCESSING'].includes(s)) return 'info'
  return 'secondary'
}

export function StatusIndicator({ status }: { status: string }) {
  const variant = getStatusVariant(status)
  const dotColors: Record<string, string> = {
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    destructive: 'bg-red-500',
    info: 'bg-blue-500',
    secondary: 'bg-gray-400',
  }
  return (
    <div className="flex items-center gap-2">
      <span className={cn('h-2 w-2 rounded-full', dotColors[variant])} />
      <span className="text-sm">{status}</span>
    </div>
  )
}
