import { PlusOutlined, ReloadOutlined, TeamOutlined } from '@ant-design/icons'
import { Button, Form, Input, Modal, Select, Space, Table, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import EntityCell from '../components/function-ui/EntityCell'
import FeaturePage from '../components/function-ui/FeaturePage'
import FilterPanel from '../components/function-ui/FilterPanel'
import SectionCard from '../components/function-ui/SectionCard'
import StatusTag from '../components/function-ui/StatusTag'
import AccountLockActions from '../features/users/AccountLockActions'
import UserRoleEditor from '../features/users/UserRoleEditor'
import type { RoleDetail, UserItem } from '../types'

const DRAFT_KEY = 'draft:user-management'

export default function UserManagementPage() {
  const { hasPermission } = useAuth()
  const [users, setUsers] = useState<UserItem[]>([])
  const [roles, setRoles] = useState<RoleDetail[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [q, setQ] = useState('')
  const [searchValue, setSearchValue] = useState('')
  const [role, setRole] = useState<string>()
  const [status, setStatus] = useState<string>()
  const [loading, setLoading] = useState(false)
  const [editUser, setEditUser] = useState<UserItem | null>(null)
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const loadRoles = async () => {
    if (!hasPermission('roles.view')) return
    const r = await api.get('/api/roles')
    setRoles(r.data.roles)
  }

  const loadUsers = async () => {
    setLoading(true)
    try {
      const r = await api.get('/api/users', { params: { q: q || undefined, role, status, page, page_size: 20 } })
      setUsers(r.data.items)
      setTotal(r.data.total)
    } catch (e) {
      message.error(apiErrorMessage(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadRoles().catch(() => undefined) }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { loadUsers() }, [page, role, status, q]) // eslint-disable-line react-hooks/exhaustive-deps

  const openCreate = () => {
    setEditUser(null)
    form.resetFields()
    const draft = sessionStorage.getItem(DRAFT_KEY)
    if (draft) {
      try { form.setFieldsValue(JSON.parse(draft)) } catch { /* ignore malformed local draft */ }
    }
    setOpen(true)
  }

  const openEdit = (u: UserItem) => {
    setEditUser(u)
    form.setFieldsValue({ full_name: u.full_name, email: u.email, phone: u.phone })
    setOpen(true)
  }

  const save = async () => {
    try {
      const v = await form.validateFields()
      if (editUser) {
        await api.put(`/api/users/${editUser.id}`, { full_name: v.full_name, email: v.email, phone: v.phone || null })
        message.success('Đã cập nhật người dùng')
      } else {
        const r = await api.post('/api/users', { ...v, role_slugs: v.role_slugs || ['student'] })
        message.success(`Đã tạo tài khoản.${r.data.debug_temporary_password ? ` Mật khẩu tạm (dev): ${r.data.debug_temporary_password}` : ''}`, 8)
        sessionStorage.removeItem(DRAFT_KEY)
      }
      setOpen(false)
      await loadUsers()
    } catch (e) {
      if ((e as { errorFields?: unknown }).errorFields) return
      message.error(apiErrorMessage(e))
    }
  }

  const resetFilters = () => {
    setSearchValue('')
    setQ('')
    setRole(undefined)
    setStatus(undefined)
    setPage(1)
  }

  const columns = useMemo<ColumnsType<UserItem>>(() => [
    {
      title: 'Người dùng',
      dataIndex: 'full_name',
      render: (_, r) => <EntityCell title={r.full_name} subtitle={r.email} />,
    },
    { title: 'Điện thoại', dataIndex: 'phone', responsive: ['md'], render: v => v || '—' },
    {
      title: 'Vai trò',
      render: (_, r) => <Space wrap>{r.roles.map(x => <Tag color="blue" key={x.slug}>{x.name}</Tag>)}</Space>,
    },
    { title: 'Trạng thái', dataIndex: 'status', render: v => <StatusTag value={v} /> },
    {
      title: 'Thao tác',
      fixed: 'right',
      render: (_, r) => <Space wrap>
        {hasPermission('users.update') && <Button size="small" onClick={() => openEdit(r)}>Sửa</Button>}
        <UserRoleEditor _user={r} _roles={roles} onSaved={loadUsers} />
        <AccountLockActions _user={r} onSaved={loadUsers} />
      </Space>,
    },
  ], [hasPermission, roles])

  return <FeaturePage
    eyebrow="Quản trị"
    title="Quản lý người dùng"
    description="Quản lý tài khoản, vai trò, trạng thái truy cập và thông tin liên hệ của người dùng trong hệ thống."
    icon={<TeamOutlined />}
    tone="violet"
    actions={hasPermission('users.create') ? <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Tạo tài khoản</Button> : undefined}
  >
    <FilterPanel
      title="Tìm kiếm & lọc"
      description="Thu hẹp danh sách theo thông tin tài khoản, vai trò hoặc trạng thái."
      actions={<Button icon={<ReloadOutlined />} onClick={resetFilters}>Đặt lại</Button>}
    >
      <Input.Search
        placeholder="Tên, email hoặc số điện thoại"
        allowClear
        value={searchValue}
        onChange={e => setSearchValue(e.target.value)}
        onSearch={v => { setQ(v.trim()); setPage(1) }}
        style={{ width: 320 }}
      />
      <Select
        allowClear
        placeholder="Vai trò"
        value={role}
        style={{ minWidth: 190 }}
        options={roles.map(r => ({ label: r.name, value: r.slug }))}
        onChange={v => { setRole(v); setPage(1) }}
      />
      <Select
        allowClear
        placeholder="Trạng thái"
        value={status}
        style={{ minWidth: 175 }}
        options={[
          { value: 'active', label: 'Hoạt động' },
          { value: 'pending', label: 'Chờ kích hoạt' },
          { value: 'locked', label: 'Đã khóa' },
        ]}
        onChange={v => { setStatus(v); setPage(1) }}
      />
      <Button type="primary" onClick={() => { setQ(searchValue.trim()); setPage(1) }}>Áp dụng bộ lọc</Button>
    </FilterPanel>

    <SectionCard
      title="Danh sách người dùng"
      subtitle={`${total} tài khoản phù hợp với điều kiện hiện tại.`}
      extra={<Button icon={<ReloadOutlined />} onClick={loadUsers}>Làm mới</Button>}
    >
      <Table
        rowKey="id"
        loading={loading}
        columns={columns}
        dataSource={users}
        scroll={{ x: 900 }}
        pagination={{ current: page, pageSize: 20, total, showSizeChanger: false, onChange: setPage }}
      />
    </SectionCard>

    <Modal title={editUser ? 'Cập nhật người dùng' : 'Tạo tài khoản'} open={open} onCancel={() => setOpen(false)} onOk={save}>
      <Form
        form={form}
        layout="vertical"
        onValuesChange={(_, all) => { if (!editUser) sessionStorage.setItem(DRAFT_KEY, JSON.stringify(all)) }}
      >
        <Form.Item name="full_name" label="Họ tên" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="email" label="Email" rules={[{ required: true }, { type: 'email' }]}><Input /></Form.Item>
        <Form.Item name="phone" label="Số điện thoại"><Input /></Form.Item>
        {!editUser && <Form.Item name="role_slugs" label="Vai trò" initialValue={['student']}><Select mode="multiple" options={roles.map(r => ({ label: r.name, value: r.slug }))} /></Form.Item>}
      </Form>
    </Modal>
  </FeaturePage>
}
