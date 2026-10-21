import { DownloadOutlined, ReloadOutlined, SendOutlined } from '@ant-design/icons'
import { Button, Card, Col, Empty, message, Row, Select, Space, Statistic, Table, Tag, Typography } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'

interface ClassOption { id: number; code: string; name: string; status: string }
interface AttendanceWarning { student_id: number; student_code: string; full_name: string; class_id: number; class_code: string; total_sessions: number; absence_count: number; absence_rate: number; attendance_rate: number; warning: boolean }
interface MatrixStudent extends AttendanceWarning { history: { session_id: number; start_at: string; status: string }[]; present_count: number; late_count: number; unexcused_absence_count: number; consecutive_absences: number; consecutive_warning: boolean }
const statusLabels: Record<string, string> = { present: 'Có mặt', late: 'Đi muộn', excused_absence: 'Vắng có phép', unexcused_absence: 'Vắng không phép', not_marked: 'Chưa điểm danh' }

export default function AttendanceInsightsPage() {
  const { user } = useAuth()
  const isStudent = Boolean(user?.roles.includes('student') && !user.roles.some((r) => ['system_admin', 'training_manager', 'teacher', 'academic_affairs'].includes(r)))
  const [classes, setClasses] = useState<ClassOption[]>([])
  const [classId, setClassId] = useState<number>()
  const [warnings, setWarnings] = useState<AttendanceWarning[]>([])
  const [matrix, setMatrix] = useState<{ sessions: { id: number; start_at: string }[]; students: MatrixStudent[]; class_code?: string }>({ sessions: [], students: [] })
  const [myAttendance, setMyAttendance] = useState<MatrixStudent[]>([])
  const [loading, setLoading] = useState(false)

  const loadWarnings = async () => {
    try { const response = await api.get('/api/s5/attendance/warnings?threshold=20'); setWarnings(response.data.items || []) }
    catch (error) { message.error(apiErrorMessage(error, 'Không tải được cảnh báo chuyên cần.')) }
  }
  const loadClasses = async () => {
    try {
      const response = await api.get('/api/s5/classes'); const rows: ClassOption[] = response.data || []
      setClasses(rows); if (!classId && rows.length) setClassId(rows[0].id)
    } catch (error) { message.error(apiErrorMessage(error, 'Không tải được danh sách lớp.')) }
  }
  const loadMatrix = async (id: number) => {
    setLoading(true)
    try { const response = await api.get(`/api/s5/attendance/classes/${id}/matrix`); setMatrix(response.data) }
    catch (error) { message.error(apiErrorMessage(error, 'Không tải được ma trận chuyên cần.')); setMatrix({ sessions: [], students: [] }) }
    finally { setLoading(false) }
  }
  const loadMine = async () => {
    try { const response = await api.get('/api/s5/attendance/me'); setMyAttendance(response.data.items || []) }
    catch (error) { message.error(apiErrorMessage(error, 'Không tải được lịch sử điểm danh cá nhân.')) }
  }
  useEffect(() => { if (isStudent) void loadMine(); else { void loadClasses(); void loadWarnings() } }, [])
  useEffect(() => { if (classId && !isStudent) void loadMatrix(classId) }, [classId])

  const exportExcel = async () => {
    if (!classId) return
    try {
      const response = await api.get(`/api/s5/attendance/classes/${classId}/export`, { responseType: 'blob' })
      const url = URL.createObjectURL(response.data); const anchor = document.createElement('a')
      anchor.href = url; anchor.download = `attendance_${matrix.class_code || classId}.xlsx`; anchor.click(); URL.revokeObjectURL(url)
    } catch (error) { message.error(apiErrorMessage(error, 'Không xuất được Excel.')) }
  }
  const sendWarnings = async () => {
    try { const response = await api.post('/api/s5/attendance/warnings/notify?threshold=20'); message.success(response.data.message); void loadWarnings() }
    catch (error) { message.error(apiErrorMessage(error, 'Không gửi được cảnh báo.')) }
  }

  if (isStudent) return <Space direction="vertical" size={16} style={{ width: '100%' }}>
    <Typography.Title level={3}>S5-03 · Lịch sử điểm danh của tôi</Typography.Title>
    {myAttendance.length === 0 ? <Empty description="Chưa có dữ liệu điểm danh cho lớp đang học." /> : myAttendance.map((item) => <Card key={item.class_id} title={`Lớp ${item.class_code}`}>
      <Row gutter={16}>
        <Col span={8}><Statistic title="Tỷ lệ chuyên cần" value={item.attendance_rate} suffix="%" /></Col>
        <Col span={8}><Statistic title="Số buổi vắng" value={item.absence_count} /></Col>
        <Col span={8}><Statistic title="Tổng buổi đã điểm danh" value={item.total_sessions} /></Col>
      </Row>
      {item.warning && <Tag color="red">Bạn đang ở ngưỡng cần chú ý về chuyên cần.</Tag>}{item.consecutive_warning && <Tag color="orange">Bạn đã vắng liên tiếp {item.consecutive_absences} buổi, hãy liên hệ giáo vụ.</Tag>}
      <Table rowKey="session_id" style={{ marginTop: 12 }} dataSource={item.history} pagination={{ pageSize: 8 }} columns={[
        { title: 'Ngày học', dataIndex: 'start_at', render: (v: string) => new Date(v).toLocaleString() },
        { title: 'Trạng thái', dataIndex: 'status', render: (v: string) => <Tag color={v.includes('absence') ? 'red' : v === 'late' ? 'orange' : 'green'}>{statusLabels[v] || v}</Tag> },
      ]} />
    </Card>)}
  </Space>

  return <Space direction="vertical" size={16} style={{ width: '100%' }}>
    <Typography.Title level={3}>S5 · Báo cáo chuyên cần</Typography.Title>
    <Card title="S5-02 · Cảnh báo học viên vượt ngưỡng" extra={<Space><Button icon={<ReloadOutlined />} onClick={() => { void loadWarnings(); if (classId) void loadMatrix(classId) }}>Làm mới</Button><Button type="primary" icon={<SendOutlined />} onClick={() => void sendWarnings()}>Gửi cảnh báo</Button></Space>}>
      <Typography.Paragraph type="secondary">Ngưỡng mặc định: tỷ lệ vắng từ 20% số buổi đã diễn ra hoặc đã được điểm danh. Dữ liệu chưa điểm danh không được tự động tính là vắng.</Typography.Paragraph>
      <Table rowKey={(r) => `${r.class_id}-${r.student_id}`} dataSource={warnings} pagination={{ pageSize: 8 }} columns={[
        { title: 'Lớp', dataIndex: 'class_code' }, { title: 'Mã HV', dataIndex: 'student_code' }, { title: 'Họ tên', dataIndex: 'full_name' },
        { title: 'Buổi vắng', dataIndex: 'absence_count' }, { title: 'Tỷ lệ vắng', dataIndex: 'absence_rate', render: (v: number) => <Tag color="red">{v}%</Tag> },
      ]} />
    </Card>
    <Card title="S5-01 / S5-04 · Ma trận chuyên cần" extra={<Space><Select placeholder="Chọn lớp" style={{ minWidth: 220 }} value={classId} onChange={setClassId} options={classes.map((c) => ({ value: c.id, label: c.code }))} /><Button icon={<DownloadOutlined />} disabled={!classId} onClick={() => void exportExcel()}>Xuất Excel</Button></Space>}>
      {!classId ? <Empty description="Chưa có lớp để xem." /> : <Table rowKey="student_id" loading={loading} dataSource={matrix.students} pagination={{ pageSize: 10 }} scroll={{ x: 900 }} columns={[
        { title: 'Mã HV', dataIndex: 'student_code', fixed: 'left', width: 110 }, { title: 'Họ tên', dataIndex: 'full_name', fixed: 'left', width: 180 },
        ...matrix.sessions.map((session) => ({ title: new Date(session.start_at).toLocaleDateString(), key: `s-${session.id}`, width: 110, render: (_: unknown, row: MatrixStudent) => { const rec = row.history.find((h) => h.session_id === session.id); const status = rec?.status || 'not_marked'; return <Tag color={status.includes('absence') ? 'red' : status === 'late' ? 'orange' : status === 'present' ? 'green' : 'default'}>{statusLabels[status] || status}</Tag> } })),
        { title: 'Tỷ lệ chuyên cần', dataIndex: 'attendance_rate', width: 130, render: (v: number) => `${v}%` }, { title: 'Cảnh báo', dataIndex: 'warning', width: 100, render: (v: boolean) => v ? <Tag color="red">Cần chú ý</Tag> : <Tag color="green">Bình thường</Tag> },
      ]} />}
    </Card>
  </Space>
}
