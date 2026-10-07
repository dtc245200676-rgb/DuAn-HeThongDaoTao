import { LockOutlined,UnlockOutlined } from '@ant-design/icons'
import { Button,Form,Input,Modal,Space,message } from 'antd'
import { useState } from 'react'
import { api,apiErrorMessage } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import type { UserItem } from '../../types'
export default function AccountLockActions({_user,onSaved}:{_user?:UserItem;onSaved?:()=>void}){
 const {hasPermission}=useAuth();const [open,setOpen]=useState(false);const [form]=Form.useForm();if(!_user||!hasPermission('users.lock'))return null;const action=_user.status==='locked'?'unlock':'lock';const submit=async()=>{try{const v=await form.validateFields();const r=await api.post(`/api/users/${_user.id}/${action}`,v);message.success(r.data.message);if(r.data.handover_warning)message.warning(r.data.handover_warning,6);setOpen(false);form.resetFields();await onSaved?.()}catch(e){if((e as {errorFields?:unknown}).errorFields)return;message.error(apiErrorMessage(e))}}
 return <Space><Button danger={action==='lock'} size="small" icon={action==='lock'?<LockOutlined/>:<UnlockOutlined/>} onClick={()=>setOpen(true)}>{action==='lock'?'Khóa':'Mở khóa'}</Button><Modal title={action==='lock'?'Khóa tài khoản':'Mở khóa tài khoản'} open={open} onCancel={()=>setOpen(false)} onOk={submit}><Form form={form} layout="vertical"><Form.Item name="reason" label="Lý do" rules={[{required:true,min:3,message:'Bắt buộc ghi lý do'}]}><Input.TextArea rows={4}/></Form.Item></Form></Modal></Space>
}
