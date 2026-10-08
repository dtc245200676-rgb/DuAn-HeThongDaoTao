import io
from openpyxl import Workbook

def make(rows):
    wb=Workbook();ws=wb.active;ws.append(['full_name','email','phone','role_slugs'])
    for r in rows:ws.append(r)
    b=io.BytesIO();wb.save(b);return b.getvalue()
def test_s2_01_preview_and_import(client,admin_headers,user_factory):
    user_factory('exists@example.com','Password123','student');raw=make([['A','new@example.com','0901234567','student'],['B','bad-email','0912345678','student'],['C','exists@example.com','0923456789','student']]);f={'file':('users.xlsx',raw,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')};r=client.post('/api/users/import/preview',headers=admin_headers,files=f);assert r.status_code==200 and r.json()['valid']==1 and r.json()['invalid']==2
    f={'file':('users.xlsx',raw,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')};r=client.post('/api/users/import',headers=admin_headers,files=f);assert r.status_code==200 and r.json()['imported_count']==1 and r.json()['skipped_count']==2
