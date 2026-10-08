import { Button, Card, Space, Table, Tag, Typography, Upload, message } from 'antd'
import { DownloadOutlined, UploadOutlined } from '@ant-design/icons'
import { useState } from 'react'
import { api, apiErrorMessage } from '../api/client'

type PreviewRow = { row:number; full_name:string; email:string; phone?:string; role_slugs:string[]; errors:string[]; valid:boolean }

export default function ImportUsersPage() {
  const [file, setFile] = useState<File | null>(null)
  const [rows, setRows] = useState<PreviewRow[]>([])
  const [busy, setBusy] = useState(false)
  const [previewed, setPreviewed] = useState(false)
  const download = async () => {
    const r = await api.get('/api/users/import/template', { responseType: 'blob' })
    const url = URL.createObjectURL(r.data); const a = document.createElement('a'); a.href=url; a.download='mau-nhap-nguoi-dung.xlsx'; a.click(); URL.revokeObjectURL(url)
  }
  const send = async (path:string) => {
    if (!file) return message.warning('Chọn tệp Excel trước.')
    setBusy(true)
    try {
      const fd = new FormData(); fd.append('file', file)
      const { data } = await api.post(path, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      if (path.endsWith('/preview')) { setRows(data.rows); setPreviewed(true); message.success(`Hợp lệ ${data.valid}/${data.total} dòng.`) }
      else { setRows(data.skipped || []); message.success(`Đã nhập ${data.imported_count}/${data.total}; bỏ qua ${data.skipped_count}.`) }
    } catch(e) { message.error(apiErrorMessage(e)) } finally { setBusy(false) }
  }
  return <Card title="S2-01 · Nhập danh sách người dùng từ Excel">
    <Space wrap style={{ marginBottom: 16 }}>
      <Button icon={<DownloadOutlined />} onClick={download}>Tải tệp mẫu</Button>
      <Upload beforeUpload={(f)=>{setFile(f); setRows([]); setPreviewed(false); return false}} maxCount={1} accept=".xlsx"><Button icon={<UploadOutlined />}>Chọn Excel</Button></Upload>
      <Button onClick={()=>send('/api/users/import/preview')} loading={busy}>Xem trước & kiểm tra</Button>
      <Button type="primary" onClick={()=>send('/api/users/import')} loading={busy} disabled={!previewed}>Nhập các dòng hợp lệ</Button>
    </Space>
    <Typography.Paragraph type="secondary">Hệ thống báo lỗi theo từng dòng trước khi nhập; email trùng/lỗi sẽ bị bỏ qua và báo cáo tổng kết.</Typography.Paragraph>
    <Table rowKey="row" dataSource={rows} pagination={false} columns={[
      {title:'Dòng',dataIndex:'row'}, {title:'Họ tên',dataIndex:'full_name'}, {title:'Email',dataIndex:'email'},
      {title:'Vai trò',dataIndex:'role_slugs',render:(v:string[])=>v?.join(', ')},
      {title:'Kết quả',render:(_:any,r:PreviewRow)=>r.valid?<Tag color="green">Hợp lệ</Tag>:<Tag color="red">{r.errors.join('; ')}</Tag>}
    ]}/>
  </Card>
}
