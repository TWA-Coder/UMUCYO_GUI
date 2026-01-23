import requests
import sys
import django
import os
import time

sys.path.append('c:\\Users\\Akaruretwa\\UMUCYO3_MVP')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umucyo_mvp.settings")
django.setup()

from core.models import SoapRequestLog

BASE_URL = 'http://127.0.0.1:8000/web'
TEST_URL = f'{BASE_URL}/test-soap/'

def run_verification():
    print("Verifying Single SOAP Operation (Attempt 2)...")
    
    # 1. Hit URL
    try:
        resp = requests.get(TEST_URL)
        print(f"HTTP Status: {resp.status_code}")
        print(f"Response Body: {resp.text}")
    except Exception as e:
        print(f"Request Error: {e}")

    # 2. Inspect Latest Log
    log = SoapRequestLog.objects.last()
    if log:
        print("\n--- Latest Log Entry ---")
        print(f"ID: {log.id}")
        print(f"Timestamp: {log.timestamp}")
        print(f"Operation: {log.operation}")
        print(f"Status: {log.status}")
        print(f"Error: {log.error_message}")
        print(f"Request Payload (First 500 chars):\n{log.request_payload[:500]}")
        
        # Check if it looks like XML
        if log.request_payload and log.request_payload.lstrip().startswith('<'):
            print("\n[SUCCESS] Payload is XML.")
        else:
            print("\n[INFO] Payload is NOT XML (Likely JSON backup).")
    else:
        print("No logs found.")

if __name__ == "__main__":
    run_verification()
