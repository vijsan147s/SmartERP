import { cn } from '@/lib/utils'

interface PageHeaderProps {
  title: string
  description?: string
  action?: React.ReactNode
  secondaryAction?: React.ReactNode
  className?: string
}

export function PageHeader({ title, description, action, secondaryAction, className }: PageHeaderProps) {
  return (
    <div className={cn('flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between', className)}>
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">{title}</h1>
        {description && <p className="text-sm text-muted-foreground">{description}</p>}
      </div>
      {(action || secondaryAction) && (
        <div className="flex items-center gap-3">
          {secondaryAction}
          {action}
        </div>
      )}
    </div>
  )
}
