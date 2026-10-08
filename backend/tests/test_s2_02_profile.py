def login(client,email,password):
    r=client.post('/api/auth/login',json={'email':email,'password':password});return {'Authorization':f"Bearer {r.json()['access_token']}"}
def test_s2_02_profile(client,user_factory):
    user_factory('student@example.com','Student1234','student',full_name='Student');h=login(client,'student@example.com','Student1234');r=client.put('/api/profile',headers=h,json={'full_name':'Nguyễn Văn Học','phone':'0901234567','date_of_birth':'2002-04-05','address':'Hà Nội'});assert r.status_code==200;rj=r.json();assert rj['email']=='student@example.com' and rj['roles']==['student'];assert client.put('/api/profile',headers=h,json={'full_name':'A','phone':'123','date_of_birth':None,'address':None}).status_code==422
