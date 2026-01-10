'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Zap, Flag, Star, Book, GitBranch, Circle, AlertTriangle } from 'lucide-react'

interface TimelineEvent {
  id: number
  event_type: string
  chapter_number: number
  title: string
  description?: string
  layer: string
  magnitude: number
  is_major_beat: boolean
  color?: string
  icon?: string
  tags: string[]
  related_characters: number[]
  is_custom: boolean
}

interface Conflict {
  id: number
  conflict_type: string
  severity: string
  chapter_start?: number
  chapter_end?: number
  title: string
}

interface InteractiveTimelineProps {
  events: TimelineEvent[]
  conflicts: Conflict[]
  filters: {
    layers: string[]
    onlyMajorBeats: boolean
  }
  onEventMove: (eventId: number, newChapter: number) => void
  onEventClick: (event: TimelineEvent) => void
}

const LAYER_COLORS: Record<string, string> = {
  plot: '#3B82F6',      // Blue
  character: '#8B5CF6',  // Purple
  theme: '#EC4899',      // Pink
  technical: '#6B7280',  // Gray
  consequence: '#F59E0B' // Orange
}

const LAYER_POSITIONS: Record<string, number> = {
  plot: 0,
  character: 1,
  theme: 2,
  technical: 3,
  consequence: 4
}

