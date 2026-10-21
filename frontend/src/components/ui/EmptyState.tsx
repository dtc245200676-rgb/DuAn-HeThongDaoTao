import { Empty } from 'antd'

export default function EmptyState({ description = 'Chưa có dữ liệu để hiển thị.' }: { description?: string }) {
  return <div className="ui-state"><Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={description} /></div>
}
