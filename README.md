# IDOR Vulnerability Demo

This application demonstrates an IDOR (Insecure Direct Object Reference) vulnerability and how to remediate it using JWT authentication and authorization middleware.

## What is IDOR?

IDOR is a security vulnerability that occurs when an application allows a user to access resources they shouldn't be able to see, simply by changing an identifier in the URL or request.

## 🏗️ Project Structure (Clean Code)

```
IDOR/
├── app/                          # Main application code
│   ├── api/                      # API layer and endpoints
│   │   ├── endpoints/            # Endpoints organized by functionality
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── users.py         # User management endpoints
│   │   │   └── documents.py     # Document endpoints with IDOR demonstrations
│   │   └── api.py               # Main API configuration
│   ├── core/                     # Core configuration and utilities
│   │   ├── config.py            # Centralized configurations
│   │   ├── database.py          # Database configuration
│   │   ├── auth.py              # Authentication middleware
│   │   ├── security.py          # Security utilities
│   │   ├── security_enhanced.py # Enhanced JWT authentication
│   │   └── middleware.py        # RLS middleware
│   ├── models/                   # Database models
│   │   ├── user.py              # User model
│   │   └── document.py          # Document model
│   ├── schemas/                  # Pydantic schemas
│   │   ├── user.py              # User validation schemas
│   │   └── document.py          # Document validation schemas
│   ├── services/                 # Business logic
│   │   ├── user_service.py      # User service
│   │   └── document_service.py  # Document service with ownership checks
│   └── main.py                   # Main FastAPI application
├── run.py                        # Entry point to run the application
├── test_mitigations.py           # Comprehensive test script
├── MITIGATION_STRATEGIES.md      # Detailed mitigation documentation
├── requirements.txt              # Project dependencies
└── README.md                     # This file
```

## 🚀 Installation and Setup

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```
   or
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Create demo data:**
   ```bash
   curl http://localhost:8000/api/v1/users/demo/setup
   curl http://localhost:8000/api/v1/documents/demo/setup
   ```

## 📋 Available Endpoints

### 🔴 IDOR Vulnerable Endpoints

- `GET /api/v1/documents/vulnerable/{document_id}` - **VULNERABLE**: Allows access to any document without authentication

### 🟢 Secure Endpoints (Remediation)

- `GET /api/v1/documents/secure/{document_id}` - **SECURE**: Mitigation #1 - Route-level owner check
- `GET /api/v1/documents/rls/{document_id}` - **SECURE**: Mitigation #2 - PostgreSQL RLS demonstration
- `GET /api/v1/documents/secure/me` - Get current user's documents
- `POST /api/v1/documents/` - Create document
- `PUT /api/v1/documents/{document_id}` - Update document
- `DELETE /api/v1/documents/{document_id}` - Delete document

### 🔐 Authentication Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get JWT token

### 👥 User Management Endpoints

- `GET /api/v1/users/me` - Get current user info
- `GET /api/v1/users/` - List all users (for demonstration)
- `GET /api/v1/users/demo/setup` - Create demo users

### 📊 Demo Endpoints

- `GET /api/v1/documents/demo/setup` - Create demo documents

## 🧪 Vulnerability Demonstration

### 1. Create Test Data

```bash
# Create demo data
curl http://localhost:8000/api/v1/users/demo/setup
curl http://localhost:8000/api/v1/documents/demo/setup
```

### 2. Demonstrate IDOR Vulnerability

```bash
# Access any document without authentication (VULNERABLE)
curl http://localhost:8000/api/v1/documents/vulnerable/1
curl http://localhost:8000/api/v1/documents/vulnerable/2
curl http://localhost:8000/api/v1/documents/vulnerable/3
curl http://localhost:8000/api/v1/documents/vulnerable/4
curl http://localhost:8000/api/v1/documents/vulnerable/5
```

### 3. Demonstrate Remediation

```bash
# 1. Login and get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'

# 2. Use token to access own document (SECURE)
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/documents/secure/1

# 3. Try to access another user's document (DENIED)
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/documents/secure/2
```

## 👥 Test Users

The application includes these predefined users (IDs 1-5):

- **ID 1: alice** (password: password123) - Regular user
- **ID 2: bob** (password: password123) - Regular user
- **ID 3: charlie** (password: password123) - Regular user
- **ID 4: diana** (password: password123) - Regular user
- **ID 5: admin** (password: admin123) - Administrator

## 📄 Test Documents

Demo documents are created with these ownership assignments:

- **Document 1**: Alice's Secret Document (Owner: alice)
- **Document 2**: Bob's Work Notes (Owner: bob)
- **Document 3**: Charlie's Personal Diary (Owner: charlie)
- **Document 4**: Diana's Project Plan (Owner: diana)
- **Document 5**: Admin's System Notes (Owner: admin)

## 🛡️ Mitigation Strategies

### Mitigation #1: Route-level Owner Check

- **JWT Authentication**: Requires valid authentication token
- **Explicit Ownership Verification**: Checks resource ownership before access
- **Admin Override**: Admins can access any resource
- **Unified 404**: Prevents user enumeration

### Mitigation #2: PostgreSQL Row-Level Security (RLS)

- **Database-enforced Authorization**: Automatic enforcement at database level
- **Middleware Integration**: Sets PostgreSQL parameters per request
- **Defense in Depth**: Works alongside application-level checks
- **Performance**: Efficient database-level filtering

## 🧪 Testing

### Run Comprehensive Tests

```bash
python test_mitigations.py
```

### Manual Testing Examples

```bash
# Test vulnerable endpoint
curl http://localhost:8000/api/v1/documents/vulnerable/1

# Test secure endpoint with authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/documents/secure/1

# Test RLS endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/documents/rls/1
```

## 📊 Key Differences

| Aspect | Vulnerable Endpoint | Secure Endpoint |
|---------|-------------------|-----------------|
| **Authentication** | Not required | JWT token mandatory |
| **Authorization** | No verification | Verifies resource ownership |
| **Access** | Any document | Owner or admin only |
| **Security** | ❌ Vulnerable | ✅ Secure |

## 📚 API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Clean Code Architecture

### **Separation of Concerns:**
- **API Layer**: Handles HTTP requests and responses
- **Service Layer**: Contains business logic with ownership checks
- **Model Layer**: Defines data models with ownership tracking
- **Schema Layer**: Validates input/output data
- **Core Layer**: Centralized configuration and security utilities

### **Applied Principles:**
- ✅ **Single Responsibility**: Each module has a specific responsibility
- ✅ **Dependency Injection**: Use of FastAPI dependencies
- ✅ **Separation of Concerns**: Clear separation between layers
- ✅ **Configuration Management**: Centralized configuration
- ✅ **Error Handling**: Consistent error handling
- ✅ **Type Hints**: Complete typing for better maintainability

## 🔒 Security Considerations

1. **Change SECRET_KEY** in production
2. **Use HTTPS** in production
3. **Configure CORS** appropriately
4. **Implement rate limiting**
5. **Use environment variables** for sensitive configurations
6. **Audit access logs**
7. **Implement 2FA** for enhanced security

## 🚀 Next Steps

To further improve security, consider:

- Implementing more granular roles and permissions
- Adding access auditing
- Implementing per-user rate limiting
- Using UUIDs instead of sequential IDs
- Implementing stricter input validation
- Adding unit and integration tests
- Setting up PostgreSQL with RLS for production use

## 📖 Additional Documentation

- **MITIGATION_STRATEGIES.md**: Detailed explanation of both mitigation strategies
- **test_mitigations.py**: Comprehensive test script with examples
- **Interactive API docs**: Available at `/docs` when running the application 