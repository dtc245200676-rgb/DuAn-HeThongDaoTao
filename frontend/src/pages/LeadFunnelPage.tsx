import {
  AppstoreOutlined,
  BookOutlined,
  ReloadOutlined,
  SearchOutlined,
  UnorderedListOutlined,
  UserOutlined,
} from '@ant-design/icons'
import {
  Button,
  Empty,
  Input,
  Segmented,
  Select,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
  message,
} from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import EntityCell from '../components/function-ui/EntityCell'
import FilterPanel from '../components/function-ui/FilterPanel'
import MetricStrip from '../components/function-ui/MetricStrip'
import SectionCard from '../components/function-ui/SectionCard'
import StatusTag from '../components/function-ui/StatusTag'
import type { LeadItem } from '../types'

type FunnelColumn = {
  status: string
  label: string
  count: number
  items: LeadItem[]
}

type FunnelLead = LeadItem & { funnel_status: string }
type ViewMode = 'board' | 'list'

const FUNNEL_STATUSES = [
  { value: 'new', label: 'Mới' },
  { value: 'contacted', label: 'Đã liên hệ' },
  { value: 'consulting', label: 'Đang tư vấn' },
  { value: 'trial', label: 'Hẹn học thử' },
  { value: 'closed', label: 'Chốt' },
  { value: 'rejected', label: 'Từ chối' },
]

function formatDate(value?: string | null) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('vi-VN')
}

