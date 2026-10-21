import { Button, DatePicker, Form, Input, message } from 'antd'
import dayjs from 'dayjs'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../../api/client'
import type { ProfileData } from '../../types'

export default function ProfileInfoSection() {
  const [form] = Form.useForm()
  const [profile, setProfile] = useState<ProfileData | null>(null)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    const { data } = await api.get<ProfileData>('/api/profile')
    setProfile(data)
    form.setFieldsValue({
      ...data,
      date_of_birth: data.date_of_birth ? dayjs(data.date_of_birth) : null,
    })
  }

  useEffect(() => {
    load().catch(() => message.error('Không tải được hồ sơ.'))
  }, [])

  const save = async (values: any) => {
    setSaving(true)
    try {
      await api.put('/api/profile', {
        ...values,
        date_of_birth: values.date_of_birth?.format('YYYY-MM-DD') || null,
      })
      message.success('Đã cập nhật hồ sơ.')
      await load()
    } catch (error) {
      message.error(apiErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="profile-info-section">
      <div className="profile-readonly-note">
        <span className="profile-readonly-dot" />
        Email và vai trò chỉ hiển thị, không được sửa.
      </div>

      <Form form={form} layout="vertical" onFinish={save} className="profile-form-grid">
        <Form.Item
          label="Họ tên"
          name="full_name"
          rules={[{ required: true, message: 'Vui lòng nhập họ tên.' }]}
          className="profile-form-full"
        >
          <Input placeholder="Nhập họ tên" />
        </Form.Item>

        <Form.Item label="Email">
          <Input value={profile?.email} disabled />
        </Form.Item>

        <Form.Item label="Vai trò">
          <Input value={profile?.roles?.join(', ')} disabled />
        </Form.Item>

        <Form.Item
          label="Số điện thoại"
          name="phone"
          rules={[{ pattern: /^(0|\+84)(3|5|7|8|9)\d{8}$/, message: 'Số điện thoại Việt Nam không hợp lệ' }]}
        >
          <Input placeholder="Nhập số điện thoại" />
        </Form.Item>

        <Form.Item label="Ngày sinh" name="date_of_birth">
          <DatePicker format="DD/MM/YYYY" placeholder="Chọn ngày sinh" style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item label="Địa chỉ" name="address" className="profile-form-full">
          <Input.TextArea rows={4} placeholder="Nhập địa chỉ" autoSize={{ minRows: 4, maxRows: 6 }} />
        </Form.Item>

        <div className="profile-form-actions profile-form-full">
          <Button type="primary" htmlType="submit" loading={saving} size="large">
            Lưu hồ sơ
          </Button>
        </div>
      </Form>
    </div>
  )
}
