import { Button, Card, Select, Space, Table, Tag, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { api, apiErrorMessage } from '../api/client'
import type { TrainingClassItem } from '../types'

export default function ClassEnrollmentPage(){
 const [classes,setClasses]=useState<TrainingClassItem[]>([]);const [classId,setClassId]=useState<number>();const [data,setData]=useState<any>({enrolled:[],available:[],current:0,max_students:0});const [selected,setSelected]=useState<number[]>([])
 const loadClasses=async()=>setClasses((await api.get('/api/s3/enrollments/classes')).data)
 const load=async(id?:number)=>{if(!id)return;setData((await api.get(`/api/s3/enrollments/classes/${id}/students`)).data)}
 useEffect(()=>{loadClasses().catch(()=>message.error('Không tải được lớp.'))},[])
 const enroll=async()=>{if(!classId||!selected.length)return message.warning('Chọn lớp và học viên.');try{await api.post(`/api/s3/enrollments/classes/${classId}`,{student_ids:selected});message.success(`Đã ghi danh ${selected.length} học viên.`);setSelected([]);await load(classId)}catch(e){message.error(apiErrorMessage(e))}}
 return <Space direction="vertical" style={{width:'100%'}}><Card title="S3-06 · Ghi danh học viên"><Select placeholder="Chọn lớp" style={{width:320}} value={classId} onChange={id=>{setClassId(id);setSelected([]);void load(id)}} options={classes.map(x=>({value:x.id,label:`${x.code} · ${x.program_name}`}))}/>{classId&&<><Typography.Paragraph style={{marginTop:12}}>Sĩ số: <strong>{data.current}/{data.max_students}</strong></Typography.Paragraph><Select mode="multiple" showSearch optionFilterProp="label" placeholder="Chọn nhiều học viên" style={{width:'100%',maxWidth:700}} value={selected} onChange={setSelected} options={data.available.map((x:any)=>({value:x.id,label:`${x.student_code} · ${x.full_name}`}))}/><Button type="primary" style={{marginTop:12}} onClick={()=>void enroll()}>Ghi danh các học viên đã chọn</Button></>}</Card><Card title="Danh sách đã ghi danh"><Table rowKey="enrollment_id" dataSource={data.enrolled} columns={[{title:'Mã HV',dataIndex:'student_code'},{title:'Họ tên',dataIndex:'full_name'},{title:'Email',dataIndex:'email'},{title:'Ngày ghi danh',dataIndex:'enrolled_at'},{title:'Người thực hiện',dataIndex:'enrolled_by',render:v=>v||<Tag>Hệ thống</Tag>}]} /></Card></Space>
}
