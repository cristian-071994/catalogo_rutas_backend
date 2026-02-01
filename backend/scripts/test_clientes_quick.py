import requests

BASE = 'http://127.0.0.1:8000'

print('1) GET /clientes/ (antes)')
r = requests.get(f'{BASE}/clientes/')
print('status', r.status_code, 'count', len(r.json()) if r.status_code==200 else r.text)

print('\n2) POST /clientes/')
r = requests.post(f'{BASE}/clientes/', json={'nombre':'Cliente Test Auto'})
print('status', r.status_code, r.text)
if r.status_code==201:
    cid = r.json()['id']
else:
    # try to find existing
    resp = requests.get(f'{BASE}/clientes/')
    items = resp.json() if resp.status_code==200 else []
    cid = items[0]['id'] if items else None

print('\n3) PUT /clientes/{cid} (actualizar nombre)')
if cid:
    r = requests.put(f'{BASE}/clientes/{cid}', json={'nombre':'Cliente Test Auto Actualizado'})
    print('status', r.status_code, r.text)
else:
    print('No se obtuvo id de cliente para actualizar')

print('\n4) DELETE /clientes/{cid} (soft delete)')
if cid:
    r = requests.delete(f'{BASE}/clientes/{cid}')
    print('status', r.status_code)
else:
    print('No se obtuvo id de cliente para eliminar')

print('\n5) GET /clientes/ (después)')
r = requests.get(f'{BASE}/clientes/')
print('status', r.status_code, 'count', len(r.json()) if r.status_code==200 else r.text)

print('\n6) GET /clientes/?incluir_inactivos=true')
r = requests.get(f'{BASE}/clientes/?incluir_inactivos=true')
print('status', r.status_code, 'count', len(r.json()) if r.status_code==200 else r.text)
