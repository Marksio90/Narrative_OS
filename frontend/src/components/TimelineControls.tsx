'use client'

import { useState } from 'react'
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Move } from 'lucide-react'

interface TimelineControlsProps {
  zoom?: number
  onZoomIn?: () => void
  onZoomOut?: () => void
  onResetView?: () => void
  onFitToView?: () => void
}

export default function TimelineControls({
  zoom = 1.0,
  onZoomIn,
  onZoomOut,
  onResetView,
  onFitToView
}: TimelineControlsProps) {
  const [showHint, setShowHint] = useState(false)

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-2">
      <div className="flex items-center gap-1">
        {/* Zoom Out */}
        <button
          onClick={onZoomOut}
          className="p-2 hover:bg-gray-100 rounded transition-colors group relative"
          title="Zoom Out"
        >
          <ZoomOut className="w-5 h-5 text-gray-700" />
        </button>

        {/* Zoom Display */}
        <div className="px-3 py-1 bg-gray-50 rounded min-w-[60px] text-center">
          <span className="text-sm font-medium text-gray-700">
            {(zoom * 100).toFixed(0)}%
          </span>
        </div>

        {/* Zoom In */}
        <button
          onClick={onZoomIn}
          className="p-2 hover:bg-gray-100 rounded transition-colors group relative"
          title="Zoom In"
        >
          <ZoomIn className="w-5 h-5 text-gray-700" />
        </button>

        {/* Divider */}
        <div className="w-px h-6 bg-gray-300 mx-1" />

        {/* Fit to View */}
        <button
          onClick={onFitToView}
          className="p-2 hover:bg-gray-100 rounded transition-colors group relative"
          title="Fit to View"
        >
          <Maximize2 className="w-5 h-5 text-gray-700" />
        </button>

        {/* Reset View */}
        <button
          onClick={onResetView}
          className="p-2 hover:bg-gray-100 rounded transition-colors group relative"
          title="Reset View"
        >
          <RotateCcw className="w-5 h-5 text-gray-700" />
        </button>

        {/* Divider */}
        <div className="w-px h-6 bg-gray-300 mx-1" />

        {/* Pan Hint */}
        <button
          onMouseEnter={() => setShowHint(true)}
          onMouseLeave={() => setShowHint(false)}
          className="p-2 hover:bg-gray-100 rounded transition-colors relative"
        >
          <Move className="w-5 h-5 text-gray-500" />

          {showHint && (
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 bg-gray-900 text-white text-xs rounded-lg px-3 py-2 shadow-lg z-50">
              <div className="font-semibold mb-1">Navigation Tips:</div>
              <ul className="space-y-1 text-gray-300">
                <li>• Scroll: Zoom in/out</li>
                <li>• Ctrl+Drag: Pan view</li>
                <li>• Drag events: Move chapters</li>
              </ul>
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                <div className="border-4 border-transparent border-t-gray-900" />
              </div>
            </div>
          )}
        </button>
      </div>
    </div>
  )
}
