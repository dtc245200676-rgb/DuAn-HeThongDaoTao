import { Tag } from 'antd'

const statusMeta: Record<string, { color: string; label: string }> = {
  new: { color: 'blue', label: 'Mới' },
  contacted: { color: 'purple', label: 'Đã liên hệ' },
  qualified: { color: 'cyan', label: 'Đủ điều kiện' },
  consulting: { color: 'gold', label: 'Đang tư vấn' },
  trial: { color: 'geekblue', label: 'Học thử' },
  closed: { color: 'green', label: 'Đã chốt' },
  enrolled: { color: 'green', label: 'Đã ghi danh' },
  rejected: { color: 'red', label: 'Từ chối' },
  active: { color: 'green', label: 'Hoạt động' },
  pending: { color: 'gold', label: 'Chờ xử lý' },
  locked: { color: 'red', label: 'Đã khóa' },
  preparing: { color: 'blue', label: 'Chuẩn bị' },
  studying: { color: 'green', label: 'Đang học' },
  completed: { color: 'default', label: 'Kết thúc' },
  cancelled: { color: 'red', label: 'Đã hủy' },
  present: { color: 'green', label: 'Có mặt' },
  late: { color: 'gold', label: 'Đi muộn' },
  excused_absence: { color: 'blue', label: 'Vắng có phép' },
  unexcused_absence: { color: 'red', label: 'Vắng không phép' },
}

type StatusTagProps = {
  value?: string | null
  label?: string
}

export default function StatusTag({ value, label }: StatusTagProps) {
  const key = value || ''
  const meta = statusMeta[key]
  return <Tag className="feature-status-tag" color={meta?.color}>{label || meta?.label || value || '—'}</Tag>
}
