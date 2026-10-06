import axios from 'axios'
const API_BASE_URL=import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const TOKEN_KEY='access_token'
export const api=axios.create({baseURL:API_BASE_URL,headers:{'Content-Type':'application/json'}})
export const getToken=()=>localStorage.getItem(TOKEN_KEY)
export const setToken=(token:string)=>localStorage.setItem(TOKEN_KEY,token)
export const clearToken=()=>localStorage.removeItem(TOKEN_KEY)
api.interceptors.request.use((config)=>{const token=getToken(); if(token) config.headers.Authorization=`Bearer ${token}`; return config})
export function apiErrorMessage(error:unknown,fallback='Có lỗi xảy ra. Vui lòng thử lại.'){
  if(axios.isAxiosError(error)){const detail=error.response?.data?.detail; if(typeof detail==='string') return detail; if(detail && typeof detail.message==='string') return detail.message}
  return fallback
}
