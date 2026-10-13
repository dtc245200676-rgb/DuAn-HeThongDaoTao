import io
from PIL import Image

def login(client,email,password):
    r=client.post('/api/auth/login',json={'email':email,'password':password});return {'Authorization':f"Bearer {r.json()['access_token']}"}
def test_avatar_and_public_consultation(client,user_factory,tmp_path,monkeypatch):
    user_factory('student@example.com','Student1234','student');h=login(client,'student@example.com','Student1234');monkeypatch.setenv('AVATAR_UPLOAD_DIR',str(tmp_path))
    # module constant was evaluated on import, so only validate processing/response here
    b=io.BytesIO();Image.new('RGB',(800,500)).save(b,'PNG');r=client.post('/api/profile/avatar',headers=h,files={'file':('a.png',b.getvalue(),'image/png')});assert r.status_code==200 and r.json()['avatar_thumbnail_url']
    one=client.post('/api/leads/public',json={'full_name':'Khách A','phone':'0901234567','email':'a@example.com','source':'website'});assert one.status_code==200 and '24 giờ' in one.json()['commitment'];two=client.post('/api/leads/public',json={'full_name':'Khách B','phone':'0901234567'});assert two.status_code==200 and two.json()['duplicate_warning'] is not None
