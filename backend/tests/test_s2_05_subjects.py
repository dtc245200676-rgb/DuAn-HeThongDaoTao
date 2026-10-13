from app.db.database import SessionLocal
from app.models.training import ProgramSubject,TrainingClass,TrainingProgram
def test_subject_crud_and_guard(client,admin_headers):
    r=client.post('/api/training/subjects',headers=admin_headers,json={'code':'JS1','name':'JS','session_count':2,'weight':50});assert r.status_code==200;sid=r.json()['id'];assert client.post('/api/training/subjects',headers=admin_headers,json={'code':'JS1','name':'Dup'}).status_code==409
    db=SessionLocal();p=TrainingProgram(code='P1',name='P1');db.add(p);db.flush();db.add(ProgramSubject(program_id=p.id,subject_id=sid,order_index=1));db.add(TrainingClass(program_id=p.id,name='C1',status='running'));db.commit();db.close();assert client.delete(f'/api/training/subjects/{sid}',headers=admin_headers).status_code==409
