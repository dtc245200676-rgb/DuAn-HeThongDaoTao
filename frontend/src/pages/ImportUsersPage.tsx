import { DownloadOutlined, FileExcelOutlined, InboxOutlined, UploadOutlined } from '@ant-design/icons'
import { Button, Steps, Table, Tag, Upload, message } from 'antd'
import { useMemo, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import FeaturePage from '../components/function-ui/FeaturePage'
import MetricStrip from '../components/function-ui/MetricStrip'
import SectionCard from '../components/function-ui/SectionCard'

const { Dragger } = Upload

type PreviewRow = { row: number; full_name: string; email: string; phone?: string; role_slugs: string[]; errors: string[]; valid: boolean }

export default function ImportUsersPage() {
  const [file, setFile] = useState<File | null>(null)
  const [rows, setRows] = useState<PreviewRow[]>([])
  const [busy, setBusy] = useState(false)
  const [previewed, setPreviewed] = useState(false)

  const validCount = useMemo(() => rows.filter(row => row.valid).length, [rows])
  const invalidCount = rows.length - validCount
  const currentStep = previewed ? 2 : file ? 1 : 0

  const download = async () => {
    const r = await api.get('/api/users/import/template', { responseType: 'blob' })
    const url = URL.createObjectURL(r.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'mau-nhap-nguoi-dung.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  }

  const send = async (path: string) => {
    if (!file) return message.warning('Chọn tệp Excel trước.')
    setBusy(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const { data } = await api.post(path, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      if (path.endsWith('/preview')) {
        setRows(data.rows)
        setPreviewed(true)
        message.success(`Hợp lệ ${data.valid}/${data.total} dòng.`)
      } else {
        setRows(data.skipped || [])
        message.success(`Đã nhập ${data.imported_count}/${data.total}; bỏ qua ${data.skipped_count}.`)
      }
    } catch (e) {
      message.error(apiErrorMessage(e))
    } finally {
      setBusy(false)
    }
  }

  return <FeaturePage
    eyebrow="Quản trị"
    title="Nhập dữ liệu người dùng"
    description="Nhập người dùng hàng loạt từ Excel theo quy trình kiểm tra trước, giúp phát hiện dữ liệu trùng hoặc không hợp lệ trước khi ghi nhận."
    icon={<FileExcelOutlined />}
    tone="violet"
    actions={<Button icon={<DownloadOutlined />} onClick={download}>Tải tệp mẫu</Button>}
  >
    <SectionCard title="Quy trình nhập dữ liệu" subtitle="Hoàn thành lần lượt từng bước để đảm bảo dữ liệu được kiểm tra trước khi nhập.">
      <Steps
        current={currentStep}
        responsive
        items={[
          { title: 'Chọn tệp Excel', description: 'Sử dụng đúng mẫu hệ thống' },
          { title: 'Xem trước & kiểm tra', description: 'Phát hiện lỗi theo từng dòng' },
          { title: 'Nhập dữ liệu hợp lệ', description: 'Chỉ ghi nhận các dòng đạt yêu cầu' },
        ]}
      />
    </SectionCard>

    <div className="feature-workflow">
      <SectionCard title="Tệp dữ liệu" subtitle="Chỉ chấp nhận định dạng .xlsx theo tệp mẫu của hệ thống.">
        <div className="feature-upload-zone">
          <Dragger
            beforeUpload={f => { setFile(f); setRows([]); setPreviewed(false); return false }}
            maxCount={1}
            accept=".xlsx"
            showUploadList
          >
            <div className="feature-upload-icon"><InboxOutlined /></div>
            <p><strong>{file ? file.name : 'Chọn hoặc kéo tệp Excel vào đây'}</strong></p>
            <p className="feature-upload-note">Dữ liệu chưa được ghi vào hệ thống cho đến khi bạn xác nhận nhập.</p>
          </Dragger>
        </div>
        <div className="feature-upload-actions">
          <Button icon={<UploadOutlined />} disabled={!file} onClick={() => send('/api/users/import/preview')} loading={busy}>Xem trước & kiểm tra</Button>
          <Button type="primary" disabled={!previewed} onClick={() => send('/api/users/import')} loading={busy}>Nhập các dòng hợp lệ</Button>
        </div>
      </SectionCard>

      <SectionCard title="Kết quả kiểm tra" subtitle="Theo dõi tổng quan chất lượng dữ liệu trước khi nhập.">
        <MetricStrip items={[
          { label: 'Tổng số dòng', value: rows.length, hint: previewed ? 'Đã phân tích' : 'Chưa xem trước' },
          { label: 'Hợp lệ', value: validCount, hint: 'Có thể nhập' },
          { label: 'Có lỗi', value: invalidCount, hint: 'Sẽ bị bỏ qua' },
          { label: 'Tệp đã chọn', value: file ? '1' : '0', hint: file?.name || 'Chưa có tệp' },
        ]} />
      </SectionCard>
    </div>

    <SectionCard title="Chi tiết dữ liệu" subtitle="Hệ thống báo lỗi theo từng dòng; email trùng hoặc dữ liệu sai sẽ được bỏ qua và hiển thị lý do.">
      <Table
        rowKey="row"
        dataSource={rows}
        pagination={false}
        locale={{ emptyText: 'Chọn tệp Excel và bấm “Xem trước & kiểm tra” để xem dữ liệu.' }}
        columns={[
          { title: 'Dòng', dataIndex: 'row', width: 80 },
          { title: 'Họ tên', dataIndex: 'full_name' },
          { title: 'Email', dataIndex: 'email' },
          { title: 'Vai trò', dataIndex: 'role_slugs', render: (v: string[]) => v?.join(', ') || '—' },
          { title: 'Kết quả', render: (_: unknown, r: PreviewRow) => r.valid ? <Tag color="green">Hợp lệ</Tag> : <Tag color="red">{r.errors.join('; ')}</Tag> },
        ]}
      />
    </SectionCard>
  </FeaturePage>
}
