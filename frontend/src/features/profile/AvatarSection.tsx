import { Avatar, Button, Space, Upload, message } from 'antd'
import type { UploadFile } from 'antd'
import { useState } from 'react'
import { api, apiErrorMessage } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
const API_BASE=import.meta.env.VITE_API_BASE_URL||'http://127.0.0.1:8000'
export default function AvatarSection(){const {user,refreshMe}=useAuth();const [busy,setBusy]=useState(false);const upload=async({file,onSuccess,onError}:any)=>{const raw=file as UploadFile&{originFileObj?:File};const actual=raw.originFileObj||(file as File);if(actual.size>2*1024*1024){message.error('Ảnh tối đa 2MB.');onError?.(new Error('too large'));return}setBusy(true);const fd=new FormData();fd.append('file',actual);try{await api.post('/api/profile/avatar',fd,{headers:{'Content-Type':'multipart/form-data'}});await refreshMe();message.success('Đã cập nhật ảnh đại diện.');onSuccess?.({})}catch(e){message.error(apiErrorMessage(e));onError?.(e)}finally{setBusy(false)}};return <Space direction="vertical" align="center"><Avatar size={128} src={user?.avatar_thumbnail_url?`${API_BASE}${user.avatar_thumbnail_url}`:undefined}>{(user?.full_name||user?.email||'U')[0]}</Avatar><Upload customRequest={upload} showUploadList={false} accept="image/jpeg,image/png"><Button loading={busy}>Đổi ảnh JPG/PNG ≤ 2MB</Button></Upload></Space>}
