import { Skeleton } from 'antd'

export default function LoadingState({ rows = 4 }: { rows?: number }) {
  return <div className="ui-state"><Skeleton active paragraph={{ rows }} /></div>
}