export default function InteractiveTimeline({
  events,
  conflicts,
  filters,
  onEventMove,
  onEventClick
}: InteractiveTimelineProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Viewport state
  const [zoom, setZoom] = useState(1.0)
  const [panX, setPanX] = useState(0)
  const [viewWidth, setViewWidth] = useState(0)
  const [viewHeight, setViewHeight] = useState(0)

  // Interaction state
  const [hoveredEvent, setHoveredEvent] = useState<TimelineEvent | null>(null)
  const [draggedEvent, setDraggedEvent] = useState<TimelineEvent | null>(null)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [isPanning, setIsPanning] = useState(false)
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 })

  // Calculate dimensions
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setViewWidth(containerRef.current.clientWidth)
        setViewHeight(containerRef.current.clientHeight)
      }
    }

    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  // Get chapter range
  const getChapterRange = (): [number, number] => {
    if (events.length === 0) return [1, 30]
    const chapters = events.map(e => e.chapter_number)
    return [Math.min(...chapters), Math.max(...chapters)]
  }

  const [minChapter, maxChapter] = getChapterRange()
  const chapterSpan = maxChapter - minChapter + 1

  // Convert chapter to X position
  const chapterToX = useCallback((chapter: number): number => {
    const padding = 80
    const usableWidth = viewWidth - (padding * 2)
    const normalized = (chapter - minChapter) / chapterSpan
    return padding + (normalized * usableWidth * zoom) + panX
  }, [minChapter, chapterSpan, viewWidth, zoom, panX])

  // Convert X position to chapter
  const xToChapter = useCallback((x: number): number => {
    const padding = 80
    const usableWidth = viewWidth - (padding * 2)
    const adjustedX = (x - padding - panX) / zoom
    const normalized = adjustedX / usableWidth
    return Math.round(minChapter + (normalized * chapterSpan))
  }, [minChapter, chapterSpan, viewWidth, zoom, panX])

  // Get Y position for layer
  const getLayerY = (layer: string): number => {
    const layerIndex = LAYER_POSITIONS[layer] || 0
    const layerHeight = 80
    const topPadding = 100
    return topPadding + (layerIndex * layerHeight)
  }

  // Draw timeline
  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    canvas.width = viewWidth
    canvas.height = viewHeight

    // Clear canvas
    ctx.clearRect(0, 0, viewWidth, viewHeight)

    // Draw background grid
    ctx.strokeStyle = '#E5E7EB'
    ctx.lineWidth = 1

    // Vertical lines for chapters
    for (let chapter = minChapter; chapter <= maxChapter; chapter++) {
      const x = chapterToX(chapter)
      if (x < 0 || x > viewWidth) continue

      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, viewHeight)
      ctx.stroke()

      // Chapter labels
      ctx.fillStyle = '#6B7280'
      ctx.font = '12px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(`Ch. ${chapter}`, x, 20)
    }

    // Draw layer separators and labels
    const layers = ['plot', 'character', 'theme', 'technical', 'consequence']
    layers.forEach((layer, index) => {
      if (!filters.layers.includes(layer)) return

      const y = getLayerY(layer)

      // Layer line
      ctx.strokeStyle = '#D1D5DB'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(0, y - 40)
      ctx.lineTo(viewWidth, y - 40)
      ctx.stroke()

      // Layer label
      ctx.fillStyle = LAYER_COLORS[layer]
      ctx.font = 'bold 14px sans-serif'
      ctx.textAlign = 'left'
      ctx.fillText(layer.charAt(0).toUpperCase() + layer.slice(1), 10, y - 20)
    })

    // Draw conflicts (as background highlights)
    conflicts.forEach(conflict => {
      if (!conflict.chapter_start || !conflict.chapter_end) return

      const x1 = chapterToX(conflict.chapter_start)
      const x2 = chapterToX(conflict.chapter_end)

      if (x2 < 0 || x1 > viewWidth) return

      const color = conflict.severity === 'critical' ? 'rgba(220, 38, 38, 0.1)' :
                    conflict.severity === 'error' ? 'rgba(239, 68, 68, 0.1)' :
                    conflict.severity === 'warning' ? 'rgba(245, 158, 11, 0.1)' :
                    'rgba(156, 163, 175, 0.1)'

      ctx.fillStyle = color
      ctx.fillRect(x1, 0, x2 - x1, viewHeight)

      // Conflict indicator at top
      ctx.fillStyle = conflict.severity === 'critical' ? '#DC2626' :
                     conflict.severity === 'error' ? '#EF4444' :
                     conflict.severity === 'warning' ? '#F59E0B' :
                     '#9CA3AF'
      ctx.fillRect(x1, 30, x2 - x1, 8)
    })

    // Filter and group events by chapter and layer
    const filteredEvents = events.filter(e =>
      filters.layers.includes(e.layer) &&
      (!filters.onlyMajorBeats || e.is_major_beat)
    )

    // Draw events
    filteredEvents.forEach(event => {
      const x = chapterToX(event.chapter_number)
      const y = getLayerY(event.layer)

      if (x < -50 || x > viewWidth + 50) return

      // Event circle
      const radius = event.is_major_beat ? 12 : 8
      const color = event.color || LAYER_COLORS[event.layer] || '#6B7280'

      // Glow for major beats
      if (event.is_major_beat) {
        ctx.shadowColor = color
        ctx.shadowBlur = 15
      }

      ctx.fillStyle = color
      ctx.beginPath()
      ctx.arc(x, y, radius, 0, Math.PI * 2)
      ctx.fill()

      ctx.shadowBlur = 0

      // Border
      ctx.strokeStyle = '#FFFFFF'
      ctx.lineWidth = 2
      ctx.stroke()

      // Hover effect
      if (hoveredEvent?.id === event.id) {
        ctx.strokeStyle = '#1F2937'
        ctx.lineWidth = 3
        ctx.beginPath()
        ctx.arc(x, y, radius + 3, 0, Math.PI * 2)
        ctx.stroke()
      }

      // Dragging effect
      if (draggedEvent?.id === event.id) {
        ctx.fillStyle = 'rgba(59, 130, 246, 0.2)'
        ctx.beginPath()
        ctx.arc(x, y, radius + 5, 0, Math.PI * 2)
        ctx.fill()
      }

      // Event label (for major beats)
      if (event.is_major_beat && zoom > 0.7) {
        ctx.fillStyle = '#1F2937'
        ctx.font = '11px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(
          event.title.length > 20 ? event.title.substring(0, 20) + '...' : event.title,
          x,
          y + radius + 15
        )
      }
    })

    // Draw dragged event preview
    if (draggedEvent) {
      const targetChapter = xToChapter(lastMousePos.x)
      const targetX = chapterToX(targetChapter)
      const targetY = getLayerY(draggedEvent.layer)

      // Ghost preview
      ctx.fillStyle = 'rgba(59, 130, 246, 0.3)'
      ctx.beginPath()
      ctx.arc(targetX, targetY, 12, 0, Math.PI * 2)
      ctx.fill()

      ctx.strokeStyle = '#3B82F6'
      ctx.lineWidth = 2
      ctx.setLineDash([5, 5])
      ctx.stroke()
      ctx.setLineDash([])

      // Target chapter indicator
      ctx.fillStyle = '#3B82F6'
      ctx.font = 'bold 14px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(`Move to Chapter ${targetChapter}`, targetX, targetY - 25)
    }

  }, [
    viewWidth,
    viewHeight,
    events,
    conflicts,
    filters,
    minChapter,
    maxChapter,
    zoom,
    panX,
    chapterToX,
    xToChapter,
    hoveredEvent,
    draggedEvent,
    lastMousePos
  ])

  // Redraw on changes
  useEffect(() => {
    draw()
  }, [draw])

  // Find event at position
  const getEventAtPosition = (x: number, y: number): TimelineEvent | null => {
    for (const event of events) {
      if (!filters.layers.includes(event.layer)) continue
      if (filters.onlyMajorBeats && !event.is_major_beat) continue

      const eventX = chapterToX(event.chapter_number)
      const eventY = getLayerY(event.layer)
      const radius = event.is_major_beat ? 12 : 8

      const distance = Math.sqrt(
        Math.pow(x - eventX, 2) + Math.pow(y - eventY, 2)
      )

      if (distance <= radius + 5) {
        return event
      }
    }
    return null
  }

  // Mouse handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return

    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const event = getEventAtPosition(x, y)

    if (event && event.is_custom) {
      // Start dragging custom event
      setDraggedEvent(event)
      setDragOffset({ x: x - chapterToX(event.chapter_number), y: 0 })
    } else if (e.button === 1 || e.ctrlKey) {
      // Middle click or Ctrl+click for panning
      setIsPanning(true)
      setLastMousePos({ x, y })
    }
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return

    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    setLastMousePos({ x, y })

    if (draggedEvent) {
      // Continue dragging
      return
    }

    if (isPanning) {
      // Pan viewport
      const dx = x - lastMousePos.x
      setPanX(prev => prev + dx)
      return
    }

    // Update hover state
    const event = getEventAtPosition(x, y)
    setHoveredEvent(event)

    // Update cursor
    if (canvasRef.current) {
      canvasRef.current.style.cursor = event ? 'pointer' : (isPanning ? 'grabbing' : 'default')
    }
  }

  const handleMouseUp = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (draggedEvent) {
      const rect = canvasRef.current?.getBoundingClientRect()
      if (!rect) return

      const x = e.clientX - rect.left
      const targetChapter = xToChapter(x)

      // Move event
      if (targetChapter !== draggedEvent.chapter_number) {
        onEventMove(draggedEvent.id, targetChapter)
      }

      setDraggedEvent(null)
    }

    if (isPanning) {
      setIsPanning(false)
    }
  }

  const handleClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (draggedEvent || isPanning) return

    const rect = canvasRef.current?.getBoundingClientRect()
    if (!rect) return

    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const event = getEventAtPosition(x, y)
    if (event) {
      onEventClick(event)
    }
  }

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault()

    const delta = e.deltaY > 0 ? 0.9 : 1.1
    const newZoom = Math.max(0.3, Math.min(3.0, zoom * delta))

    // Zoom towards mouse position
    const rect = canvasRef.current?.getBoundingClientRect()
    if (rect) {
      const mouseX = e.clientX - rect.left
      const worldX = (mouseX - panX) / zoom
      const newPanX = mouseX - (worldX * newZoom)
      setPanX(newPanX)
    }

    setZoom(newZoom)
  }

  return (
    <div ref={containerRef} className="w-full h-full relative">
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onClick={handleClick}
        onWheel={handleWheel}
        className="w-full h-full"
      />

      {/* Hover Tooltip */}
      {hoveredEvent && !draggedEvent && (
        <div
          className="absolute pointer-events-none bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg z-50 max-w-xs"
          style={{
            left: Math.min(lastMousePos.x + 10, viewWidth - 200),
            top: lastMousePos.y + 10
          }}
        >
          <div className="font-semibold mb-1">{hoveredEvent.title}</div>
          <div className="text-gray-300 text-xs">
            Chapter {hoveredEvent.chapter_number} • {hoveredEvent.layer}
          </div>
          {hoveredEvent.description && (
            <div className="text-gray-400 text-xs mt-1 line-clamp-2">
              {hoveredEvent.description}
            </div>
          )}
          {hoveredEvent.is_custom && (
            <div className="text-blue-400 text-xs mt-1">Custom event (draggable)</div>
          )}
        </div>
      )}

      {/* Zoom Indicator */}
      <div className="absolute top-4 right-4 bg-white rounded-lg shadow px-3 py-2 text-sm text-gray-700">
        Zoom: {(zoom * 100).toFixed(0)}%
      </div>
    </div>
  )
}
