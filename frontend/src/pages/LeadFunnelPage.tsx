import { Card, Col, Empty, Row, Space, Tag, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import type { LeadItem } from '../types'

type FunnelColumn = { status: string; label: string; count: number; items: LeadItem[] }

export default function LeadFunnelPage() {
  const [columns, setColumns] = useState<FunnelColumn[]>([])
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try { setColumns((await api.get('/api/s3/funnel')).data.columns) }
    catch (e) { message.error(apiErrorMessage(e, 'Không tải được bảng phễu.')) }
    finally { setLoading(false) }
  }
  useEffect(() => { void load() }, [])

  const move = async (leadId: number, status: string) => {
    let rejection_reason: string | undefined
    if (status === 'rejected') {
      const reason = window.prompt('Lý do từ chối:')?.trim()
      if (!reason) return message.warning('Từ chối lead bắt buộc phải có lý do.')
      rejection_reason = reason
    }
    try {
      await api.patch(`/api/s3/funnel/leads/${leadId}/status`, { status, rejection_reason })
      message.success('Đã cập nhật trạng thái và ghi nhật ký.')
      await load()
    } catch (e) { message.error(apiErrorMessage(e)) }
  }

  return <Card title="S3-01 · Bảng phễu tư vấn" loading={loading}>
    <Typography.Paragraph type="secondary">Kéo lead sang cột khác để đổi trạng thái. Mỗi lần đổi đều được ghi lịch sử.</Typography.Paragraph>
    <Row gutter={[12, 12]} wrap={false} style={{ overflowX: 'auto', paddingBottom: 8 }}>
      {columns.map(column => <Col key={column.status} flex="0 0 260px">
        <Card size="small" title={<Space>{column.label}<Tag>{column.count}</Tag></Space>}
          onDragOver={e => e.preventDefault()}
          onDrop={e => { const id = Number(e.dataTransfer.getData('lead-id')); if (id) void move(id, column.status) }}>
          {column.items.length === 0 ? <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Chưa có lead" /> : column.items.map(lead =>
            <Card key={lead.id} size="small" draggable onDragStart={e => e.dataTransfer.setData('lead-id', String(lead.id))} style={{ marginBottom: 8, cursor: 'grab' }}>
              <strong>{lead.full_name}</strong><br />
              <Typography.Text type="secondary">{lead.phone}</Typography.Text><br />
              {lead.assignee && <Tag>{lead.assignee}</Tag>}
            </Card>)}
        </Card>
      </Col>)}
    </Row>
  </Card>
}