export default function LeadFunnelPage() {
  const [columns, setColumns] = useState<FunnelColumn[]>([])
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('board')
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const [sourceFilter, setSourceFilter] = useState<string | undefined>()
  const [assigneeFilter, setAssigneeFilter] = useState<string | undefined>()

  const load = async () => {
    setLoading(true)
    try {
      const response = await api.get('/api/s3/funnel')
      setColumns(Array.isArray(response.data?.columns) ? response.data.columns : [])
    } catch (error) {
      message.error(apiErrorMessage(error, 'Không tải được phễu tuyển sinh.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const allLeads = useMemo<FunnelLead[]>(
    () => columns.flatMap(column =>
      (column.items || []).map(lead => ({ ...lead, funnel_status: column.status })),
    ),
    [columns],
  )

  const sourceOptions = useMemo(
    () => [...new Set(allLeads.map(lead => lead.source).filter((value): value is string => Boolean(value)))]
      .sort((a, b) => a.localeCompare(b, 'vi'))
      .map(value => ({ value, label: value })),
    [allLeads],
  )

  const assigneeOptions = useMemo(
    () => [...new Set(allLeads.map(lead => lead.assignee || 'Chưa phân công'))]
      .sort((a, b) => a.localeCompare(b, 'vi'))
      .map(value => ({ value, label: value })),
    [allLeads],
  )

  const filteredLeads = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase('vi-VN')

    return allLeads.filter(lead => {
      const searchableValues = [
        lead.full_name,
        lead.phone,
        lead.email,
        lead.interested_program,
      ]
      const matchesQuery = !normalizedQuery || searchableValues.some(value =>
        String(value || '').toLocaleLowerCase('vi-VN').includes(normalizedQuery),
      )
      const matchesStatus = !statusFilter || lead.funnel_status === statusFilter
      const matchesSource = !sourceFilter || lead.source === sourceFilter
      const matchesAssignee = !assigneeFilter || (lead.assignee || 'Chưa phân công') === assigneeFilter

      return matchesQuery && matchesStatus && matchesSource && matchesAssignee
    })
  }, [allLeads, query, statusFilter, sourceFilter, assigneeFilter])

  const filteredColumns = useMemo(
    () => columns.map(column => {
      const items = filteredLeads.filter(lead => lead.funnel_status === column.status)
      return { ...column, items, count: items.length }
    }),
    [columns, filteredLeads],
  )

  const resetFilters = () => {
    setQuery('')
    setStatusFilter(undefined)
    setSourceFilter(undefined)
    setAssigneeFilter(undefined)
  }

  const move = async (leadId: number, nextStatus: string) => {
    const current = allLeads.find(lead => lead.id === leadId)
    if (!current || current.funnel_status === nextStatus) return

    let rejection_reason: string | undefined
    if (nextStatus === 'rejected') {
      rejection_reason = window.prompt('Vui lòng nhập lý do từ chối lead:')?.trim()
      if (!rejection_reason) {
        message.warning('Từ chối lead bắt buộc phải có lý do.')
        return
      }
    }

    try {
      await api.patch(`/api/s3/funnel/leads/${leadId}/status`, {
        status: nextStatus,
        rejection_reason,
      })
      message.success('Đã cập nhật trạng thái và ghi nhật ký chuyển phễu.')
      await load()
    } catch (error) {
      message.error(apiErrorMessage(error, 'Không thể chuyển trạng thái lead.'))
    }
  }

  const metrics = [
    {
      label: 'Lead phù hợp bộ lọc',
      value: filteredLeads.length,
      hint: 'Tổng số lead đang hiển thị',
    },
    {
      label: 'Mới',
      value: filteredLeads.filter(lead => lead.funnel_status === 'new').length,
      hint: 'Cần liên hệ ban đầu',
    },
    {
      label: 'Đang xử lý',
      value: filteredLeads.filter(lead => ['contacted', 'consulting', 'trial'].includes(lead.funnel_status)).length,
      hint: 'Đã bắt đầu tư vấn',
    },
    {
      label: 'Đã chốt',
      value: filteredLeads.filter(lead => lead.funnel_status === 'closed').length,
      hint: 'Có thể chuyển thành học viên',
    },
  ]

  // AppLayout already renders the shared FeaturePage hero for this route.
  // Keep this page focused on its working content to avoid displaying a duplicate hero.
  return <>
    <MetricStrip items={metrics} />

    <FilterPanel
      title="Tìm kiếm và lọc lead"
      description="Lọc theo tên, số điện thoại, email, chương trình quan tâm, trạng thái hoặc người phụ trách."
      actions={(
        <Button
          icon={<ReloadOutlined />}
          onClick={() => {
            resetFilters()
            void load()
          }}
        >
          Đặt lại
        </Button>
      )}
    >
      <Input
        allowClear
        aria-label="Tìm kiếm lead"
        prefix={<SearchOutlined />}
        placeholder="Tìm tên, số điện thoại, email..."
        value={query}
        onChange={event => setQuery(event.target.value)}
        style={{ width: 280, maxWidth: '100%' }}
      />
      <Select
        allowClear
        aria-label="Lọc theo trạng thái"
        placeholder="Tất cả trạng thái"
        value={statusFilter}
        onChange={setStatusFilter}
        style={{ width: 180, maxWidth: '100%' }}
        options={FUNNEL_STATUSES}
      />
      <Select
        allowClear
        aria-label="Lọc theo nguồn lead"
        placeholder="Tất cả nguồn"
        value={sourceFilter}
        onChange={setSourceFilter}
        style={{ width: 165, maxWidth: '100%' }}
        options={sourceOptions}
      />
      <Select
        allowClear
        aria-label="Lọc theo người phụ trách"
        placeholder="Tất cả người phụ trách"
        value={assigneeFilter}
        onChange={setAssigneeFilter}
        style={{ width: 220, maxWidth: '100%' }}
        options={assigneeOptions}
      />
    </FilterPanel>

    <SectionCard
      title={viewMode === 'board' ? 'Bảng phễu tuyển sinh' : 'Danh sách lead'}
      subtitle={viewMode === 'board'
        ? 'Kéo thẻ sang cột khác để chuyển giai đoạn. Mỗi thay đổi được lưu vào lịch sử.'
        : `${filteredLeads.length} lead phù hợp với bộ lọc hiện tại. Có thể đổi trạng thái trực tiếp trong bảng.`}
      extra={(
        <Space wrap>
          <Segmented
            aria-label="Chế độ hiển thị phễu tuyển sinh"
            value={viewMode}
            onChange={value => setViewMode(value as ViewMode)}
            options={[
              { label: <Space size={6}><AppstoreOutlined />Bảng</Space>, value: 'board' },
              { label: <Space size={6}><UnorderedListOutlined />Danh sách</Space>, value: 'list' },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={() => void load()} loading={loading}>
            Làm mới
          </Button>
        </Space>
      )}
    >
      <Spin spinning={loading}>
        {viewMode === 'board' ? (
          <div className="lead-funnel-board-scroll">
            <div className="lead-funnel-columns">
              {filteredColumns.map(column => (
                <section
                  key={column.status}
                  className={`lead-funnel-column lead-funnel-column-${column.status}`}
                  aria-label={`Cột trạng thái ${column.label}`}
                  onDragOver={event => event.preventDefault()}
                  onDrop={event => {
                    event.preventDefault()
                    const leadId = Number(event.dataTransfer.getData('lead-id'))
                    if (leadId) void move(leadId, column.status)
                  }}
                >
                  <header className="lead-funnel-column-head">
                    <strong>{column.label}</strong>
                    <Tag>{column.count}</Tag>
                  </header>

                  <div className="lead-funnel-column-content">
                    {column.items.length === 0 ? (
                      <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Chưa có lead" />
                    ) : column.items.map(lead => (
                      <article
                        key={lead.id}
                        className="lead-funnel-lead-card"
                        draggable
                        tabIndex={0}
                        onDragStart={event => {
                          event.dataTransfer.setData('lead-id', String(lead.id))
                          event.dataTransfer.effectAllowed = 'move'
                        }}
                        title="Kéo thẻ sang cột khác để chuyển trạng thái"
                        aria-label={`${lead.full_name}, ${lead.phone}. Kéo sang cột khác để đổi trạng thái.`}
                      >
                        <div className="lead-funnel-lead-name">{lead.full_name}</div>
                        <div className="lead-funnel-lead-meta">{lead.phone || 'Chưa có số điện thoại'}</div>
                        {lead.interested_program && (
                          <div className="lead-funnel-program">
                            <BookOutlined />
                            <span>{lead.interested_program}</span>
                          </div>
                        )}
                        <div className="lead-funnel-card-footer">
                          <Tag color="blue">{lead.source || 'Chưa rõ nguồn'}</Tag>
                          <span><UserOutlined /> {lead.assignee || 'Chưa phân công'}</span>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>
              ))}
            </div>
          </div>
        ) : (
          <Table<FunnelLead>
            rowKey="id"
            dataSource={filteredLeads}
            scroll={{ x: 1250 }}
            pagination={{ pageSize: 10, showSizeChanger: true, showTotal: total => `Tổng ${total} lead` }}
            locale={{
              emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Không có lead phù hợp với bộ lọc." />,
            }}
            columns={[
              {
                title: 'Khách hàng',
                dataIndex: 'full_name',
                width: 230,
                render: (_, lead) => <EntityCell title={lead.full_name} subtitle={`Mã lead #${lead.id}`} />,
              },
              { title: 'Số điện thoại', dataIndex: 'phone', width: 145, render: value => value || '—' },
              {
                title: 'Chương trình quan tâm',
                dataIndex: 'interested_program',
                width: 190,
                render: value => value || '—',
              },
              {
                title: 'Nguồn',
                dataIndex: 'source',
                width: 125,
                render: value => <Tag color="blue">{value || 'Chưa rõ'}</Tag>,
              },
              {
                title: 'Người phụ trách',
                dataIndex: 'assignee',
                width: 170,
                render: value => value || 'Chưa phân công',
              },
              {
                title: 'Trạng thái',
                dataIndex: 'funnel_status',
                width: 145,
                render: value => <StatusTag value={value} />,
              },
              { title: 'Ngày tạo', dataIndex: 'created_at', width: 115, render: value => formatDate(value) },
              {
                title: 'Chuyển trạng thái',
                width: 190,
                fixed: 'right' as const,
                render: (_, lead) => (
                  <Select
                    size="middle"
                    aria-label={`Chuyển trạng thái cho ${lead.full_name}`}
                    value={lead.funnel_status}
                    options={FUNNEL_STATUSES}
                    onChange={status => void move(lead.id, status)}
                    style={{ width: 165 }}
                  />
                ),
              },
            ]}
          />
        )}
      </Spin>
      {viewMode === 'board' && filteredLeads.length === 0 && (
        <Typography.Paragraph type="secondary" className="lead-funnel-no-results">
          Không tìm thấy lead phù hợp. Hãy thử xóa bớt điều kiện lọc.
        </Typography.Paragraph>
      )}
    </SectionCard>
  </>
}
