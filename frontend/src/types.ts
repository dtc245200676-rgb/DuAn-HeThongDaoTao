export interface CurrentUser {
  id: number
  full_name: string
  email: string
  phone?: string | null
  date_of_birth?: string | null
  address?: string | null
  avatar_url?: string | null
  avatar_thumbnail_url?: string | null
  roles: string[]
  permissions: string[]
  must_change_password: boolean
}

export interface RoleBrief {
  id: number
  slug: string
  name: string
}

export interface UserItem {
  id: number
  full_name: string
  email: string
  phone?: string | null
  status: 'active' | 'pending' | 'locked' | string
  is_active: boolean
  must_change_password: boolean
  needs_handover: boolean
  roles: RoleBrief[]
  created_at: string
}

export interface PermissionItem {
  id: number
  code: string
  name: string
}

export interface RoleDetail extends RoleBrief {
  description?: string | null
  permissions: PermissionItem[]
}

export interface ProfileData {
  id: number
  full_name: string
  email: string
  phone?: string | null
  date_of_birth?: string | null
  address?: string | null
  avatar_url?: string | null
  avatar_thumbnail_url?: string | null
  roles: string[]
}

export interface TrainingProgramItem {
  id: number
  code: string
  name: string
  description?: string | null
  total_duration_hours: number
  standard_tuition: number
  status: string
}

export interface SubjectItem {
  id: number
  code: string
  name: string
  session_count: number
  weight: number
  description?: string | null
  learning_outcomes?: string | null
}

export interface LeadItem {
  id: number
  full_name: string
  phone: string
  email?: string | null
  source?: string | null
  interested_program_id?: number | null
  interested_program?: string | null
  status: string
  assignee_user_id?: number | null
  assignee?: string | null
  note?: string | null
  created_at: string
}

export interface StudentProfileItem {
  id: number
  student_code: string
  user_id: number
  full_name: string
  email: string
  phone?: string | null
  date_of_birth?: string | null
  address?: string | null
  entry_level?: string | null
  notes?: string | null
  current_classes: string[]
  class_history: string[]
}

export interface TrainingClassItem {
  id: number
  code: string
  program_id: number
  program_name: string
  expected_start_date?: string | null
  max_students: number
  delivery_mode: string
  status: string
  current_students: number
  completed_sessions: number
  total_sessions: number
  room_id?: number | null
  room_name?: string | null
}

export interface TrainingRoomItem {
  id: number
  code: string
  name: string
  room_type: 'physical' | 'online'
  capacity?: number | null
  online_url?: string | null
  is_active: boolean
}
