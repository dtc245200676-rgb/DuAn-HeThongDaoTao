import { Alert, Button, Card, DatePicker, Form, Input, List, Select, Space, Tag, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import type { LeadItem } from '../types'

type Interaction = { id:number; interaction_type:string; content:string; occurred_at:string; reminder_at?:string|null; is_overdue:boolean; reminder_completed_at?:string|null }

export default function LeadCarePage(){
 const [leads,setLeads]=useState<LeadItem[]>([]);const [leadId,setLeadId]=useState<number>();const [items,setItems]=useState<Interaction[]>([]);const [overdue,setOverdue]=useState<any[]>([]);const [form]=Form.useForm()
 const loadLeads=async()=>setLeads((await api.get('/api/leads',{params:{page_size:100}})).data.items)
 const loadInteractions=async(id?:number)=>{if(!id)return setItems([]);setItems((await api.get(`/api/s3/care/leads/${id}/interactions`)).data)}
 const loadOverdue=async()=>setOverdue((await api.get('/api/s3/care/reminders',{params:{overdue_only:true}})).data)
 useEffect(()=>{loadLeads().catch(()=>undefined);loadOverdue().catch(()=>undefined)},[])
 const submit=async(values:any)=>{if(!leadId)return message.warning('Chọn lead.');try{await api.post(`/api/s3/care/leads/${leadId}/interactions`,{interaction_type:values.interaction_type,content:values.content,reminder_at:values.reminder_at?.toISOString()});message.success('Đã lưu nhật ký chăm sóc.');form.resetFields();await Promise.all([loadInteractions(leadId),loadOverdue()])}catch(e){message.error(apiErrorMessage(e))}}
 const complete=async(id:number)=>{try{await api.patch(`/api/s3/care/interactions/${id}/complete-reminder`);await Promise.all([loadInteractions(leadId),loadOverdue()])}catch(e){message.error(apiErrorMessage(e))}}
 return <Space direction="vertical" size="middle" style={{width:'100%'}}>
  {overdue.length>0&&<Alert type="warning" showIcon message={`${overdue.length} lead đang quá hạn gọi lại`} description={overdue.map(x=>`${x.lead_name} (${x.lead_phone})`).join(', ')}/>} 
  <Card title="S3-02 · Nhật ký chăm sóc và nhắc gọi lại"><Select showSearch optionFilterProp="label" placeholder="Chọn lead" style={{width:320}} value={leadId} onChange={id=>{setLeadId(id);void loadInteractions(id)}} options={leads.map(x=>({value:x.id,label:`${x.full_name} · ${x.phone}`}))}/><Form form={form} layout="vertical" onFinish={submit} style={{marginTop:16}}><Space align="start" wrap><Form.Item name="interaction_type" label="Loại" rules={[{required:true}]}><Select style={{width:150}} options={[{value:'call',label:'Gọi'},{value:'message',label:'Nhắn'},{value:'meeting',label:'Gặp'}]}/></Form.Item><Form.Item name="reminder_at" label="Nhắc gọi lại"><DatePicker showTime/></Form.Item></Space><Form.Item name="content" label="Nội dung" rules={[{required:true}]}><Input.TextArea rows={3}/></Form.Item><Button type="primary" htmlType="submit">Lưu tương tác</Button></Form></Card>
  <Card title="Lịch sử"><List dataSource={items} locale={{emptyText:'Chưa có tương tác'}} renderItem={x=><List.Item actions={x.reminder_at&&!x.reminder_completed_at?[<Button size="small" onClick={()=>void complete(x.id)}>Hoàn tất nhắc</Button>]:[]}><List.Item.Meta title={<Space><Tag>{x.interaction_type}</Tag><span>{new Date(x.occurred_at).toLocaleString()}</span>{x.is_overdue&&<Tag color="error">Quá hạn</Tag>}</Space>} description={<><Typography.Paragraph>{x.content}</Typography.Paragraph>{x.reminder_at&&<Typography.Text type={x.is_overdue?'danger':'secondary'}>Nhắc: {new Date(x.reminder_at).toLocaleString()}</Typography.Text>}</>}/></List.Item>}/></Card>
 </Space>
}
