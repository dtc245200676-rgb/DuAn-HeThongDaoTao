import { createContext, useContext } from 'react'
import type { CurrentUser } from '../types'
interface LoginResult { access_token:string; roles:string[]; role:string; must_change_password:boolean; message:string }
interface AuthContextValue { user:CurrentUser|null; loading:boolean; login:(email:string,password:string)=>Promise<LoginResult>; logout:()=>Promise<void>; refreshMe:()=>Promise<CurrentUser|null>; hasPermission:(permission:string)=>boolean }
const C=createContext<AuthContextValue|null>(null)
export function AuthProvider({children}:{children:React.ReactNode}){
  const unavailable=async()=>{throw new Error('Authentication chưa được tích hợp')}
  const value:AuthContextValue={user:null,loading:false,login:unavailable,logout:async()=>{},refreshMe:async()=>null,hasPermission:()=>false}
  return <C.Provider value={value}>{children}</C.Provider>
}
export function useAuth(){const v=useContext(C); if(!v) throw new Error('useAuth must be used inside AuthProvider'); return v}
