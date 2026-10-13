import { Button, Card, Form, Input, Select, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import type { TrainingProgramItem } from '../types'

export default function ConsultationPage() {
  const [programs,setPrograms]=useState<TrainingProgramItem[]>([])
  const [done,setDone]=useState<{message:string;commitment:string}|null>(null)
  useEffect(()=>{ api.get('/api/training/public-programs').then(r=>setPrograms(r.data)).catch(()=>setPrograms([])) },[])
  const submit=async(values:any)=>{
    try{
      const {data}=await api.post('/api/leads/public', values)
      setDone(data); message.success(data.message)
    }catch(e){ message.error(apiErrorMessage(e)) }
  }
  if(done) return <Card style={{maxWidth:640,margin:'48px auto'}}><Typography.Title level={3}>Cảm ơn bạn!</Typography.Title><Typography.Paragraph>{done.message}</Typography.Paragraph><Typography.Paragraph strong>{done.commitment}</Typography.Paragraph></Card>
  return <Card title="Đăng ký tư vấn tuyển sinh" style={{maxWidth:640,margin:'48px auto'}}>
    <Form layout="vertical" onFinish={submit}>
      <Form.Item name="website" style={{display:'none'}}><Input autoComplete="off" /></Form.Item>
      <Form.Item label="Họ và tên" name="full_name" rules={[{required:true}]}><Input /></Form.Item>
      <Form.Item label="Số điện thoại" name="phone" rules={[{required:true},{pattern:/^(0|\+84)(3|5|7|8|9)\d{8}$/,message:'Số điện thoại Việt Nam không hợp lệ'}]}><Input /></Form.Item>
      <Form.Item label="Email" name="email" rules={[{type:'email'}]}><Input /></Form.Item>
      <Form.Item label="Nguồn" name="source" initialValue="website"><Select options={[{value:'website',label:'Website'},{value:'facebook',label:'Facebook'},{value:'referral',label:'Giới thiệu'},{value:'other',label:'Khác'}]} /></Form.Item>
      <Form.Item label="Chương trình quan tâm" name="interested_program_id"><Select allowClear options={programs.map(p=>({value:p.id,label:`${p.code} - ${p.name}`}))} /></Form.Item>
      <Button type="primary" htmlType="submit" block>Gửi đăng ký</Button>
    </Form>
  </Card>
}
