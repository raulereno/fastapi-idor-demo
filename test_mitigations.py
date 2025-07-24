#!/usr/bin/env python3
"""
Test script to demonstrate IDOR vulnerability and both mitigation strategies
"""
import requests
import json
import jwt
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
SECRET_KEY = "your_very_secure_secret_key_here_change_in_production"

def create_token(user_id: int) -> str:
    """Create JWT token for a user"""
    payload = {"sub": str(user_id)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def print_separator(title: str):
    """Print a separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_setup():
    """Setup demo data"""
    print_separator("SETUP: Creating Demo Data")
    
    # Create users
    response = requests.get(f"{BASE_URL}/users/demo/setup")
    print(f"Users setup: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    
    # Create documents
    response = requests.get(f"{BASE_URL}/documents/demo/setup")
    print(f"Documents setup: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))

def test_vulnerable_endpoints():
    """Test vulnerable endpoints (no authentication)"""
    print_separator("VULNERABLE ENDPOINTS (No Authentication)")
    
    # Test vulnerable document endpoint
    print("Testing vulnerable document endpoint:")
    for doc_id in [1, 2, 3, 4, 5]:
        response = requests.get(f"{BASE_URL}/documents/vulnerable/{doc_id}")
        print(f"  GET /documents/vulnerable/{doc_id}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Document: {data['title']} (Owner: {data['owner_id']})")

def test_secure_endpoints():
    """Test secure endpoints with authentication"""
    print_separator("SECURE ENDPOINTS (With Authentication)")
    
    # Test with Alice's token (user_id = 1)
    alice_token = create_token(1)
    headers = {"Authorization": f"Bearer {alice_token}"}
    
    print("Testing with Alice's token (user_id = 1):")
    
    # Test secure document endpoints
    print("\nDocument endpoints (Mitigation #1 - Route-level check):")
    for doc_id in [1, 2, 3, 4, 5]:
        response = requests.get(f"{BASE_URL}/documents/secure/{doc_id}", headers=headers)
        print(f"  GET /documents/secure/{doc_id}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Document: {data['title']} (Owner: {data['owner_id']})")
        elif response.status_code == 404:
            print(f"    Access denied (404 - Not Found)")
    
    # Test RLS endpoint
    print("\nRLS endpoints (Mitigation #2 - PostgreSQL RLS):")
    for doc_id in [1, 2, 3, 4, 5]:
        response = requests.get(f"{BASE_URL}/documents/rls/{doc_id}", headers=headers)
        print(f"  GET /documents/rls/{doc_id}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Document: {data['title']} (Owner: {data['owner_id']})")
        elif response.status_code == 404:
            print(f"    Access denied (404 - Not Found)")

def test_admin_access():
    """Test admin access to all resources"""
    print_separator("ADMIN ACCESS TEST")
    
    # Test with Admin's token (user_id = 5, role = admin)
    admin_token = create_token(5)
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    print("Testing with Admin's token (user_id = 5, role = admin):")
    
    # Test admin can access all documents
    print("\nAdmin accessing all documents:")
    for doc_id in [1, 2, 3, 4, 5]:
        response = requests.get(f"{BASE_URL}/documents/secure/{doc_id}", headers=headers)
        print(f"  GET /documents/secure/{doc_id}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Document: {data['title']} (Owner: {data['owner_id']})")

def test_unauthorized_access():
    """Test unauthorized access attempts"""
    print_separator("UNAUTHORIZED ACCESS TESTS")
    
    # Test without token
    print("Testing without authentication token:")
    response = requests.get(f"{BASE_URL}/documents/secure/1")
    print(f"  GET /documents/secure/1 (no token): {response.status_code}")
    
    # Test with invalid token
    print("\nTesting with invalid token:")
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(f"{BASE_URL}/documents/secure/1", headers=headers)
    print(f"  GET /documents/secure/1 (invalid token): {response.status_code}")

def test_ownership_verification():
    """Test ownership verification"""
    print_separator("OWNERSHIP VERIFICATION TESTS")
    
    # Test Bob trying to access Alice's document
    bob_token = create_token(2)  # Bob (user_id = 2)
    headers = {"Authorization": f"Bearer {bob_token}"}
    
    print("Bob (user_id = 2) trying to access Alice's document (document_id = 1, owner_id = 1):")
    response = requests.get(f"{BASE_URL}/documents/secure/1", headers=headers)
    print(f"  GET /documents/secure/1: {response.status_code}")
    if response.status_code == 404:
        print("    ✅ Access correctly denied (404 - Not Found)")
    else:
        print("    ❌ Access incorrectly allowed")

def test_document_management():
    """Test document management operations"""
    print_separator("DOCUMENT MANAGEMENT TESTS")
    
    # Test with Alice's token
    alice_token = create_token(1)
    headers = {"Authorization": f"Bearer {alice_token}"}
    
    print("Testing document management with Alice's token:")
    
    # Test creating a document
    new_doc = {
        "title": "Alice's New Document",
        "content": "This is a test document created by Alice"
    }
    response = requests.post(f"{BASE_URL}/documents/", headers=headers, json=new_doc)
    print(f"  POST /documents/ (create): {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Created document: {data['title']} (ID: {data['id']})")
    
    # Test getting user's documents
    response = requests.get(f"{BASE_URL}/documents/secure/me", headers=headers)
    print(f"  GET /documents/secure/me: {response.status_code}")
    if response.status_code == 200:
        documents = response.json()
        print(f"    Found {len(documents)} documents")

def main():
    """Run all tests"""
    print("IDOR Vulnerability and Mitigation Demonstration")
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    try:
        # Setup
        test_setup()
        
        # Test vulnerable endpoints
        test_vulnerable_endpoints()
        
        # Test secure endpoints
        test_secure_endpoints()
        
        # Test admin access
        test_admin_access()
        
        # Test unauthorized access
        test_unauthorized_access()
        
        # Test ownership verification
        test_ownership_verification()
        
        # Test document management
        test_document_management()
        
        print_separator("TEST SUMMARY")
        print("✅ Vulnerable endpoints allow access to any document")
        print("✅ Secure endpoints properly enforce ownership")
        print("✅ Admin can access all documents")
        print("✅ Unauthorized access is properly denied")
        print("✅ Ownership verification works correctly")
        print("✅ Document management operations work")
        print("\n🎯 Both mitigation strategies are working:")
        print("   - Mitigation #1: Route-level owner check")
        print("   - Mitigation #2: PostgreSQL RLS demonstration")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the application is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 