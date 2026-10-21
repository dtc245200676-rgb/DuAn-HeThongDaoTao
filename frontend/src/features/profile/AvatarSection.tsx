import { CameraOutlined, LoadingOutlined } from '@ant-design/icons'
import { Avatar, Upload, message } from 'antd'
import type { UploadFile } from 'antd'
import { useState } from 'react'
import { api, apiErrorMessage } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001'

export default function AvatarSection() {
  const { user, refreshMe } = useAuth()
  const [busy, setBusy] = useState(false)

  const upload = async ({ file, onSuccess, onError }: any) => {
    const raw = file as UploadFile & { originFileObj?: File }
    const actual = raw.originFileObj || (file as File)

    if (!['image/jpeg', 'image/png'].includes(actual.type)) {
      message.error('Chỉ hỗ trợ ảnh JPG hoặc PNG.')
      onError?.(new Error('invalid file type'))
      return
    }

    if (actual.size > 2 * 1024 * 1024) {
      message.error('Ảnh tối đa 2MB.')
      onError?.(new Error('too large'))
      return
    }

    setBusy(true)
    const formData = new FormData()
    formData.append('file', actual)

    try {
      await api.post('/api/profile/avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      await refreshMe()
      message.success('Đã cập nhật ảnh đại diện.')
      onSuccess?.({})
    } catch (error) {
      message.error(apiErrorMessage(error))
      onError?.(error)
    } finally {
      setBusy(false)
    }
  }

  const displayName = user?.full_name || 'Người dùng'
  const initial = (displayName || user?.email || 'U').trim().charAt(0).toUpperCase()
  const avatarUrl = user?.avatar_thumbnail_url
    ? `${API_BASE}${user.avatar_thumbnail_url}`
    : undefined

  return (
    <aside className="profile-premium-card profile-identity-card">
      <div className="profile-identity-body">
        <Upload
          customRequest={upload}
          showUploadList={false}
          accept="image/jpeg,image/png"
          disabled={busy}
          className="profile-avatar-upload"
        >
          <button
            type="button"
            className="profile-avatar-trigger"
            aria-label="Đổi ảnh đại diện"
            disabled={busy}
          >
            <Avatar size={140} src={avatarUrl} className="profile-premium-avatar">
              {initial}
            </Avatar>

            <span className="profile-camera-button" aria-hidden="true">
              {busy ? <LoadingOutlined /> : <CameraOutlined />}
            </span>
          </button>
        </Upload>

        <h2 className="profile-identity-name">{displayName}</h2>
        <p className="profile-identity-email">{user?.email}</p>

        <div className="profile-avatar-help">
          <CameraOutlined />
          <div>
            <strong>Đổi ảnh đại diện</strong>
            <span>Nhấn vào ảnh hoặc biểu tượng camera. Hỗ trợ JPG/PNG tối đa 2MB.</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
