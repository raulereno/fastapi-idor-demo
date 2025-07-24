# IDOR Mitigation Strategies

This document explains the two main strategies implemented to mitigate IDOR (Insecure Direct Object Reference) vulnerabilities.

## Overview

IDOR vulnerabilities occur when an application allows users to access resources they shouldn't have access to by simply changing an identifier in the URL or request. This implementation demonstrates two complementary mitigation strategies:

1. **Mitigation #1: Route-level owner check** - Application-level authorization
2. **Mitigation #2: PostgreSQL Row-Level Security (RLS)** - Database-level authorization

## Mitigation #1: Route-level Owner Check

### How it Works

This approach adds explicit ownership verification in the route handler before returning the resource.

### Implementation

```python
@app.get("/documents/{document_id}")
def get_document_secure(
    document_id: int, 
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Get current user to check admin status
    current_user = db.query(User).filter(User.id == current_user_id).first()
    is_admin = current_user.role == "admin" if current_user else False
    
    document = DocumentService.get_document_with_ownership_check(
        db, document_id, current_user_id, is_admin
    )
    
    if not document:
        # Unified 404 prevents user enumeration
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document
```

### Key Features

- **Explicit ownership check**: Verifies resource ownership before access
- **Admin override**: Admins can access any resource
- **Unified 404**: Returns same error for non-existent and unauthorized resources
- **JWT authentication**: Requires valid authentication token

### Pros

- ✅ Simple to implement
- ✅ Works with any database
- ✅ Explicit and easy to understand
- ✅ Can handle complex authorization logic

### Cons

- ❌ Easy to forget on new routes
- ❌ Requires developer discipline
- ❌ Can be bypassed if not implemented consistently

## Mitigation #2: PostgreSQL Row-Level Security (RLS)

### How it Works

This approach uses PostgreSQL's built-in Row-Level Security to enforce access control at the database level.

### Implementation

#### 1. Enable RLS on the table

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
```

#### 2. Create RLS policy

```sql
CREATE POLICY doc_owner_select
  ON documents FOR SELECT
  USING (owner_id = current_setting('app.user_id')::int);
```

#### 3. Set app.user_id parameter per request

```python
class SetAppUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            with request.app.state.db.connect() as conn:
                conn.execute(text("SET app.user_id = :uid"), {"uid": user_id})
        response = await call_next(request)
        return response
```

### Key Features

- **Database-enforced**: Authorization happens at the database level
- **Automatic enforcement**: Cannot be bypassed by application code
- **Performance**: Efficient database-level filtering
- **Defense in depth**: Works alongside application-level checks

### Pros

- ✅ Cannot be bypassed by application code
- ✅ Automatic enforcement for all queries
- ✅ Database-level performance
- ✅ Defense in depth

### Cons

- ❌ PostgreSQL-specific
- ❌ More complex setup
- ❌ Requires database privileges
- ❌ May not handle complex authorization logic

## Combined Approach: Defense in Depth

The best practice is to combine both strategies:

```python
@app.get("/documents/{document_id}")
def get_document_secure(
    document_id: int, 
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Mitigation #1: Application-level check
    current_user = db.query(User).filter(User.id == current_user_id).first()
    is_admin = current_user.role == "admin" if current_user else False
    
    document = DocumentService.get_document_with_ownership_check(
        db, document_id, current_user_id, is_admin
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Mitigation #2: RLS automatically enforced at database level
    return document
```

## Testing the Mitigations

### 1. Run the test script

```bash
python test_mitigations.py
```

### 2. Manual testing

#### Test vulnerable endpoint (should allow access):

```bash
# Access any document without authentication
curl http://localhost:8000/api/v1/documents/vulnerable/1
curl http://localhost:8000/api/v1/documents/vulnerable/2
```

#### Test secure endpoint (should enforce ownership):

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'

# Use token to access own document (should work)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/documents/secure/1

# Try to access another user's document (should fail)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/documents/secure/2
```

## Security Considerations

### 1. Token Security

- Use strong secret keys
- Implement token expiration
- Use HTTPS in production
- Consider token refresh mechanisms

### 2. Error Handling

- Use unified 404 responses to prevent user enumeration
- Don't leak sensitive information in error messages
- Log security events for monitoring

### 3. Database Security

- Use parameterized queries to prevent SQL injection
- Implement proper connection pooling
- Use least privilege database accounts
- Enable SSL for database connections

### 4. Monitoring and Logging

- Log all access attempts
- Monitor for suspicious patterns
- Implement rate limiting
- Set up alerts for security events

## Best Practices

1. **Always implement authentication** before authorization
2. **Use both application and database-level checks** for defense in depth
3. **Test thoroughly** with different user roles and scenarios
4. **Document your security model** clearly
5. **Regular security audits** of your authorization logic
6. **Keep dependencies updated** to patch security vulnerabilities
7. **Use security headers** and HTTPS in production
8. **Implement proper session management**

## Conclusion

Both mitigation strategies are effective, but they work best when combined:

- **Route-level checks** provide explicit, understandable authorization logic
- **RLS** provides automatic, database-enforced security
- **Together** they provide defense in depth against IDOR vulnerabilities

The key is to implement both consistently across your application and test thoroughly to ensure they work as expected. 