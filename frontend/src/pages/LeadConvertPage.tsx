import { Button, Card, Form, Input, Modal, Space, Table, Tag, message } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import type { LeadItem } from '../types'

export default function LeadConvertPage(){
 const [items,setItems]=useState<LeadItem[]>([]);const [lead,setLead]=useState<LeadItem>();const [open,setOpen]=useState(false);const [result,setResult]=useState<any>();const [form]=Form.useForm()
 const load=async()=>setItems((await api.get('/api/leads',{params:{status:'closed',page_size:100}})).data.items)
 useEffect(()=>{load().catch(()=>message.error('Không tải được lead đã chốt.'))},[])
 const convert=async(values:any)=>{if(!lead)return;try{const r=(await api.post(`/api/s3/convert/leads/${lead.id}/student`,values)).data;setResult(r);setOpen(false);message.success('Đã tạo hồ sơ học viên.');await load()}catch(e){message.error(apiErrorMessage(e))}}
 return <Card title="S3-03 · Chuyển lead đã chốt thành học viên"><Table rowKey="id" dataSource={items} columns={[{title:'Khách hàng',dataIndex:'full_name'},{title:'SĐT',dataIndex:'phone'},{title:'Email',dataIndex:'email'},{title:'Trạng thái',render:()=> <Tag color="green">Chốt</Tag>},{title:'Thao tác',render:(_,r)=><Button type="primary" onClick={()=>{setLead(r);setOpen(true)}}>Tạo hồ sơ học viên</Button>}]}/><Modal title={`Chuyển ${lead?.full_name||''} thành học viên`} open={open} onCancel={()=>setOpen(false)} footer={null}><Form form={form} layout="vertical" onFinish={convert}><Form.Item name="entry_level" label="Trình độ đầu vào"><Input/></Form.Item><Form.Item name="notes" label="Ghi chú"><Input.TextArea/></Form.Item><Button type="primary" htmlType="submit">Xác nhận chuyển</Button></Form></Modal><Modal title="Tạo học viên thành công" open={!!result} onCancel={()=>setResult(undefined)} footer={<Button onClick={()=>setResult(undefined)}>Đóng</Button>}><Space direction="vertical"><div>Mã học viên: <strong>{result?.student_code}</strong></div><div>Email: {result?.email}</div>{result?.debug_temporary_password&&<div>Mật khẩu tạm (DEV): <strong>{result.debug_temporary_password}</strong></div>}</Space></Modal></Card>
}
