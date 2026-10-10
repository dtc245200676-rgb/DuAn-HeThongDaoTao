from app.db.database import SessionLocal
from app.models.lead import Lead
def login(client,email,password):
    r=client.post('/api/auth/login',json={'email':email,'password':password});return {'Authorization':f"Bearer {r.json()['access_token']}"}
def test_lead_crud_duplicate_and_delete_role(client,user_factory):
    a=user_factory('tv@example.com','Password123','admissions',full_name='TV');h=login(client,'tv@example.com','Password123');r=client.post('/api/leads',headers=h,json={'full_name':'A','phone':'0901234567','status':'new'});assert r.status_code==200 and r.json()['lead']['assignee_user_id']==a.id;r2=client.post('/api/leads',headers=h,json={'full_name':'B','phone':'0901234567','status':'new'});assert r2.status_code==200 and r2.json()['duplicate_warning'];assert client.delete(f"/api/leads/{r.json()['lead']['id']}",headers=h).status_code==403;user_factory('manager@example.com','Password123','training_manager');mh=login(client,'manager@example.com','Password123');assert client.delete(f"/api/leads/{r2.json()['lead']['id']}",headers=mh).status_code==200
