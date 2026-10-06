import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
export default function ProtectedRoute({permission:_permission}:{permission?:string}){
 const {user,loading}=useAuth(); if(loading) return <div className="page-center">Đang tải...</div>; if(!user) return <Navigate to="/login" replace/>; return <Outlet/>
}
