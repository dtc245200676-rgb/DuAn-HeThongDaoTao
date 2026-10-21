import { BookOutlined, PlusOutlined } from '@ant-design/icons'
import { Button, DatePicker, Form, Input, InputNumber, Modal, Select, Space, Table, message } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import FeaturePage from '../components/function-ui/FeaturePage'
import MetricStrip from '../components/function-ui/MetricStrip'
import SectionCard from '../components/function-ui/SectionCard'
import StatusTag from '../components/function-ui/StatusTag'
import type { TrainingClassItem, TrainingProgramItem } from '../types'

export default function ClassManagementPage() {
  const [items, setItems] = useState<TrainingClassItem[]>([])
  const [programs, setPrograms] = useState<TrainingProgramItem[]>([])
  const [open, setOpen] = useState(false)
  const [form] = Form.useForm()

  const load = async () => setItems((await api.get('/api/s3/classes-manage/classes')).data)

  useEffect(() => {
    load().catch(() => message.error('Không tải được lớp.'))
    api.get('/api/training/programs').then(r => setPrograms(r.data)).catch(() => undefined)
  }, [])

  const create = async (v: any) => {
    try {
      await api.post('/api/s3/classes-manage/classes', { ...v, expected_start_date: v.expected_start_date.format('YYYY-MM-DD') })
      message.success('Đã mở lớp và sao chép lộ trình môn học.')
      setOpen(false)
      form.resetFields()
      await load()
    } catch (e) {
      message.error(apiErrorMessage(e))
    }
  }

  const setStatus = async (id: number, status: string) => {
    try {
      await api.put(`/api/s3/classes-manage/classes/${id}`, { status })
      await load()
    } catch (e) {
      message.error(apiErrorMessage(e))
    }
  }

  const metrics = useMemo(() => {
    const preparing = items.filter(item => item.status === 'preparing').length
    const studying = items.filter(item => item.status === 'studying').length
    const totalCapacity = items.reduce((sum, item) => sum + (item.max_students || 0), 0)
    return [
      { label: 'Tổng số lớp', value: items.length, hint: 'Tất cả trạng thái' },
      { label: 'Đang chuẩn bị', value: preparing, hint: 'Chưa bắt đầu học' },
      { label: 'Đang học', value: studying, hint: 'Đang vận hành' },
      { label: 'Tổng sức chứa', value: totalCapacity, hint: 'Theo sĩ số tối đa' },
    ]
  }, [items])

  return <FeaturePage
    eyebrow="Đào tạo"
    title="Quản lý lớp học"
    description="Mở lớp từ chương trình đào tạo, theo dõi trạng thái vận hành và quản lý quy mô lớp học."
    icon={<BookOutlined />}
    tone="blue"
    actions={<Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>Mở lớp mới</Button>}
  >
    <MetricStrip items={metrics} />

    <SectionCard title="Danh sách lớp học" subtitle="Theo dõi chương trình, lịch khai giảng, hình thức học và trạng thái của từng lớp.">
      <Table
        rowKey="id"
        dataSource={items}
        scroll={{ x: 920 }}
        columns={[
          { title: 'Mã lớp', dataIndex: 'code', render: v => <strong>{v}</strong> },
          { title: 'Chương trình', dataIndex: 'program_name' },
          { title: 'Khai giảng', dataIndex: 'expected_start_date' },
          { title: 'Sĩ số tối đa', dataIndex: 'max_students' },
          { title: 'Hình thức', dataIndex: 'delivery_mode', render: v => v === 'offline' ? 'Trực tiếp' : v === 'online' ? 'Trực tuyến' : v === 'hybrid' ? 'Kết hợp' : v },
          { title: 'Trạng thái', dataIndex: 'status', render: v => <StatusTag value={v} /> },
          {
            title: 'Chuyển trạng thái',
            render: (_, r) => <Space>
              {r.status === 'preparing' && <>
                <Button size="small" type="primary" ghost onClick={() => void setStatus(r.id, 'studying')}>Bắt đầu học</Button>
                <Button size="small" danger onClick={() => void setStatus(r.id, 'cancelled')}>Hủy</Button>
              </>}
              {r.status === 'studying' && <>
                <Button size="small" type="primary" ghost onClick={() => void setStatus(r.id, 'completed')}>Kết thúc</Button>
                <Button size="small" danger onClick={() => void setStatus(r.id, 'cancelled')}>Hủy</Button>
              </>}
            </Space>,
          },
        ]}
      />
    </SectionCard>

    <Modal title="Mở lớp mới" open={open} onCancel={() => setOpen(false)} footer={null}>
      <Form form={form} layout="vertical" onFinish={create}>
        <Form.Item name="code" label="Mã lớp" rules={[{ required: true }]}><Input /></Form.Item>
        <Form.Item name="program_id" label="Chương trình" rules={[{ required: true }]}><Select options={programs.map(x => ({ value: x.id, label: `${x.code} · ${x.name}` }))} /></Form.Item>
        <Form.Item name="expected_start_date" label="Ngày khai giảng dự kiến" rules={[{ required: true }]}><DatePicker style={{ width: '100%' }} /></Form.Item>
        <Form.Item name="max_students" label="Sĩ số tối đa" initialValue={30}><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
        <Form.Item name="delivery_mode" label="Hình thức" initialValue="offline"><Select options={[{ value: 'offline', label: 'Trực tiếp' }, { value: 'online', label: 'Trực tuyến' }, { value: 'hybrid', label: 'Kết hợp' }]} /></Form.Item>
        <Button type="primary" htmlType="submit">Tạo lớp</Button>
      </Form>
    </Modal>
  </FeaturePage>
}
