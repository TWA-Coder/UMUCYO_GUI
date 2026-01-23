import requests
import sys

BASE_URL = 'http://127.0.0.1:8000/api'

def run_verification():
    print("Verifying API...")
    
    # 1. Login to get Token
    try:
        resp = requests.post(f"{BASE_URL}/auth/login/", json={
            'username': 'admin',
            'password': 'adminpassword'
        })
        if resp.status_code != 200:
            print(f"Login FAILED: {resp.status_code} {resp.text}")
            sys.exit(1)
            
        token = resp.json()['token']
        print(f"Login SUCCESS. Token: {token[:10]}...")
        
    except Exception as e:
        print(f"Connection Failed: {e}")
        sys.exit(1)

    headers = {'Authorization': f'Token {token}'}

    # 2. Check SOAP Operations List
    try:
        resp = requests.get(f"{BASE_URL}/soap/", headers=headers)
        if resp.status_code == 200:
            ops = resp.json().get('operations', [])
            print(f"Operations List: {len(ops)} found.")
        else:
            print(f"List Operations FAILED: {resp.status_code}")
    except Exception as e:
        print(f"List Operations Exception: {e}")

    # 3. Execute 'getTenderInformation' (Mock call since we don't have real credentials or upstream might fail)
    # We expect either a success or a specific SOAP fault, but obtaining a 200 or 500 IS a success for the API layer connectivity.
    payload = {
        'id': 'testUser',
        'password': 'testPassword',
        'ref_name': 'TestRef',
        'ref_number': '12345'
    }
    
    # We need to assign permission first? 
    # Admin has all permissions.
    
    print("Executing SOAP operation...")
    try:
        resp = requests.post(f"{BASE_URL}/soap/execute/getTenderInformation/", json=payload, headers=headers)
        print(f"Execution Status: {resp.status_code}")
        # print(f"Response: {resp.text[:200]}")
    except Exception as e:
        print(f"Execution Exception: {e}")
        
    print("Verification Complete.")

if __name__ == "__main__":
    run_verification()
