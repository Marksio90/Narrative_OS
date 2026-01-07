// Draft generation types

export type DraftStatus =
  | 'pending'
  | 'generating'
  | 'passed'
  | 'needs_regeneration'
  | 'rejected'

export interface ExtractedFact {
  category: string
  fact: string
  confidence: number
  source_quote: string
}

export interface QCIssue {
  type: 'blocker' | 'warning' | 'suggestion'
  editor: string
  message: string
  quote?: string
  suggestion?: string
}

export interface QCReport {
  passed: boolean
  score: number
  issues: QCIssue[]
  breakdown: {
    continuity: number
    character: number
    plot: number
  }
}

export interface SceneDraft {
  scene_id: number
  prose: string
  status: DraftStatus
  extracted_facts: ExtractedFact[]
  detected_promises: any[]
  qc_report?: QCReport
  created_at: string
  updated_at: string
}

export interface ChapterDraft {
  chapter_id: number
  prose: string
  scenes: SceneDraft[]
  accumulated_facts: ExtractedFact[]
  qc_report?: QCReport
  created_at: string
  updated_at: string
}
