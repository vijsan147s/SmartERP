import { useState, useMemo } from 'react'
import { ChevronUp, ChevronDown, ChevronsUpDown, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

export interface Column<T> {
  key: string
  header: string
  sortable?: boolean
  className?: string
  render?: (item: T, index: number) => React.ReactNode
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyField?: string
  pageSize?: number
  onRowClick?: (item: T) => void
  emptyMessage?: string
}

type SortDirection = 'asc' | 'desc' | null

export function DataTable<T extends object>({
  columns,
  data,
  keyField = 'id',
  pageSize = 10,
  onRowClick,
  emptyMessage = 'No data available',
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>(null)
  const [currentPage, setCurrentPage] = useState(1)

  const handleSort = (key: string) => {
    if (sortKey === key) {
      if (sortDirection === 'asc') setSortDirection('desc')
      else if (sortDirection === 'desc') {
        setSortKey(null)
        setSortDirection(null)
      }
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  const sortedData = useMemo(() => {
    if (!sortKey || !sortDirection) return data
    return [...data].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortKey]
      const bVal = (b as Record<string, unknown>)[sortKey]
      if (aVal == null && bVal == null) return 0
      if (aVal == null) return 1
      if (bVal == null) return -1
      const comparison = String(aVal).localeCompare(String(bVal), undefined, { numeric: true })
      return sortDirection === 'asc' ? comparison : -comparison
    })
  }, [data, sortKey, sortDirection])

  const totalPages = Math.ceil(sortedData.length / pageSize)
  const paginatedData = sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  const renderSortIcon = (key: string) => {
    if (sortKey !== key) return <ChevronsUpDown className="ml-1 h-3 w-3 opacity-50" />
    return sortDirection === 'asc'
      ? <ChevronUp className="ml-1 h-3 w-3" />
      : <ChevronDown className="ml-1 h-3 w-3" />
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">{emptyMessage}</div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    'px-4 py-3 text-left font-medium text-muted-foreground',
                    col.sortable && 'cursor-pointer select-none hover:text-foreground',
                    col.className
                  )}
                  onClick={() => col.sortable && handleSort(col.key)}
                >
                  <div className="flex items-center">
                    {col.header}
                    {col.sortable && renderSortIcon(col.key)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((item, index) => (
              <tr
                key={String((item as Record<string, unknown>)[keyField])}
                className={cn(
                  'border-b last:border-b-0 hover:bg-muted/50 transition-colors',
                  onRowClick && 'cursor-pointer'
                )}
                onClick={() => onRowClick?.(item)}
              >
                {columns.map((col) => (
                  <td key={col.key} className={cn('px-4 py-3', col.className)}>
                    {col.render
                      ? col.render(item, (currentPage - 1) * pageSize + index)
                      : String((item as Record<string, unknown>)[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {currentPage} of {totalPages}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
