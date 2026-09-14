import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  text?: string
}

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
}

export function LoadingSpinner({ size = 'md', className, text }: LoadingSpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <Loader2 className={cn('animate-spin text-primary', sizeMap[size])} />
      {text && <p className="text-sm text-muted-foreground">{text}</p>}
    </div>
  )
}

export function PageLoader({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex h-[50vh] items-center justify-center">
      <LoadingSpinner size="lg" text={text} />
    </div>
  )
}

export function InlineLoader() {
  return (
    <div className="flex items-center justify-center p-8">
      <LoadingSpinner size="md" />
    </div>
  )
}
