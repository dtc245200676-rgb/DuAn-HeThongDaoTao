import {
  BellOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  PhoneOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { Alert, Button, DatePicker, Empty, Form, Input, List, Select, Space, Table, Tag, Typography, message } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import EntityCell from '../components/function-ui/EntityCell'
import FeaturePage from '../components/function-ui/FeaturePage'
import MetricStrip from '../components/function-ui/MetricStrip'
import SectionCard from '../components/function-ui/SectionCard'
import type { LeadItem } from '../types'

type Interaction = {
  id: number
  lead_id: number
  interaction_type: string
  content: string
  occurred_at: string
  reminder_at?: string | null
  is_overdue: boolean
  reminder_completed_at?: string | null
  created_by?: string | null
}

type ReminderItem = Interaction & {
  lead_name: string
  lead_phone: string
}

const interactionLabels: Record<string, string> = {
  call: 'Gọi điện',
  message: 'Nhắn tin',
  meeting: 'Gặp trực tiếp',
}

function formatDateTime(value?: string | null) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString('vi-VN', { dateStyle: 'short', timeStyle: 'short' })
}

export default function LeadCarePage() {
  const [leads, setLeads] = useState<LeadItem[]>([])
  const [leadId, setLeadId] = useState<number>()
  const [items, setItems] = useState<Interaction[]>([])
  const [reminders, setReminders] = useState<ReminderItem[]>([])
  const [loadingLeads, setLoadingLeads] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [loadingReminders, setLoadingReminders] = useState(false)
  const [form] = Form.useForm()

  const activeLeads = useMemo(() => leads.filter(lead => lead.status !== 'enrolled'), [leads])
  const overdueReminders = useMemo(() => reminders.filter(item => item.is_overdue), [reminders])
  const overdueLeadCount = useMemo(() => new Set(overdueReminders.map(item => item.lead_id)).size, [overdueReminders])
  const selectedLead = activeLeads.find(lead => lead.id === leadId)

  const loadLeads = async () => {
    setLoadingLeads(true)
    try {
      const response = await api.get('/api/leads', { params: { page_size: 100 } })
      setLeads(response.data.items || [])
    } catch (e) {
      message.error(apiErrorMessage(e, 'Không tải được danh sách lead.'))
    } finally {
      setLoadingLeads(false)
    }
  }

  const loadInteractions = async (id?: number) => {
    if (!id) {
      setItems([])
      return
    }
    setLoadingHistory(true)
    try {
      const response = await api.get(`/api/s3/care/leads/${id}/interactions`)
      setItems(response.data || [])
    } catch (e) {
      message.error(apiErrorMessage(e, 'Không tải được lịch sử chăm sóc.'))
    } finally {
      setLoadingHistory(false)
    }
  }

  const loadReminders = async () => {
    setLoadingReminders(true)
    try {
      const response = await api.get('/api/s3/care/reminders')
      setReminders(response.data || [])
    } catch (e) {
      message.error(apiErrorMessage(e, 'Không tải được lịch nhắc gọi lại.'))
    } finally {
      setLoadingReminders(false)
    }
  }

  useEffect(() => {
    void loadLeads()
    void loadReminders()
  }, [])

  const refreshAll = async () => {
    await Promise.all([loadLeads(), loadReminders(), loadInteractions(leadId)])
  }

  const submit = async (values: { interaction_type: string; content: string; reminder_at?: { toISOString: () => string } | null }) => {
    if (!leadId) {
      message.warning('Hãy chọn lead trước khi ghi nhận tương tác.')
      return
    }
    const content = values.content?.trim()
    if (!content) {
      message.warning('Nội dung chăm sóc không được để trống.')
      return
    }
    try {
      await api.post(`/api/s3/care/leads/${leadId}/interactions`, {
        interaction_type: values.interaction_type,
        content,
        reminder_at: values.reminder_at?.toISOString() || null,
      })
      message.success('Đã lưu tương tác và cập nhật lịch chăm sóc.')
      form.resetFields()
      await Promise.all([loadInteractions(leadId), loadReminders()])
    } catch (e) {
      message.error(apiErrorMessage(e, 'Không thể lưu tương tác chăm sóc.'))
    }
  }

  const completeReminder = async (id: number) => {
    try {
      await api.patch(`/api/s3/care/interactions/${id}/complete-reminder`)
      message.success('Đã hoàn tất lịch nhắc gọi lại.')
      await Promise.all([loadInteractions(leadId), loadReminders()])
    } catch (e) {
      message.error(apiErrorMessage(e, 'Không thể hoàn tất lịch nhắc.'))
    }
  }

  const metrics = [
    { label: 'Lead có thể chăm sóc', value: activeLeads.length, hint: 'Không bao gồm lead đã nhập học' },
    { label: 'Lịch nhắc đang mở', value: reminders.length, hint: 'Đang chờ xử lý' },
    { label: 'Lead quá hạn', value: overdueLeadCount, hint: 'Tính theo khách hàng, không đếm trùng' },
    { label: 'Tương tác trong hồ sơ', value: items.length, hint: selectedLead ? selectedLead.full_name : 'Chọn lead để xem lịch sử' },
  ]

  return <FeaturePage
    eyebrow="Tuyển sinh"
    title="Chăm sóc lead"
    description="Ghi nhận cuộc gọi, tin nhắn và buổi tư vấn; quản lý lịch gọi lại để hạn chế bỏ sót khách hàng tiềm năng."
    icon={<PhoneOutlined />}
    tone="cyan"
    actions={<Button icon={<ReloadOutlined />} onClick={() => void refreshAll()} loading={loadingLeads || loadingReminders}>Làm mới dữ liệu</Button>}
  >
    <MetricStrip items={metrics} />

    {overdueLeadCount > 0 && <Alert
      type="warning"
      showIcon
      icon={<BellOutlined />}
      message={`${overdueLeadCount} khách hàng có lịch gọi lại quá hạn`}
      description={`${overdueReminders.length} lịch nhắc cần xử lý. Hoàn tất từng lịch sau khi đã liên hệ khách hàng.`}
    />}

    <SectionCard title="Ghi nhận tương tác" subtitle="Mỗi lần gọi, nhắn tin hoặc tư vấn cần có nội dung cụ thể và lịch gọi lại nếu cần.">
      <Form form={form} layout="vertical" onFinish={submit}>
        <Form.Item label="Khách hàng / lead" required>
          <Select
            showSearch
            optionFilterProp="label"
            placeholder="Tìm và chọn lead cần chăm sóc"
            value={leadId}
            loading={loadingLeads}
            onChange={id => {
              setLeadId(id)
              void loadInteractions(id)
            }}
            options={activeLeads.map(lead => ({ value: lead.id, label: `${lead.full_name} · ${lead.phone}` }))}
            style={{ width: '100%', maxWidth: 560 }}
            notFoundContent={<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Không có lead phù hợp" />}
          />
        </Form.Item>
        {selectedLead && <div className="lead-care-selected-lead">
          <EntityCell title={selectedLead.full_name} subtitle={`${selectedLead.phone}${selectedLead.interested_program ? ` · Quan tâm: ${selectedLead.interested_program}` : ''}`} />
          <span className="lead-care-selected-status">{selectedLead.assignee ? `Phụ trách: ${selectedLead.assignee}` : 'Chưa phân công'}</span>
        </div>}
        <div className="lead-care-form-grid">
          <Form.Item name="interaction_type" label="Hình thức tương tác" rules={[{ required: true, message: 'Chọn hình thức tương tác.' }]}>
            <Select placeholder="Chọn hình thức" options={[
              { value: 'call', label: 'Gọi điện' },
              { value: 'message', label: 'Nhắn tin' },
              { value: 'meeting', label: 'Gặp trực tiếp' },
            ]} />
          </Form.Item>
          <Form.Item name="reminder_at" label="Nhắc gọi lại (không bắt buộc)">
            <DatePicker showTime format="DD/MM/YYYY HH:mm" placeholder="Chọn ngày và giờ" style={{ width: '100%' }} suffixIcon={<CalendarOutlined />} />
          </Form.Item>
        </div>
        <Form.Item name="content" label="Nội dung trao đổi" rules={[{ required: true, whitespace: true, message: 'Nhập nội dung trao đổi.' }, { max: 4000, message: 'Nội dung không được vượt quá 4.000 ký tự.' }]}>
          <Input.TextArea rows={4} showCount maxLength={4000} placeholder="Ví dụ: Đã gọi tư vấn chương trình Fullstack, khách muốn nhận lịch khai giảng và sẽ phản hồi vào thứ Sáu..." />
        </Form.Item>
        <Button type="primary" htmlType="submit" icon={<CheckCircleOutlined />}>Lưu tương tác</Button>
      </Form>
    </SectionCard>

    <SectionCard title="Lịch gọi lại" subtitle="Lịch quá hạn được đưa lên đầu. Khi đã liên hệ khách hàng, bấm hoàn tất để đóng lịch nhắc." extra={<Button icon={<ReloadOutlined />} onClick={() => void loadReminders()} loading={loadingReminders}>Cập nhật</Button>}>
      <Table
        rowKey="id"
        loading={loadingReminders}
        dataSource={[...reminders].sort((a, b) => Number(b.is_overdue) - Number(a.is_overdue) || new Date(a.reminder_at || 0).getTime() - new Date(b.reminder_at || 0).getTime())}
        scroll={{ x: 900 }}
        locale={{ emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Không có lịch gọi lại đang chờ." /> }}
        columns={[
          { title: 'Khách hàng', width: 210, render: (_, row: ReminderItem) => <EntityCell title={row.lead_name} subtitle={row.lead_phone} /> },
          { title: 'Thời điểm nhắc', dataIndex: 'reminder_at', width: 165, render: (value, row: ReminderItem) => <Typography.Text type={row.is_overdue ? 'danger' : 'secondary'}>{formatDateTime(value)}</Typography.Text> },
          { title: 'Nội dung cần theo dõi', dataIndex: 'content', render: value => <Typography.Paragraph className="lead-care-reminder-content" ellipsis={{ rows: 2, tooltip: value }}>{value}</Typography.Paragraph> },
          { title: 'Tình trạng', dataIndex: 'is_overdue', width: 135, render: (value: boolean) => value ? <Tag color="red" icon={<ClockCircleOutlined />}>Quá hạn</Tag> : <Tag color="blue">Sắp tới</Tag> },
          { title: 'Thao tác', width: 160, fixed: 'right' as const, render: (_, row: ReminderItem) => <Button size="small" type="primary" ghost icon={<CheckCircleOutlined />} onClick={() => void completeReminder(row.id)}>Hoàn tất nhắc</Button> },
        ]}
      />
    </SectionCard>

    <SectionCard title="Lịch sử chăm sóc" subtitle={selectedLead ? `Các tương tác đã ghi nhận với ${selectedLead.full_name}.` : 'Chọn một lead ở phần ghi nhận tương tác để xem lịch sử.'}>
      <List
        loading={loadingHistory}
        dataSource={items}
        locale={{ emptyText: selectedLead ? 'Lead này chưa có tương tác nào.' : 'Chưa chọn lead.' }}
        renderItem={item => <List.Item actions={item.reminder_at && !item.reminder_completed_at ? [<Button key="complete" size="small" icon={<CheckCircleOutlined />} onClick={() => void completeReminder(item.id)}>Hoàn tất nhắc</Button>] : []}>
          <List.Item.Meta
            title={<Space wrap>
              <Tag color={item.interaction_type === 'call' ? 'blue' : item.interaction_type === 'message' ? 'purple' : 'cyan'}>{interactionLabels[item.interaction_type] || item.interaction_type}</Tag>
              <Typography.Text strong>{formatDateTime(item.occurred_at)}</Typography.Text>
              {item.is_overdue && <Tag color="red">Quá hạn</Tag>}
              {item.reminder_at && item.reminder_completed_at && <Tag color="green">Đã hoàn tất nhắc</Tag>}
            </Space>}
            description={<div className="lead-care-history-description">
              <Typography.Paragraph>{item.content}</Typography.Paragraph>
              {item.reminder_at && <Typography.Text type={item.is_overdue ? 'danger' : 'secondary'}> <CalendarOutlined /> Nhắc gọi lại: {formatDateTime(item.reminder_at)}</Typography.Text>}
              {item.created_by && <Typography.Text type="secondary"> · Ghi nhận bởi {item.created_by}</Typography.Text>}
            </div>}
          />
        </List.Item>}
      />
    </SectionCard>
  </FeaturePage>
}
