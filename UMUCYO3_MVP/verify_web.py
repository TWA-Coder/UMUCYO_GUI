import requests
import sys

BASE_URL = 'http://127.0.0.1:8000/web'
LOGIN_URL = 'http://127.0.0.1:8000/web/login/'
RESET_URL = 'http://127.0.0.1:8000/web/accounts/password_reset/'

def run_verification():
    print("Verifying Web UI & Password Reset...")
    session = requests.Session()

    # 1. Check Password Reset Page
    print("1. Accessing Password Reset Page...")
    try:
        resp = session.get(RESET_URL)
        if resp.status_code == 200:
            print("Password Reset Page: OK")
        else:
            print(f"Password Reset Page: FAILED ({resp.status_code})")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    # 2. Login to check Dashboard again (Regression test)
    # ... (Reuse previous logic if needed, or simple check)
    
    # 3. Trigger Reset (Simulate)
    csrftoken = session.cookies.get('csrftoken')
    if not csrftoken:
        # Get one from reset page
        session.get(RESET_URL)
        csrftoken = session.cookies['csrftoken']
        
    print("2. Submitting Password Reset Request...")
    data = {
        'email': 'karuretwaarsene744@gmail.com', # The email of the superuser created earlier
        'csrfmiddlewaretoken': csrftoken
    }
    resp = session.post(RESET_URL, data=data, headers={'Referer': RESET_URL})
    
    if "password_reset/done" in resp.url or "Check your inbox" in resp.text:
         print("Reset Request: SUCCESS (Redirected to Done page)")
    else:
         print(f"Reset Request: FAILED or Different Outcome. URL: {resp.url}")

    print("Verification Complete. Check console for 'Email'.")

if __name__ == "__main__":
    run_verification()
