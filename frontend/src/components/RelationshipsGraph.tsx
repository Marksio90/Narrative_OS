'use client'

import { useEffect, useRef, useState } from 'react'
import { Users, ZoomIn, ZoomOut, Maximize2, X } from 'lucide-react'

interface Character {
  id: number
  name: string
  relationships?: {
    [characterName: string]: {
      type: string
      description?: string
      strength?: number
    }
  }
}

interface Node {
  id: number
  name: string
  x: number
  y: number
  vx: number
  vy: number
  fx?: number
  fy?: number
}

interface Edge {
  source: number
  target: number
  type: string
  description?: string
  strength: number
}

interface RelationshipsGraphProps {
  characters: Character[]
  onClose: () => void
}

export default function RelationshipsGraph({ characters, onClose }: RelationshipsGraphProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [draggedNode, setDraggedNode] = useState<Node | null>(null)
  const [isPanning, setIsPanning] = useState(false)
  const [lastMouse, setLastMouse] = useState({ x: 0, y: 0 })

  // Build graph data from characters
  useEffect(() => {
    const graphNodes: Node[] = characters.map((char, idx) => ({
      id: char.id,
      name: char.name,
      x: Math.cos(idx * (Math.PI * 2) / characters.length) * 200,
      y: Math.sin(idx * (Math.PI * 2) / characters.length) * 200,
      vx: 0,
      vy: 0,
    }))

    const graphEdges: Edge[] = []
    const characterMap = new Map(characters.map(c => [c.name, c.id]))

    characters.forEach(char => {
      if (char.relationships) {
        Object.entries(char.relationships).forEach(([targetName, rel]) => {
          const targetId = characterMap.get(targetName)
          if (targetId && targetId !== char.id) {
            // Avoid duplicate edges
            const exists = graphEdges.some(
              e => (e.source === char.id && e.target === targetId) ||
                   (e.source === targetId && e.target === char.id)
            )
            if (!exists) {
              graphEdges.push({
                source: char.id,
                target: targetId,
                type: rel.type,
                description: rel.description,
                strength: rel.strength || 5,
              })
            }
          }
        })
      }
    })

    setNodes(graphNodes)
    setEdges(graphEdges)
  }, [characters])

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
            const force = 200 / (dist * dist)

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
            const targetDist = 150
            const force = (dist - targetDist) * 0.1

            source.vx += (dx / dist) * force
            source.vy += (dy / dist) * force
            target.vx -= (dx / dist) * force
            target.vy -= (dy / dist) * force
          }
        })

        // Center force
        const centerX = 0
        const centerY = 0
        newNodes.forEach(node => {
          const dx = centerX - node.x
          const dy = centerY - node.y
          node.vx += dx * 0.01
          node.vy += dy * 0.01
        })

        // Apply velocities
        newNodes.forEach(node => {
          if (!node.fx && !node.fy) {
            node.x += node.vx
            node.y += node.vy
            node.vx *= 0.8
            node.vy *= 0.8
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

    // Draw edges
    edges.forEach(edge => {
      const source = nodes.find(n => n.id === edge.source)
      const target = nodes.find(n => n.id === edge.target)
      if (source && target) {
        ctx.beginPath()
        ctx.moveTo(source.x, source.y)
        ctx.lineTo(target.x, target.y)
        ctx.strokeStyle = getEdgeColor(edge.type)
        ctx.lineWidth = edge.strength / 2
        ctx.stroke()

        // Draw arrow
        const angle = Math.atan2(target.y - source.y, target.x - source.x)
        const arrowSize = 8
        const midX = (source.x + target.x) / 2
        const midY = (source.y + target.y) / 2

        ctx.save()
        ctx.translate(midX, midY)
        ctx.rotate(angle)
        ctx.beginPath()
        ctx.moveTo(-arrowSize, -arrowSize / 2)
        ctx.lineTo(0, 0)
        ctx.lineTo(-arrowSize, arrowSize / 2)
        ctx.strokeStyle = getEdgeColor(edge.type)
        ctx.lineWidth = 2
        ctx.stroke()
        ctx.restore()
      }
    })

    // Draw nodes
    nodes.forEach(node => {
      const isSelected = selectedNode?.id === node.id

      // Node circle
      ctx.beginPath()
      ctx.arc(node.x, node.y, isSelected ? 32 : 28, 0, Math.PI * 2)
      ctx.fillStyle = isSelected ? '#6366f1' : '#8b5cf6'
      ctx.fill()
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 3
      ctx.stroke()

      // Node label
      ctx.fillStyle = '#fff'
      ctx.font = 'bold 12px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(node.name.substring(0, 12), node.x, node.y)

      // Full name below if selected
      if (isSelected) {
        ctx.fillStyle = '#1f2937'
        ctx.font = 'bold 14px sans-serif'
        ctx.fillText(node.name, node.x, node.y + 50)
      }
    })

    ctx.restore()

    const animationFrame = requestAnimationFrame(() => {})
    return () => cancelAnimationFrame(animationFrame)
  }, [nodes, edges, zoom, pan, selectedNode])

  const getEdgeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      ally: '#10b981',
      friend: '#3b82f6',
      family: '#8b5cf6',
      enemy: '#ef4444',
      rival: '#f59e0b',
      mentor: '#14b8a6',
      romance: '#ec4899',
      neutral: '#6b7280',
    }
    return colors[type.toLowerCase()] || '#6b7280'
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
      return Math.sqrt(dx * dx + dy * dy) < 28
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

  const getLegendItems = () => {
    const types = new Set(edges.map(e => e.type))
    return Array.from(types).map(type => ({
      type,
      color: getEdgeColor(type),
      label: type.charAt(0).toUpperCase() + type.slice(1)
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full h-full max-w-7xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
              <Users className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Graf Relacji Postaci</h2>
              <p className="text-sm text-gray-600">
                {nodes.length} postaci, {edges.length} relacji
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
        <div ref={containerRef} className="flex-1 relative overflow-hidden bg-gradient-to-br from-slate-50 to-indigo-50">
          <canvas
            ref={canvasRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onWheel={handleWheel}
            className="w-full h-full cursor-move"
          />

          {/* Legend */}
          {edges.length > 0 && (
            <div className="absolute top-4 left-4 bg-white bg-opacity-95 rounded-lg shadow-lg p-4 max-w-xs">
              <h3 className="text-sm font-bold text-gray-900 mb-3">Typy Relacji</h3>
              <div className="space-y-2">
                {getLegendItems().map(item => (
                  <div key={item.type} className="flex items-center space-x-2">
                    <div
                      className="w-8 h-1 rounded"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-xs text-gray-700">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Selected Node Info */}
          {selectedNode && (
            <div className="absolute bottom-4 right-4 bg-white bg-opacity-95 rounded-lg shadow-lg p-4 max-w-sm">
              <h3 className="text-lg font-bold text-gray-900 mb-2">{selectedNode.name}</h3>
              <div className="space-y-2">
                {edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).map((edge, idx) => {
                  const otherNodeId = edge.source === selectedNode.id ? edge.target : edge.source
                  const otherNode = nodes.find(n => n.id === otherNodeId)
                  return (
                    <div key={idx} className="flex items-start space-x-2 text-sm">
                      <div
                        className="w-3 h-3 rounded-full mt-0.5 flex-shrink-0"
                        style={{ backgroundColor: getEdgeColor(edge.type) }}
                      />
                      <div>
                        <span className="font-medium text-gray-900">{otherNode?.name}</span>
                        <span className="text-gray-500"> • {edge.type}</span>
                        {edge.description && (
                          <p className="text-xs text-gray-600 mt-1">{edge.description}</p>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Instructions */}
          {nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Users className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">Brak postaci z relacjami</p>
                <p className="text-sm mt-2">Dodaj relacje do postaci w edytorze postaci</p>
              </div>
            </div>
          )}

          {nodes.length > 0 && (
            <div className="absolute bottom-4 left-4 bg-white bg-opacity-90 rounded-lg shadow-md p-3 text-xs text-gray-600">
              <p>💡 <strong>Przeciągnij</strong> węzły aby przesunąć</p>
              <p>🔍 <strong>Scroll</strong> aby zoom</p>
              <p>👆 <strong>Kliknij tło</strong> aby panoramować</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
