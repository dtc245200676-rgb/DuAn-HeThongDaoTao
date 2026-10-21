import { FileAddOutlined, HistoryOutlined, ReloadOutlined } from '@ant-design/icons'
import { Button, Card, Checkbox, Form, Input, InputNumber, message, Modal, Select, Space, Table, Tag, Typography } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'

interface ClassOption { id: number; code: string; name: string }
interface AssignmentItem { id: number; title: string; description?: string; due_at: string; student_due_at?: string; max_score: number; allow_late: boolean; status: string; classes: { id: number; code: string }[]; submission_status?: string; latest_submission?: SubmissionItem | null; attachments?: { name: string; path: string; size: number }[] }
interface SubmissionItem { id: number; assignment_id: number; student_id: number; student_code?: string; student_name?: string; version: number; files: { name: string; path: string; size: number }[]; comment?: string; status: string; is_late: boolean; score?: number; feedback?: string; submitted_at: string }
interface ProgressRow { id: number; title: string; students: { student_id: number; student_code: string; student_name: string; status: string; submitted_at?: string; is_late: boolean; score?: number; submission_id?: number; feedback?: string }[]; total_students: number; submitted_count: number; graded_count: number; late_count: number }
const submissionLabels: Record<string, string> = { not_submitted: 'Chưa nộp', overdue: 'Quá hạn', submitted: 'Đã nộp', graded: 'Đã chấm', needs_revision: 'Cần làm lại', late: 'Nộp muộn' }
const statusColor: Record<string, string> = { not_submitted: 'default', overdue: 'red', submitted: 'blue', graded: 'green', needs_revision: 'orange', late: 'red' }
const defaultDue = () => { const d = new Date(Date.now() + 7 * 86400000); d.setMinutes(d.getMinutes() - d.getTimezoneOffset()); return d.toISOString().slice(0, 16) }

