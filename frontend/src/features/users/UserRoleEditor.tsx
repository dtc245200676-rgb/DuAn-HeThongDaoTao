import { Button,Modal,Select,message } from 'antd'
import { useState } from 'react'
import { api,apiErrorMessage } from '../../api/client'
import { useAuth } from '../../auth/AuthContext'
import type { RoleDetail,UserItem } from '../../types'
export default function UserRoleEditor({_user,_roles,onSaved}:{_user?:UserItem;_roles?:RoleDetail[];onSaved?:()=>void}){
 const {hasPermission}=useAuth();const [open,setOpen]=useState(false);const [values,setValues]=useState<string[]>(_user?.roles.map(r=>r.slug)||[]);if(!_user||!hasPermission('roles.assign'))return null
 const save=async()=>{try{await api.put(`/api/users/${_user.id}/roles`,{role_slugs:values});message.success('Đã cập nhật vai trò');setOpen(false);await onSaved?.()}catch(e){message.error(apiErrorMessage(e))}}
 return <><Button size="small" onClick={()=>{setValues(_user.roles.map(r=>r.slug));setOpen(true)}}>Vai trò</Button><Modal title={`Gán vai trò - ${_user.full_name}`} open={open} onCancel={()=>setOpen(false)} onOk={save}><Select mode="multiple" style={{width:'100%'}} value={values} onChange={setValues} options={(_roles||[]).map(r=>({label:r.name,value:r.slug}))}/></Modal></>
}
