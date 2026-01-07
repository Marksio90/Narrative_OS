// Canon entity types matching backend schemas

export interface Character {
  id: number
  project_id: number
  name: string
  description?: string
  goals: string[]
  voice_profile: Record<string, any>
  behavioral_limits: string[]
  claims: Record<string, any>
  unknowns: string[]
  canon_version_id?: number
  created_at: string
  updated_at: string
}

export interface Location {
  id: number
  project_id: number
  name: string
  description?: string
  geography: Record<string, any>
  atmosphere: string
  accessibility: string[]
  claims: Record<string, any>
  unknowns: string[]
  canon_version_id?: number
  created_at: string
  updated_at: string
}

export interface Faction {
  id: number
  project_id: number
  name: string
  description?: string
  goals: string[]
  power_structure: Record<string, any>
  relationships: Record<string, any>
  claims: Record<string, any>
  unknowns: string[]
  canon_version_id?: number
  created_at: string
  updated_at: string
}

export interface MagicRule {
  id: number
  project_id: number
  name: string
  description?: string
  constraints: string[]
  cost: string
  exceptions: string[]
  claims: Record<string, any>
  unknowns: string[]
  canon_version_id?: number
  created_at: string
  updated_at: string
}

export interface Item {
  id: number
  project_id: number
  name: string
  description?: string
  properties: Record<string, any>
  history?: string
  current_owner?: string
  claims: Record<string, any>
  unknowns: string[]
  canon_version_id?: number
  created_at: string
  updated_at: string
}

export interface Event {
  id: number
  project_id: number
  name: string
  description?: string
  when: string
  where?: string
  participants: string[]
  consequences: string[]
  claims: Record<string, any>
  unknowns: string[]
  canon_version_id?: number
  created_at: string
  updated_at: string
}

export interface CanonContract {
  id: number
  project_id: number
  name: string
  description?: string
  rule: string
  severity: 'must' | 'should' | 'prefer'
  entity_type?: string
  entity_id?: number
  active: boolean
  created_at: string
  updated_at: string
}

export interface Promise {
  id: number
  project_id: number
  setup: string
  chapter_introduced: number
  payoff_required: string
  status: 'open' | 'fulfilled' | 'abandoned'
  confidence: number
  payoff_deadline?: number
  payoff_chapter?: number
  created_at: string
  updated_at: string
}

export type CanonEntityType =
  | 'character'
  | 'location'
  | 'faction'
  | 'magic_rule'
  | 'item'
  | 'event'

export interface ContractViolation {
  contract_id: number
  contract_name: string
  severity: string
  violated_text: string
  reason: string
  suggested_fix?: string
}
