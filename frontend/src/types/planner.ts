// Planner types matching backend schemas

export interface BookArc {
  id: number
  project_id: number
  premise: string
  protagonist_goal: string
  central_conflict: string
  stakes: string
  act1_end: number
  midpoint: number
  act2_end: number
  climax: number
  resolution: string
  created_at: string
  updated_at: string
}

export interface Chapter {
  id: number
  project_id: number
  chapter_number: number
  title?: string
  summary: string
  pov_character?: string
  location?: string
  goals: string[]
  created_at: string
  updated_at: string
}

export interface Scene {
  id: number
  chapter_id: number
  project_id: number
  scene_number: number
  goal: string
  conflict?: string
  entering_value: string
  exiting_value: string
  what_changes: string
  participants: string[]
  prose?: string
  created_at: string
  updated_at: string
}

export interface ProjectStructure {
  book_arc?: BookArc
  chapters: Chapter[]
  scenes_by_chapter: Record<number, Scene[]>
}
