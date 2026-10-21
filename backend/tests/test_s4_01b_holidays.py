def test_holiday_crud(client,admin_headers):
 r=client.post('/api/s4/holidays',headers=admin_headers,json={'holiday_date':'2026-12-24','name':'Nghỉ lễ'});assert r.status_code==200,r.text;hid=r.json()['id']
 assert client.post('/api/s4/holidays',headers=admin_headers,json={'holiday_date':'2026-12-24','name':'Trùng'}).status_code==409
 r=client.put(f'/api/s4/holidays/{hid}',headers=admin_headers,json={'name':'Nghỉ lễ cập nhật'});assert r.status_code==200 and 'cập nhật' in r.json()['name']
 assert len(client.get('/api/s4/holidays',headers=admin_headers).json())==1
 assert client.delete(f'/api/s4/holidays/{hid}',headers=admin_headers).status_code==200