export default function AssignmentsPage() {
  const { user } = useAuth()
  const isStudent = Boolean(user?.roles.includes('student') && !user.roles.some((r) => ['system_admin', 'training_manager', 'teacher', 'academic_affairs'].includes(r)))
  const [classes, setClasses] = useState<ClassOption[]>([])
  const [classId, setClassId] = useState<number>()
  const [items, setItems] = useState<AssignmentItem[]>([])
  const [loading, setLoading] = useState(false)
  const [createOpen, setCreateOpen] = useState(false)
  const [submitTarget, setSubmitTarget] = useState<AssignmentItem | null>(null)
  const [historyTarget, setHistoryTarget] = useState<AssignmentItem | null>(null)
  const [history, setHistory] = useState<SubmissionItem[]>([])
  const [submissionRows, setSubmissionRows] = useState<SubmissionItem[]>([])
  const [submissionTarget, setSubmissionTarget] = useState<AssignmentItem | null>(null)
  const [progressOpen, setProgressOpen] = useState(false)
  const [progressRows, setProgressRows] = useState<ProgressRow[]>([])
  const [gradeTarget, setGradeTarget] = useState<SubmissionItem | null>(null)
  const [extensionTarget, setExtensionTarget] = useState<SubmissionItem | null>(null)
  const [studentStatusFilter, setStudentStatusFilter] = useState<string>('all')
  const [createForm] = Form.useForm()
  const [gradeForm] = Form.useForm()
  const [extensionForm] = Form.useForm()
  const [submissionFiles, setSubmissionFiles] = useState<File[]>([])
  const [attachmentFiles, setAttachmentFiles] = useState<File[]>([])

  const loadClasses = async () => {
    try { const response = await api.get('/api/s5/classes'); const rows: ClassOption[] = response.data || []; setClasses(rows); if (!classId && rows.length) setClassId(rows[0].id) }
    catch (error) { message.error(apiErrorMessage(error, 'Không tải được danh sách lớp.')) }
  }
  const loadAssignments = async () => {
    setLoading(true)
    try { const response = await api.get(isStudent ? '/api/s5/assignments/mine' : '/api/s5/assignments', { params: !isStudent && classId ? { class_id: classId } : undefined }); setItems(response.data || []) }
    catch (error) { message.error(apiErrorMessage(error, 'Không tải được danh sách bài tập.')) }
    finally { setLoading(false) }
  }
  useEffect(() => { if (!isStudent) void loadClasses(); else void loadAssignments() }, [])
  useEffect(() => { if (!isStudent) void loadAssignments() }, [classId])

  const createAssignment = async (values: { title: string; description?: string; class_ids: number[]; due_at: string; max_score: number; allow_late?: boolean }) => {
    const form = new FormData()
    form.append('title', values.title); form.append('description', values.description || ''); form.append('class_ids', JSON.stringify(values.class_ids))
    form.append('due_at', values.due_at.replace('T', 'T')); form.append('max_score', String(values.max_score || 10)); form.append('allow_late', String(Boolean(values.allow_late))); form.append('publish', 'true')
    attachmentFiles.forEach((file) => form.append('files', file))
    try { await api.post('/api/s5/assignments', form, { headers: { 'Content-Type': 'multipart/form-data' } }); message.success('Đã giao bài tập.'); setCreateOpen(false); createForm.resetFields(); setAttachmentFiles([]); void loadAssignments() }
    catch (error) { message.error(apiErrorMessage(error, 'Không tạo được bài tập.')) }
  }
  const submitAssignment = async () => {
    if (!submitTarget) return
    if (!submissionFiles.length) { message.warning('Hãy chọn ít nhất một tệp để nộp.'); return }
    const form = new FormData(); form.append('comment', (document.getElementById('s5-submit-comment') as HTMLTextAreaElement | null)?.value || '')
    submissionFiles.forEach((file) => form.append('files', file))
    try { await api.post(`/api/s5/assignments/${submitTarget.id}/submissions`, form, { headers: { 'Content-Type': 'multipart/form-data' } }); message.success('Đã nộp bài và tạo phiên bản mới.'); setSubmitTarget(null); setSubmissionFiles([]); void loadAssignments() }
    catch (error) { message.error(apiErrorMessage(error, 'Không nộp được bài tập.')) }
  }
  const openHistory = async (item: AssignmentItem) => {
    setHistoryTarget(item)
    try { const response = await api.get(`/api/s5/assignments/${item.id}/history`); setHistory(response.data || []) }
    catch (error) { message.error(apiErrorMessage(error, 'Không tải được lịch sử nộp.')) }
  }
  const openSubmissions = async (item: AssignmentItem) => {
    setSubmissionTarget(item)
    try { const response = await api.get(`/api/s5/assignments/${item.id}/submissions`, { params: classId ? { class_id: classId } : undefined }); setSubmissionRows(response.data || []) }
    catch (error) { message.error(apiErrorMessage(error, 'Không tải được bài nộp.')) }
  }
  const openProgress = async () => {
    if (!classId) return
    try { const response = await api.get(`/api/s5/assignments/progress/${classId}`); setProgressRows(response.data.items || []); setProgressOpen(true) }
    catch (error) { message.error(apiErrorMessage(error, 'Không tải được tiến độ lớp.')) }
  }
  const grantExtension = async (values: { extended_due_at: string; reason: string }) => {
    if (!extensionTarget || !submissionTarget) return
    try { await api.post(`/api/s5/assignments/${submissionTarget.id}/extensions`, { student_id: extensionTarget.student_id, extended_due_at: values.extended_due_at, reason: values.reason }); message.success('Đã gia hạn hạn nộp cho học viên.'); setExtensionTarget(null); extensionForm.resetFields() }
    catch (error) { message.error(apiErrorMessage(error, 'Không gia hạn được bài tập.')) }
  }
  const gradeSubmission = async (values: { score?: number; feedback?: string; status: 'graded' | 'needs_revision' }) => {
    if (!gradeTarget) return
    try { await api.patch(`/api/s5/submissions/${gradeTarget.id}/grade`, values); message.success('Đã lưu điểm và nhận xét.'); setGradeTarget(null); void openSubmissions(submissionTarget as AssignmentItem) }
    catch (error) { message.error(apiErrorMessage(error, 'Không lưu được kết quả chấm.')) }
  }
  const downloadFile = (path: string, name: string) => { const anchor = document.createElement('a'); anchor.href = `${api.defaults.baseURL || 'http://127.0.0.1:8001'}/uploads/${path.replace(/^uploads\//, '')}`; anchor.target = '_blank'; anchor.download = name; anchor.click() }

  const studentColumns = [
    { title: 'Bài tập', dataIndex: 'title', key: 'title' },
    { title: 'Lớp', dataIndex: 'classes', render: (v: AssignmentItem['classes']) => v.map((x) => x.code).join(', ') },
    { title: 'Hạn nộp', dataIndex: 'student_due_at', render: (_: unknown, row: AssignmentItem) => new Date(row.student_due_at || row.due_at).toLocaleString() },
    { title: 'Trạng thái', dataIndex: 'submission_status', render: (v: string) => <Tag color={statusColor[v] || 'default'}>{submissionLabels[v] || v}</Tag> },
    { title: 'Điểm', render: (_: unknown, row: AssignmentItem) => row.latest_submission?.score == null ? '—' : `${row.latest_submission.score}/${row.max_score}` },
    { title: 'Thao tác', render: (_: unknown, row: AssignmentItem) => <Space><Button size="small" icon={<HistoryOutlined />} onClick={() => void openHistory(row)}>Lịch sử</Button><Button size="small" type="primary" icon={<FileAddOutlined />} disabled={row.submission_status === 'overdue' && !row.allow_late} onClick={() => { setSubmitTarget(row); setSubmissionFiles([]) }}>{row.submission_status === 'not_submitted' ? 'Nộp bài' : 'Nộp phiên bản mới'}</Button></Space> },
  ]

  if (isStudent) return <Card title="Bài tập của tôi" extra={<Space><Select value={studentStatusFilter} style={{ minWidth: 160 }} onChange={setStudentStatusFilter} options={[{ value: 'all', label: 'Tất cả trạng thái' }, ...Object.entries(submissionLabels).map(([value, label]) => ({ value, label }))]} /><Button icon={<ReloadOutlined />} onClick={() => void loadAssignments()}>Làm mới</Button></Space>}>
    <Table rowKey="id" loading={loading} dataSource={items.filter((item) => studentStatusFilter === 'all' || item.submission_status === studentStatusFilter)} columns={studentColumns} scroll={{ x: 900 }} />
    <Modal title={`Nộp bài: ${submitTarget?.title || ''}`} open={Boolean(submitTarget)} onCancel={() => setSubmitTarget(null)} onOk={() => void submitAssignment()} okText="Nộp bài">
      <Typography.Paragraph type="secondary">Có thể chọn nhiều tệp. Mỗi tệp tối đa 20 MB; các lần nộp được lưu thành phiên bản riêng.</Typography.Paragraph>
      <input type="file" multiple onChange={(event) => setSubmissionFiles(Array.from(event.target.files || []))} />
      <Input.TextArea id="s5-submit-comment" rows={3} placeholder="Nhận xét gửi giảng viên (không bắt buộc)" style={{ marginTop: 12 }} />
      {submitTarget?.attachments?.length ? <div style={{ marginTop: 12 }}><Typography.Text strong>Tệp hướng dẫn</Typography.Text>{submitTarget.attachments.map((f) => <div key={f.path}><Button type="link" onClick={() => downloadFile(f.path, f.name)}>{f.name}</Button></div>)}</div> : null}
    </Modal>
    <Modal title={`Lịch sử nộp: ${historyTarget?.title || ''}`} open={Boolean(historyTarget)} onCancel={() => setHistoryTarget(null)} footer={null} width={850}>
      <Table rowKey="id" dataSource={history} columns={[{ title: 'Phiên bản', dataIndex: 'version' }, { title: 'Ngày nộp', dataIndex: 'submitted_at', render: (v: string) => new Date(v).toLocaleString() }, { title: 'Tệp', dataIndex: 'files', render: (v: SubmissionItem['files']) => v.map((f) => <div key={f.path}><Button type="link" onClick={() => downloadFile(f.path, f.name)}>{f.name}</Button></div>) }, { title: 'Trạng thái', dataIndex: 'status', render: (v: string) => <Tag color={statusColor[v] || 'default'}>{submissionLabels[v] || v}</Tag> }, { title: 'Điểm', dataIndex: 'score' }, { title: 'Nhận xét', dataIndex: 'feedback' }]} />
    </Modal>
  </Card>

  return <Space direction="vertical" size={16} style={{ width: '100%' }}>
    <Card title="Tạo và giao bài tập" extra={<Space><Select placeholder="Chọn lớp" style={{ minWidth: 200 }} value={classId} onChange={setClassId} options={classes.map((c) => ({ value: c.id, label: c.code }))} /><Button icon={<ReloadOutlined />} onClick={() => void loadAssignments()}>Làm mới</Button><Button onClick={() => void openProgress()}>Tiến độ lớp</Button><Button type="primary" icon={<FileAddOutlined />} onClick={() => { createForm.setFieldsValue({ class_ids: classId ? [classId] : [], due_at: defaultDue(), max_score: 10, allow_late: false }); setCreateOpen(true) }}>Tạo bài tập</Button></Space>}>
      <Table rowKey="id" loading={loading} dataSource={items} columns={[
        { title: 'Tên bài tập', dataIndex: 'title' }, { title: 'Lớp', dataIndex: 'classes', render: (v: AssignmentItem['classes']) => v.map((x) => x.code).join(', ') },
        { title: 'Hạn nộp', dataIndex: 'due_at', render: (v: string) => new Date(v).toLocaleString() }, { title: 'Điểm tối đa', dataIndex: 'max_score' },
        { title: 'Trạng thái', dataIndex: 'status', render: (v: string) => <Tag color={v === 'published' ? 'green' : 'default'}>{v === 'published' ? 'Đã giao' : v === 'draft' ? 'Bản nháp' : 'Đã lưu trữ'}</Tag> },
        { title: 'Cho nộp muộn', dataIndex: 'allow_late', render: (v: boolean) => v ? 'Có' : 'Không' },
        { title: 'Thao tác', render: (_: unknown, row: AssignmentItem) => <Space><Button size="small" onClick={() => void openSubmissions(row)}>Bài nộp / chấm</Button><Button size="small" disabled={row.status !== 'draft'} onClick={async () => { try { await api.patch(`/api/s5/assignments/${row.id}`, { status: 'published' }); message.success('Đã giao bài.'); void loadAssignments() } catch (error) { message.error(apiErrorMessage(error)) } }}>Giao bài</Button></Space> },
      ]} scroll={{ x: 900 }} />
    </Card>
    <Modal title="Tạo bài tập mới" open={createOpen} onCancel={() => setCreateOpen(false)} onOk={() => void createForm.submit()} okText="Giao bài" width={700}>
      <Form form={createForm} layout="vertical" onFinish={createAssignment}>
        <Form.Item name="title" label="Tiêu đề" rules={[{ required: true, message: 'Nhập tiêu đề bài tập.' }]}><Input maxLength={200} /></Form.Item>
        <Form.Item name="description" label="Mô tả / yêu cầu"><Input.TextArea rows={3} /></Form.Item>
        <Form.Item name="class_ids" label="Giao cho lớp" rules={[{ required: true, message: 'Chọn ít nhất một lớp.' }]}><Select mode="multiple" options={classes.map((c) => ({ value: c.id, label: c.code }))} /></Form.Item>
        <Form.Item name="due_at" label="Hạn nộp" rules={[{ required: true, message: 'Nhập hạn nộp.' }]}><Input type="datetime-local" /></Form.Item>
        <Form.Item name="max_score" label="Điểm tối đa" rules={[{ required: true }]}><InputNumber min={1} max={1000} style={{ width: '100%' }} /></Form.Item>
        <Form.Item name="allow_late" valuePropName="checked"><Checkbox>Cho phép nộp muộn (đánh dấu nộp muộn)</Checkbox></Form.Item>
        <Form.Item label="Tệp đính kèm (mỗi tệp tối đa 20 MB)"><input type="file" multiple onChange={(event) => setAttachmentFiles(Array.from(event.target.files || []))} /></Form.Item>
      </Form>
    </Modal>
    <Modal title={`Bài nộp: ${submissionTarget?.title || ''}`} open={Boolean(submissionTarget)} onCancel={() => setSubmissionTarget(null)} footer={null} width={1000}>
      <Table rowKey="id" dataSource={submissionRows} pagination={{ pageSize: 8 }} columns={[
        { title: 'Học viên', render: (_: unknown, row: SubmissionItem) => `${row.student_code || ''} · ${row.student_name || ''}` }, { title: 'Phiên bản', dataIndex: 'version' },
        { title: 'Ngày nộp', dataIndex: 'submitted_at', render: (v: string) => new Date(v).toLocaleString() }, { title: 'Tệp', dataIndex: 'files', render: (v: SubmissionItem['files']) => v.map((f) => <div key={f.path}><Button type="link" onClick={() => downloadFile(f.path, f.name)}>{f.name}</Button></div>) },
        { title: 'Trạng thái', dataIndex: 'status', render: (v: string, row: SubmissionItem) => <Space><Tag color={statusColor[v] || 'default'}>{submissionLabels[v] || v}</Tag>{row.is_late && <Tag color="red">Muộn</Tag>}</Space> },
        { title: 'Điểm', dataIndex: 'score' }, { title: 'Thao tác', render: (_: unknown, row: SubmissionItem) => <Space><Button size="small" type="primary" onClick={() => { setGradeTarget(row); gradeForm.setFieldsValue({ score: row.score, feedback: row.feedback || '', status: row.status === 'needs_revision' ? 'needs_revision' : 'graded' }) }}>Chấm / nhận xét</Button><Button size="small" onClick={() => { setExtensionTarget(row); extensionForm.setFieldsValue({ extended_due_at: defaultDue(), reason: 'Gia hạn theo thỏa thuận với học viên' }) }}>Gia hạn</Button></Space> },
      ]} />
    </Modal>
    <Modal title="Chấm điểm và phản hồi" open={Boolean(gradeTarget)} onCancel={() => setGradeTarget(null)} onOk={() => void gradeForm.submit()} okText="Lưu kết quả">
      <Form form={gradeForm} layout="vertical" onFinish={gradeSubmission}>
        <Form.Item name="score" label="Điểm" rules={[{ type: 'number', min: 0 }]}><InputNumber style={{ width: '100%' }} min={0} /></Form.Item>
        <Form.Item name="status" label="Kết quả" rules={[{ required: true }]}><Select options={[{ value: 'graded', label: 'Đã chấm' }, { value: 'needs_revision', label: 'Yêu cầu làm lại' }]} /></Form.Item>
        <Form.Item name="feedback" label="Nhận xét"><Input.TextArea rows={4} /></Form.Item>
      </Form>
    </Modal>
    <Modal title={`Gia hạn bài tập: ${extensionTarget?.student_name || ''}`} open={Boolean(extensionTarget)} onCancel={() => setExtensionTarget(null)} onOk={() => void extensionForm.submit()} okText="Lưu gia hạn">
      <Form form={extensionForm} layout="vertical" onFinish={grantExtension}>
        <Form.Item name="extended_due_at" label="Hạn mới" rules={[{ required: true, message: 'Chọn hạn nộp mới.' }]}><Input type="datetime-local" /></Form.Item>
        <Form.Item name="reason" label="Lý do" rules={[{ required: true, message: 'Nhập lý do gia hạn.' }]}><Input.TextArea rows={3} maxLength={500} /></Form.Item>
      </Form>
    </Modal>
    <Modal title="Tiến độ bài tập của lớp" open={progressOpen} onCancel={() => setProgressOpen(false)} footer={null} width={1000}>
      {progressRows.map((assignment) => <Card key={assignment.id} size="small" title={assignment.title} style={{ marginBottom: 12 }} extra={<Space><Tag>{assignment.submitted_count}/{assignment.total_students} đã nộp</Tag><Tag color="green">{assignment.graded_count} đã chấm</Tag><Tag color="red">{assignment.late_count} nộp muộn</Tag></Space>}>
        <Table rowKey="student_id" size="small" dataSource={assignment.students} pagination={false} columns={[{ title: 'Mã HV', dataIndex: 'student_code' }, { title: 'Họ tên', dataIndex: 'student_name' }, { title: 'Trạng thái', dataIndex: 'status', render: (v: string) => <Tag color={statusColor[v] || 'default'}>{submissionLabels[v] || v}</Tag> }, { title: 'Ngày nộp', dataIndex: 'submitted_at', render: (v?: string) => v ? new Date(v).toLocaleString() : '—' }, { title: 'Điểm', dataIndex: 'score', render: (v?: number) => v ?? '—' }]} />
      </Card>)}
    </Modal>
  </Space>
}
