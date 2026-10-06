import { createContext,useCallback,useContext,useEffect,useMemo,useRef,useState } from 'react'
import { api,clearToken,getToken,setToken } from '../api/client'
import type { CurrentUser } from '../types'
interface LoginResult{access_token:string;roles:string[];role:string;must_change_password:boolean;message:string}
interface AuthContextValue{user:CurrentUser|null;loading:boolean;login:(email:string,password:string)=>Promise<LoginResult>;logout:()=>Promise<void>;refreshMe:()=>Promise<CurrentUser|null>;hasPermission:(permission:string)=>boolean}
const AuthContext=createContext<AuthContextValue|null>(null)
export function AuthProvider({children}:{children:React.ReactNode}){
 const [user,setUser]=useState<CurrentUser|null>(null); const [loading,setLoading]=useState(true); const lastActivityRef=useRef(Date.now())
 const refreshMe=useCallback(async()=>{if(!getToken()){setUser(null);return null} const response=await api.get<CurrentUser>('/api/auth/me');setUser(response.data);return response.data},[])
 useEffect(()=>{refreshMe().catch(()=>{clearToken();setUser(null)}).finally(()=>setLoading(false))},[refreshMe])
 useEffect(()=>{const mark=()=>{lastActivityRef.current=Date.now()};const events=['click','keydown','mousemove','touchstart'] as const;events.forEach(e=>window.addEventListener(e,mark,{passive:true}));const interval=window.setInterval(async()=>{const token=getToken();const active=Date.now()-lastActivityRef.current<10*60*1000;if(!token||!active)return;try{const response=await api.post('/api/auth/refresh');setToken(response.data.access_token)}catch{}},5*60*1000);return()=>{window.clearInterval(interval);events.forEach(e=>window.removeEventListener(e,mark))}},[])
 useEffect(()=>{const expired=()=>setUser(null);window.addEventListener('auth:expired',expired);return()=>window.removeEventListener('auth:expired',expired)},[])
 const login=useCallback(async(email:string,password:string)=>{const response=await api.post<LoginResult>('/api/auth/login',{email,password});setToken(response.data.access_token);await refreshMe();return response.data},[refreshMe])
 const logout=useCallback(async()=>{try{if(getToken())await api.post('/api/auth/logout')}finally{clearToken();setUser(null)}},[])
 const value=useMemo<AuthContextValue>(()=>({user,loading,login,logout,refreshMe,hasPermission:(p)=>Boolean(user?.permissions.includes(p))}),[user,loading,login,logout,refreshMe])
 return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export function useAuth(){const v=useContext(AuthContext);if(!v)throw new Error('useAuth must be used inside AuthProvider');return v}
