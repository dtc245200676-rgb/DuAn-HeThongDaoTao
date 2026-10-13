import { Card, Tabs } from 'antd'
import ProgramTab from '../features/training/ProgramTab'
import SubjectTab from '../features/training/SubjectTab'
import CurriculumTab from '../features/training/CurriculumTab'
import SessionsTab from '../features/training/SessionsTab'
export default function TrainingManagementPage(){return <Card title="Sprint 2 · Quản lý đào tạo"><Tabs items={[
 {key:'programs',label:'Chương trình',children:<ProgramTab/>},
 {key:'subjects',label:'Môn học',children:<SubjectTab/>},
 {key:'curriculum',label:'Lộ trình chương trình',children:<CurriculumTab/>},
 {key:'sessions',label:'Buổi học',children:<SessionsTab/>},
]}/></Card>}
