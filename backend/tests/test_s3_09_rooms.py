from app.db.database import SessionLocal
from app.models.sprint3 import ClassEnrollment, StudentProfile
from app.models.training import TrainingClass, TrainingProgram


def test_room_capacity_warning_and_online_room(client,user_factory,admin_headers):
    s1=user_factory('r91@example.com','Pass1234','student',full_name='SV91')
    s2=user_factory('r92@example.com','Pass1234','student',full_name='SV92')
    db=SessionLocal()
    try:
        p=TrainingProgram(code='P09',name='Program 09',total_duration_hours=1,standard_tuition=0,status='active');db.add(p);db.flush()
        c=TrainingClass(program_id=p.id,name='C09',code='C09',status='studying',max_students=30,delivery_mode='offline');db.add(c);db.flush()
        a=StudentProfile(student_code='HV091',user_id=s1.id);b=StudentProfile(student_code='HV092',user_id=s2.id);db.add_all([a,b]);db.flush();db.add_all([ClassEnrollment(class_id=c.id,student_id=a.id,status='active'),ClassEnrollment(class_id=c.id,student_id=b.id,status='active')]);db.commit();cid=c.id
    finally:db.close()
    room=client.post('/api/s3/rooms',headers=admin_headers,json={'code':'P101','name':'Phòng 101','room_type':'physical','capacity':1}).json()
    assigned=client.put(f'/api/s3/rooms/classes/{cid}/assign',headers=admin_headers,json={'room_id':room['id']})
    assert assigned.status_code==200
    assert '2 học viên' in assigned.json()['warning']
    online=client.post('/api/s3/rooms',headers=admin_headers,json={'code':'ZOOM01','name':'Zoom 01','room_type':'online','online_url':'https://example.com/room'} )
    assert online.status_code==200
    assert online.json()['capacity'] is None
