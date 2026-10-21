import { HistoryOutlined, ReloadOutlined, TeamOutlined } from '@ant-design/icons'
import { Button, DatePicker, Drawer, Input, Select, Table, Tag, message } from 'antd'
import type { Key } from 'react'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import ActionBar from '../components/function-ui/ActionBar'
import EntityCell from '../components/function-ui/EntityCell'
import FeaturePage from '../components/function-ui/FeaturePage'
import FilterPanel from '../components/function-ui/FilterPanel'
import SectionCard from '../components/function-ui/SectionCard'
import StatusTag from '../components/function-ui/StatusTag'
import type { LeadItem, UserItem } from '../types'

const { RangePicker } = DatePicker

export default function LeadAssignmentPage() {
  const { hasPermission } = useAuth()
  const [items, setItems] = useState<LeadItem[]>([])
  const [users, setUsers] = useState<UserItem[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState<string | undefined>()
  const [source, setSource] = useState<string | undefined>()
  const [assignee, setAssignee] = useState<number | undefined>()
  const [range, setRange] = useState<any>(null)
  const [assignTo, setAssignTo] = useState<number | undefined>()
  const [selected, setSelected] = useState<Key[]>([])
  const [history, setHistory] = useState<any[]>([])
  const [historyOpen, setHistoryOpen] = useState(false)

  const load = async () => {
    const params: Record<string, unknown> = { q }
    if (status) params.status = status
    if (source) params.source = source
    if (assignee) params.assignee_user_id = assignee
    if (range?.[0]) params.created_from = range[0].format('YYYY-MM-DDT00:00:00')
    if (range?.[1]) params.created_to = range[1].format('YYYY-MM-DDT23:59:59')
    setItems((await api.get('/api/leads', { params })).data.items)
  }

  useEffect(() => {
    load().catch(() => message.error('Không tải được lead.'))
    api.get('/api/users', { params: { role: 'admissions', page_size: 100 } }).then(r => setUsers(r.data.items)).catch(() => undefined)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const assign = async () => {
    if (!selected.length || !assignTo) return message.warning('Chọn ít nhất một lead và người phụ trách.')
    try {
      await api.post('/api/leads/assign', { lead_ids: selected, assignee_user_id: assignTo })
      message.success(`Đã phân công ${selected.length} lead.`)
      setSelected([])
      await load()
    } catch (e) {
      message.error(apiErrorMessage(e))
    }
  }

  const showHistory = async (id: number) => {
    try {
      setHistory((await api.get(`/api/leads/${id}/assignment-history`)).data)
      setHistoryOpen(true)
    } catch (e) {
      message.error(apiErrorMessage(e))
    }
  }

  const resetFilters = async () => {
    setQ('')
    setStatus(undefined)
    setSource(undefined)
    setAssignee(undefined)
    setRange(null)
    const data = (await api.get('/api/leads', { params: {} })).data.items
    setItems(data)
  }

  return <FeaturePage
    eyebrow="Tuyển sinh"
    title="Phân công & lọc lead"
    description="Tìm kiếm lead theo nhiều tiêu chí và phân bổ nhanh cho nhân viên tuyển sinh phù hợp."
    icon={<TeamOutlined />}
    tone="cyan"
  >
    <FilterPanel
      title="Bộ lọc lead"
      description="Kết hợp nhiều điều kiện để tìm nhanh đúng nhóm khách hàng cần xử lý."
      actions={<Button icon={<ReloadOutlined />} onClick={() => void resetFilters()}>Đặt lại</Button>}
    >
      <Input.Search placeholder="Tìm tên hoặc số điện thoại" value={q} onChange={e => setQ(e.target.value)} onSearch={() => void load()} style={{ width: 260 }} />
      <Select placeholder="Trạng thái" allowClear value={status} onChange={setStatus} style={{ width: 165 }} options={['new', 'contacted', 'qualified', 'closed'].map(x => ({ value: x, label: x }))} />
      <Select placeholder="Nguồn" allowClear value={source} onChange={setSource} style={{ width: 165 }} options={['website', 'facebook', 'referral', 'other'].map(x => ({ value: x, label: x }))} />
      <Select placeholder="Người phụ trách" allowClear value={assignee} onChange={setAssignee} style={{ width: 220 }} options={users.map(u => ({ value: u.id, label: u.full_name || u.email }))} />
      <RangePicker value={range} onChange={setRange} />
      <Button type="primary" onClick={() => void load()}>Lọc dữ liệu</Button>
    </FilterPanel>

    {hasPermission('leads.assign') && <ActionBar
      selectedCount={selected.length}
      description={selected.length ? 'Chọn nhân viên tuyển sinh và xác nhận để cập nhật người phụ trách.' : 'Tick các lead trong bảng để kích hoạt thao tác phân công.'}
    >
      <Select placeholder="Phân công cho tư vấn viên" value={assignTo} onChange={setAssignTo} style={{ width: 250 }} options={users.map(u => ({ value: u.id, label: u.full_name || u.email }))} />
      <Button type="primary" onClick={() => void assign()} disabled={!selected.length || !assignTo}>Phân công ngay</Button>
    </ActionBar>}

    <SectionCard title="Danh sách lead" subtitle={`${items.length} lead đang hiển thị theo điều kiện lọc hiện tại.`}>
      <Table
        rowKey="id"
        rowSelection={{ selectedRowKeys: selected, onChange: setSelected }}
        dataSource={items}
        scroll={{ x: 900 }}
        columns={[
          { title: 'Khách hàng', dataIndex: 'full_name', render: (_, r) => <EntityCell title={r.full_name} /> },
          { title: 'SĐT', dataIndex: 'phone' },
          { title: 'Nguồn', dataIndex: 'source', render: v => <Tag color="blue">{v || '—'}</Tag> },
          { title: 'Trạng thái', dataIndex: 'status', render: v => <StatusTag value={v} /> },
          { title: 'Phụ trách', dataIndex: 'assignee', render: v => v || 'Chưa phân công' },
          { title: 'Thao tác', render: (_, r) => <Button icon={<HistoryOutlined />} size="small" onClick={() => void showHistory(r.id)}>Lịch sử giao</Button> },
        ]}
      />
    </SectionCard>

    <Drawer title="Lịch sử chuyển giao lead" open={historyOpen} onClose={() => setHistoryOpen(false)} width={560}>
      <Table
        rowKey="id"
        pagination={false}
        dataSource={history}
        columns={[
          { title: 'Từ', dataIndex: 'from_user', render: v => v || 'Chưa giao' },
          { title: 'Đến', dataIndex: 'to_user' },
          { title: 'Người giao', dataIndex: 'actor_user' },
          { title: 'Thời gian', dataIndex: 'created_at' },
        ]}
      />
    </Drawer>
  </FeaturePage>
}
