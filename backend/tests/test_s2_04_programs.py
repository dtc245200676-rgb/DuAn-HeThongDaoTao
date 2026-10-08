from app.db.database import SessionLocal
from app.models.training import TrainingClass
def test_program_crud_and_guard(client,admin_headers):
    r=client.post('/api/training/programs',headers=admin_headers,json={'code':'CG01','name':'Fullstack','total_duration_hours':600,'standard_tuition':30000000,'status':'active'});assert r.status_code==200;pid=r.json()['id'];assert client.post('/api/training/programs',headers=admin_headers,json={'code':'CG01','name':'Dup'}).status_code==409
    db=SessionLocal();db.add(TrainingClass(program_id=pid,name='C1',status='running'));db.commit();db.close();assert client.delete(f'/api/training/programs/{pid}',headers=admin_headers).status_code==409
