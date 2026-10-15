from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.sprint3 import ClassSubject, ClassSubjectStaff
from app.models.training import Subject, TrainingClass, TrainingProgram


def login_headers(client,email,password):
    token=client.post('/api/auth/login',json={'email':email,'password':password}).json()['access_token']
    return {'Authorization':f'Bearer {token}'}


def test_assign_teacher_assistant_and_my_classes(client,user_factory,admin_headers):
    teacher=user_factory('teacher8@example.com','Pass1234','teacher',full_name='GV 8')
    assistant=user_factory('assistant8@example.com','Pass1234','teaching_assistant',full_name='TG 8')
    wrong=user_factory('student8@example.com','Pass1234','student',full_name='SV 8')
    db=SessionLocal()
    try:
        p=TrainingProgram(code='P08',name='Program 08',total_duration_hours=1,standard_tuition=0,status='active')
        s=Subject(code='SUB08',name='Môn 08',session_count=2,weight=100)
        db.add_all([p,s]);db.flush();c=TrainingClass(program_id=p.id,name='C08',code='C08',status='studying',max_students=20,delivery_mode='offline');db.add(c);db.flush();cs=ClassSubject(class_id=c.id,subject_id=s.id,order_index=1);db.add(cs);db.commit();csid=cs.id
    finally:db.close()

    bad=client.put(f'/api/s3/class-staff/class-subjects/{csid}/assign',headers=admin_headers,json={'teacher_user_id':wrong.id,'assistant_user_ids':[assistant.id]})
    assert bad.status_code==422
    ok=client.put(f'/api/s3/class-staff/class-subjects/{csid}/assign',headers=admin_headers,json={'teacher_user_id':teacher.id,'assistant_user_ids':[assistant.id]})
    assert ok.status_code==200,ok.text
    db=SessionLocal()
    try:
        staff=db.scalars(select(ClassSubjectStaff).where(ClassSubjectStaff.class_subject_id==csid)).all();assert len(staff)==2
    finally:db.close()
    mine=client.get('/api/s3/class-staff/my-classes',headers=login_headers(client,'teacher8@example.com','Pass1234'))
    assert mine.status_code==200
    assert [x['code'] for x in mine.json()]==['C08']
