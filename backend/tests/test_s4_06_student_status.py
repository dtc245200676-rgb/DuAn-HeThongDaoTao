from datetime import date
from sqlalchemy import select
from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.role import Role
from app.models.sprint3 import ClassEnrollment,StudentProfile
from app.models.sprint4 import StudentStatusHistory
from app.models.training import TrainingClass,TrainingProgram
from app.models.user import User

def test_transfer_preserves_old_enrollment_and_history(client,admin_headers):
 db=SessionLocal()
 try:
  role=db.scalar(select(Role).where(Role.slug=='student'));u=User(full_name='HV',email='hv406@example.com',password_hash=hash_password('Student123'),role='student',status='active',is_active=True,roles=[role]);p=TrainingProgram(code='P406',name='P',total_duration_hours=1,standard_tuition=0,status='active');db.add_all([u,p]);db.flush();sp=StudentProfile(student_code='HV406',user_id=u.id);db.add(sp);c1=TrainingClass(program_id=p.id,name='A',code='C406A',expected_start_date=date.today(),max_students=10,delivery_mode='offline',status='studying');c2=TrainingClass(program_id=p.id,name='B',code='C406B',expected_start_date=date.today(),max_students=10,delivery_mode='offline',status='preparing');db.add_all([c1,c2]);db.flush();db.add(ClassEnrollment(class_id=c1.id,student_id=sp.id,status='active'));db.commit();sid=sp.id;a=c1.id;b=c2.id
 finally:db.close()
 r=client.post(f'/api/s4/student-status/{sid}/transfer',headers=admin_headers,json={'from_class_id':a,'to_class_id':b,'effective_date':date.today().isoformat(),'reason':'Chuyển ca'});assert r.status_code==200,r.text
 db=SessionLocal()
 try:
  old=db.scalar(select(ClassEnrollment).where(ClassEnrollment.student_id==sid,ClassEnrollment.class_id==a));new=db.scalar(select(ClassEnrollment).where(ClassEnrollment.student_id==sid,ClassEnrollment.class_id==b));assert old.status=='transferred' and new.status=='active';assert db.scalar(select(StudentStatusHistory.id).where(StudentStatusHistory.student_id==sid))
 finally:db.close()
