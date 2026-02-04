import requests

print("Testing onboarding...")
response = requests.post(
    "http://localhost:8000/api/v1/onboarding",
    json={
        "email": "cgutierrez@admin.com",
        "nombre": "Carlos Gutierrez",
        "password": "Admin123!"
    }
)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    data = response.json()
    print(f"Mensaje: {data['mensaje']}")
    print(f"Super Admin Email: {data['super_admin_email']}")
    print("SUCCESS!")
else:
    print(f"ERROR: {response.text}")
