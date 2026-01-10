'use client'

import { useEffect, useRef, useState } from 'react'
import { GitBranch, ZoomIn, ZoomOut, Maximize2, X, Filter } from 'lucide-react'

interface StoryEvent {
  id: number
  title: string
  event_type: string
  magnitude: number
  chapter_number?: number
}

interface Consequence {
  id: number
  source_event_id: number
  target_event_id?: number
  description: string
  probability: number
  severity: number
  timeframe: string
  status: string
  plot_impact?: string
}

interface GraphNode {
  id: number
  type: 'event' | 'consequence'
  data: StoryEvent | Consequence
  x: number
  y: number
  vx: number
  vy: number
  fx?: number
  fy?: number
}

interface GraphEdge {
  source: number
  target: number
  consequence: Consequence
}

interface ConsequenceGraphProps {
  events: StoryEvent[]
  consequences: Consequence[]
  onClose: () => void
}

export default function ConsequenceGraph({ events, consequences, onClose }: ConsequenceGraphProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [draggedNode, setDraggedNode] = useState<GraphNode | null>(null)
  const [isPanning, setIsPanning] = useState(false)
  const [lastMouse, setLastMouse] = useState({ x: 0, y: 0 })
  const [filter, setFilter] = useState({
    showPotential: true,
    showActive: true,
    showRealized: true,
    showInvalidated: false,
  })

  // Build graph data from events and consequences
  useEffect(() => {
    // Create event nodes
    const eventNodes: GraphNode[] = events.map((event, idx) => ({
      id: event.id,
      type: 'event' as const,
      data: event,
      x: (idx % 5) * 250 - 500,
      y: Math.floor(idx / 5) * 200 - 300,
      vx: 0,
      vy: 0,
    }))

    // Create edges from consequences
    const graphEdges: GraphEdge[] = []
    consequences.forEach(cons => {
      // Filter based on status
      if (!filter.showPotential && cons.status === 'potential') return
      if (!filter.showActive && cons.status === 'active') return
      if (!filter.showRealized && cons.status === 'realized') return
      if (!filter.showInvalidated && cons.status === 'invalidated') return

      const sourceNode = eventNodes.find(n => n.id === cons.source_event_id)

      if (sourceNode && cons.target_event_id) {
        // Realized consequence - connect to target event
        const targetNode = eventNodes.find(n => n.id === cons.target_event_id)
        if (targetNode) {
          graphEdges.push({
            source: cons.source_event_id,
            target: cons.target_event_id,
            consequence: cons,
          })
        }
      }
    })

    setNodes(eventNodes)
    setEdges(graphEdges)
  }, [events, consequences, filter])

  // Force simulation
  useEffect(() => {
    if (nodes.length === 0) return

    const interval = setInterval(() => {
      setNodes(prevNodes => {
        const newNodes = prevNodes.map(node => ({ ...node }))

        // Repulsion between nodes
        for (let i = 0; i < newNodes.length; i++) {
          for (let j = i + 1; j < newNodes.length; j++) {
            const dx = newNodes[j].x - newNodes[i].x
            const dy = newNodes[j].y - newNodes[i].y
            const dist = Math.sqrt(dx * dx + dy * dy) || 1
            const force = 300 / (dist * dist)

            newNodes[i].vx -= (dx / dist) * force
            newNodes[i].vy -= (dy / dist) * force
            newNodes[j].vx += (dx / dist) * force
            newNodes[j].vy += (dy / dist) * force
          }
        }

        // Spring force along edges
        edges.forEach(edge => {
          const source = newNodes.find(n => n.id === edge.source)
          const target = newNodes.find(n => n.id === edge.target)
          if (source && target) {
            const dx = target.x - source.x
            const dy = target.y - source.y
            const dist = Math.sqrt(dx * dx + dy * dy) || 1
            const targetDist = 200
            const force = (dist - targetDist) * 0.08

            source.vx += (dx / dist) * force
            source.vy += (dy / dist) * force
            target.vx -= (dx / dist) * force
            target.vy -= (dy / dist) * force
          }
        })

        // Center force
        newNodes.forEach(node => {
          node.vx -= node.x * 0.005
          node.vy -= node.y * 0.005
        })

        // Apply velocities with damping
        newNodes.forEach(node => {
          if (!node.fx && !node.fy) {
            node.x += node.vx
            node.y += node.vy
            node.vx *= 0.85
            node.vy *= 0.85
          }
        })

        return newNodes
      })
    }, 50)

    return () => clearInterval(interval)
  }, [nodes.length, edges])

  // Render graph
  useEffect(() => {
    const canvas = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const rect = container.getBoundingClientRect()
    canvas.width = rect.width * window.devicePixelRatio
    canvas.height = rect.height * window.devicePixelRatio
    canvas.style.width = `${rect.width}px`
    canvas.style.height = `${rect.height}px`
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio)

    // Clear
    ctx.clearRect(0, 0, rect.width, rect.height)

    // Apply transform
    ctx.save()
    ctx.translate(rect.width / 2 + pan.x, rect.height / 2 + pan.y)
    ctx.scale(zoom, zoom)

    // Draw edges (consequences)
    edges.forEach(edge => {
      const source = nodes.find(n => n.id === edge.source)
      const target = nodes.find(n => n.id === edge.target)
      if (source && target) {
        const cons = edge.consequence

        // Calculate curve control point for better visualization
        const midX = (source.x + target.x) / 2
        const midY = (source.y + target.y) / 2
        const dx = target.x - source.x
        const dy = target.y - source.y
        const offset = 30
        const controlX = midX - dy * 0.2
        const controlY = midY + dx * 0.2

        // Draw curved line
        ctx.beginPath()
        ctx.moveTo(source.x, source.y)
        ctx.quadraticCurveTo(controlX, controlY, target.x, target.y)
        ctx.strokeStyle = getConsequenceColor(cons.status)
        ctx.lineWidth = Math.max(1, cons.probability * 5)
        ctx.globalAlpha = cons.status === 'invalidated' ? 0.3 : 0.8
        ctx.stroke()
        ctx.globalAlpha = 1

        // Draw arrow at target
        const angle = Math.atan2(target.y - controlY, target.x - controlX)
        const arrowSize = 12

        ctx.save()
        ctx.translate(target.x, target.y)
        ctx.rotate(angle)
        ctx.beginPath()
        ctx.moveTo(-arrowSize, -arrowSize / 2)
        ctx.lineTo(0, 0)
        ctx.lineTo(-arrowSize, arrowSize / 2)
        ctx.strokeStyle = getConsequenceColor(cons.status)
        ctx.lineWidth = 2
        ctx.stroke()
        ctx.restore()

        // Draw consequence label if probability is high
        if (cons.probability > 0.6 && cons.status !== 'invalidated') {
          ctx.fillStyle = '#1f2937'
          ctx.font = '10px sans-serif'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillText(
            `${Math.round(cons.probability * 100)}%`,
            controlX,
            controlY
          )
        }
      }
    })

    // Draw unrealized consequences (floating near source event)
    consequences.forEach(cons => {
      if (cons.target_event_id || !filter.showPotential && cons.status === 'potential') return
      if (cons.status === 'invalidated' && !filter.showInvalidated) return

      const sourceNode = nodes.find(n => n.id === cons.source_event_id)
      if (!sourceNode) return

      // Position consequence indicator near source
      const angle = cons.id * 0.8
      const radius = 80
      const x = sourceNode.x + Math.cos(angle) * radius
      const y = sourceNode.y + Math.sin(angle) * radius

      // Draw connection line
      ctx.beginPath()
      ctx.moveTo(sourceNode.x, sourceNode.y)
      ctx.lineTo(x, y)
      ctx.strokeStyle = getConsequenceColor(cons.status)
      ctx.lineWidth = 1
      ctx.setLineDash([5, 5])
      ctx.globalAlpha = 0.5
      ctx.stroke()
      ctx.setLineDash([])
      ctx.globalAlpha = 1

      // Draw consequence bubble
      const size = 8 + cons.severity * 12
      ctx.beginPath()
      ctx.arc(x, y, size, 0, Math.PI * 2)
      ctx.fillStyle = getConsequenceColor(cons.status)
      ctx.globalAlpha = cons.probability
      ctx.fill()
      ctx.globalAlpha = 1
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 2
      ctx.stroke()

      // Severity indicator (inner circle)
      if (cons.severity > 0.7) {
        ctx.beginPath()
        ctx.arc(x, y, size * 0.5, 0, Math.PI * 2)
        ctx.fillStyle = '#fff'
        ctx.fill()
      }
    })

    // Draw event nodes
    nodes.forEach(node => {
      const event = node.data as StoryEvent
      const isSelected = selectedNode?.id === node.id

      // Node background circle
      const radius = isSelected ? 40 : 35
      ctx.beginPath()
      ctx.arc(node.x, node.y, radius, 0, Math.PI * 2)

      // Color based on event type
      const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, radius)
      const eventColor = getEventTypeColor(event.event_type)
      gradient.addColorStop(0, eventColor)
      gradient.addColorStop(1, adjustColor(eventColor, -30))

      ctx.fillStyle = gradient
      ctx.fill()
      ctx.strokeStyle = isSelected ? '#fbbf24' : '#fff'
      ctx.lineWidth = isSelected ? 4 : 3
      ctx.stroke()

      // Magnitude indicator (ring)
      if (event.magnitude > 0.6) {
        ctx.beginPath()
        ctx.arc(node.x, node.y, radius + 5, 0, Math.PI * 2)
        ctx.strokeStyle = eventColor
        ctx.lineWidth = 2
        ctx.globalAlpha = event.magnitude
        ctx.stroke()
        ctx.globalAlpha = 1
      }

      // Event title
      ctx.fillStyle = '#fff'
      ctx.font = isSelected ? 'bold 11px sans-serif' : 'bold 10px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      // Wrap text if too long
      const maxWidth = radius * 1.8
      const title = event.title.length > 15 ? event.title.substring(0, 13) + '...' : event.title
      ctx.fillText(title, node.x, node.y)

      // Chapter number
      if (event.chapter_number) {
        ctx.fillStyle = 'rgba(255,255,255,0.8)'
        ctx.font = '8px sans-serif'
        ctx.fillText(`Ch ${event.chapter_number}`, node.x, node.y - radius - 8)
      }

      // Full title below if selected
      if (isSelected) {
        ctx.fillStyle = '#1f2937'
        ctx.font = 'bold 12px sans-serif'
        const bgPadding = 8
        const textWidth = ctx.measureText(event.title).width

        ctx.fillStyle = 'rgba(255,255,255,0.95)'
        ctx.fillRect(
          node.x - textWidth / 2 - bgPadding,
          node.y + radius + 10,
          textWidth + bgPadding * 2,
          20
        )

        ctx.fillStyle = '#1f2937'
        ctx.fillText(event.title, node.x, node.y + radius + 20)
      }
    })

    ctx.restore()
  }, [nodes, edges, consequences, zoom, pan, selectedNode, filter])

  const getEventTypeColor = (type: string): string => {
    const colors: { [key: string]: string } = {
      decision: '#3b82f6',      // blue
      revelation: '#8b5cf6',    // purple
      conflict: '#ef4444',      // red
      resolution: '#10b981',    // green
      relationship: '#ec4899',  // pink
      discovery: '#f59e0b',     // amber
      loss: '#6b7280',          // gray
      transformation: '#14b8a6', // teal
    }
    return colors[type.toLowerCase()] || '#6366f1'
  }

  const getConsequenceColor = (status: string): string => {
    const colors: { [key: string]: string } = {
      potential: '#8b5cf6',     // purple
      active: '#f59e0b',        // amber
      realized: '#10b981',      // green
      invalidated: '#6b7280',   // gray
    }
    return colors[status.toLowerCase()] || '#6b7280'
  }

  const adjustColor = (color: string, amount: number): string => {
    const num = parseInt(color.replace('#', ''), 16)
    const r = Math.max(0, Math.min(255, (num >> 16) + amount))
    const g = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amount))
    const b = Math.max(0, Math.min(255, (num & 0x0000FF) + amount))
    return `#${((r << 16) | (g << 8) | b).toString(16).padStart(6, '0')}`
  }

  // Mouse handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = ((e.clientX - rect.left - rect.width / 2 - pan.x) / zoom)
    const y = ((e.clientY - rect.top - rect.height / 2 - pan.y) / zoom)

    // Check if clicked on a node
    const clickedNode = nodes.find(node => {
      const dx = node.x - x
      const dy = node.y - y
      return Math.sqrt(dx * dx + dy * dy) < 35
    })

    if (clickedNode) {
      setDraggedNode(clickedNode)
      setSelectedNode(clickedNode)
    } else {
      setIsPanning(true)
      setSelectedNode(null)
    }

    setLastMouse({ x: e.clientX, y: e.clientY })
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (draggedNode) {
      const canvas = canvasRef.current
      if (!canvas) return

      const rect = canvas.getBoundingClientRect()
      const x = ((e.clientX - rect.left - rect.width / 2 - pan.x) / zoom)
      const y = ((e.clientY - rect.top - rect.height / 2 - pan.y) / zoom)

      setNodes(prevNodes =>
        prevNodes.map(node =>
          node.id === draggedNode.id
            ? { ...node, x, y, fx: x, fy: y, vx: 0, vy: 0 }
            : node
        )
      )
    } else if (isPanning) {
      const dx = e.clientX - lastMouse.x
      const dy = e.clientY - lastMouse.y
      setPan(prev => ({ x: prev.x + dx, y: prev.y + dy }))
      setLastMouse({ x: e.clientX, y: e.clientY })
    }
  }

  const handleMouseUp = () => {
    if (draggedNode) {
      setNodes(prevNodes =>
        prevNodes.map(node =>
          node.id === draggedNode.id
            ? { ...node, fx: undefined, fy: undefined }
            : node
        )
      )
    }
    setDraggedNode(null)
    setIsPanning(false)
  }

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    setZoom(prev => Math.max(0.3, Math.min(3, prev * delta)))
  }

  const resetView = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  const getRelatedConsequences = (eventId: number) => {
    return consequences.filter(c =>
      c.source_event_id === eventId || c.target_event_id === eventId
    )
  }

  const getStats = () => {
    const potential = consequences.filter(c => c.status === 'potential').length
    const active = consequences.filter(c => c.status === 'active').length
    const realized = consequences.filter(c => c.status === 'realized').length
    const highProb = consequences.filter(c => c.probability > 0.7 && c.status !== 'invalidated').length

    return { potential, active, realized, highProb }
  }

  const stats = getStats()

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full h-full max-w-7xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
              <GitBranch className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Graf Konsekwencji</h2>
              <p className="text-sm text-gray-600">
                {events.length} wydarzeń, {consequences.length} konsekwencji
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setZoom(prev => Math.min(3, prev * 1.2))}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              title="Przybliż"
            >
              <ZoomIn className="h-5 w-5" />
            </button>
            <button
              onClick={() => setZoom(prev => Math.max(0.3, prev * 0.8))}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              title="Oddal"
            >
              <ZoomOut className="h-5 w-5" />
            </button>
            <button
              onClick={resetView}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
              title="Resetuj widok"
            >
              <Maximize2 className="h-5 w-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Graph Canvas */}
        <div ref={containerRef} className="flex-1 relative overflow-hidden bg-gradient-to-br from-slate-50 to-purple-50">
          <canvas
            ref={canvasRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onWheel={handleWheel}
            className="w-full h-full cursor-move"
          />

          {/* Filter Controls */}
          <div className="absolute top-4 left-4 bg-white bg-opacity-95 rounded-lg shadow-lg p-4 max-w-xs">
            <div className="flex items-center space-x-2 mb-3">
              <Filter className="h-4 w-4 text-gray-600" />
              <h3 className="text-sm font-bold text-gray-900">Filtry Statusu</h3>
            </div>
            <div className="space-y-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filter.showPotential}
                  onChange={(e) => setFilter(f => ({ ...f, showPotential: e.target.checked }))}
                  className="rounded text-purple-600"
                />
                <div className="w-3 h-3 rounded-full bg-purple-500" />
                <span className="text-xs text-gray-700">Potencjalne ({stats.potential})</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filter.showActive}
                  onChange={(e) => setFilter(f => ({ ...f, showActive: e.target.checked }))}
                  className="rounded text-amber-600"
                />
                <div className="w-3 h-3 rounded-full bg-amber-500" />
                <span className="text-xs text-gray-700">Aktywne ({stats.active})</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filter.showRealized}
                  onChange={(e) => setFilter(f => ({ ...f, showRealized: e.target.checked }))}
                  className="rounded text-green-600"
                />
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-xs text-gray-700">Zrealizowane ({stats.realized})</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filter.showInvalidated}
                  onChange={(e) => setFilter(f => ({ ...f, showInvalidated: e.target.checked }))}
                  className="rounded text-gray-600"
                />
                <div className="w-3 h-3 rounded-full bg-gray-400" />
                <span className="text-xs text-gray-700">Unieważnione</span>
              </label>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="text-xs text-gray-600 space-y-1">
                <div className="flex justify-between">
                  <span>Wysokie prawdopodobieństwo:</span>
                  <span className="font-bold text-purple-600">{stats.highProb}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="absolute top-4 right-4 bg-white bg-opacity-95 rounded-lg shadow-lg p-4 max-w-xs">
            <h3 className="text-sm font-bold text-gray-900 mb-3">Typy Wydarzeń</h3>
            <div className="grid grid-cols-2 gap-2">
              {['decision', 'revelation', 'conflict', 'resolution', 'relationship', 'discovery'].map(type => (
                <div key={type} className="flex items-center space-x-2">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: getEventTypeColor(type) }}
                  />
                  <span className="text-xs text-gray-700 capitalize">{type}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Selected Event Info */}
          {selectedNode && (
            <div className="absolute bottom-4 right-4 bg-white bg-opacity-95 rounded-lg shadow-lg p-4 max-w-sm max-h-96 overflow-y-auto">
              <div className="mb-3">
                <h3 className="text-lg font-bold text-gray-900">{(selectedNode.data as StoryEvent).title}</h3>
                <p className="text-xs text-gray-500 mt-1">
                  Typ: <span className="font-medium">{(selectedNode.data as StoryEvent).event_type}</span>
                  {(selectedNode.data as StoryEvent).chapter_number && (
                    <> • Rozdział {(selectedNode.data as StoryEvent).chapter_number}</>
                  )}
                </p>
                <div className="mt-2">
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-purple-500"
                        style={{ width: `${(selectedNode.data as StoryEvent).magnitude * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-600">Znaczenie</span>
                  </div>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-3">
                <h4 className="text-sm font-bold text-gray-900 mb-2">Konsekwencje</h4>
                <div className="space-y-2">
                  {getRelatedConsequences(selectedNode.id).map((cons, idx) => (
                    <div key={idx} className="text-xs bg-gray-50 rounded p-2">
                      <div className="flex items-start space-x-2">
                        <div
                          className="w-3 h-3 rounded-full mt-0.5 flex-shrink-0"
                          style={{ backgroundColor: getConsequenceColor(cons.status) }}
                        />
                        <div className="flex-1">
                          <p className="text-gray-900 font-medium">{cons.description}</p>
                          <div className="flex items-center space-x-3 mt-1 text-gray-600">
                            <span>📊 {Math.round(cons.probability * 100)}%</span>
                            <span>⚡ {Math.round(cons.severity * 100)}%</span>
                            <span className="capitalize">{cons.timeframe.replace('_', ' ')}</span>
                          </div>
                          {cons.plot_impact && (
                            <p className="text-gray-500 mt-1 italic">{cons.plot_impact}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  {getRelatedConsequences(selectedNode.id).length === 0 && (
                    <p className="text-gray-500 text-xs italic">Brak konsekwencji dla tego wydarzenia</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Instructions */}
          {events.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <GitBranch className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">Brak wydarzeń</p>
                <p className="text-sm mt-2">Przeanalizuj sceny aby wyodrębnić wydarzenia</p>
              </div>
            </div>
          )}

          {events.length > 0 && (
            <div className="absolute bottom-4 left-4 bg-white bg-opacity-90 rounded-lg shadow-md p-3 text-xs text-gray-600">
              <p>💡 <strong>Przeciągnij</strong> wydarzenia aby przesunąć</p>
              <p>🔍 <strong>Scroll</strong> aby zoom</p>
              <p>👆 <strong>Kliknij tło</strong> aby panoramować</p>
              <p className="mt-1 text-purple-600">● Większe bąbelki = wyższa dotkliwość</p>
              <p className="text-purple-600">● Szersze linie = wyższe prawdopodobieństwo</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
