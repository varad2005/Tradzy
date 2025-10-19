# 🔐 TRADZY Login Flow Chart

## Complete Authentication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER STARTS HERE                             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   http://localhost:5000  │
                    │      (Home Page)         │
                    └─────────────────────────┘
                                  │
                                  │ Clicks "Login" Button
                                  ▼
                    ┌─────────────────────────┐
                    │  /login (Login Portal)   │
                    │  login.html              │
                    └─────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │  Choose Your Portal       │
                    └─────────────┬─────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
    ┌──────────────┐      ┌──────────────┐    ┌──────────────┐
    │ Admin Login  │      │Retailer Login│    │Wholesaler    │
    │              │      │              │    │Login         │
    └──────────────┘      └──────────────┘    └──────────────┘
            │                     │                     │
            │                     │                     │
            ▼                     ▼                     ▼
    ┌──────────────┐      ┌──────────────┐    ┌──────────────┐
    │ /admin.html  │      │/retailer.html│    │/wholesaler   │
    │              │      │              │    │.html         │
    └──────────────┘      └──────────────┘    └──────────────┘
            │                     │                     │
            └─────────────────────┴─────────────────────┘
                                  │
                                  │ User Enters:
                                  │ • Email/Username
                                  │ • Password
                                  ▼
                    ┌─────────────────────────┐
                    │  JavaScript Form Submit  │
                    │  (api.js - login())      │
                    └─────────────────────────┘
                                  │
                                  │ POST Request
                                  ▼
                    ┌─────────────────────────┐
                    │  /api/auth/login         │
                    │  (Backend API)           │
                    └─────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │  Validate Credentials     │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │  ✅ VALID         │        │  ❌ INVALID       │
          │  Credentials      │        │  Credentials     │
          └──────────────────┘        └──────────────────┘
                    │                           │
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │ Create JWT Token  │        │ Return 401 Error  │
          │ Set Session:      │        │ Show Error Msg    │
          │ • user_id         │        └──────────────────┘
          │ • role            │                  │
          │ • permanent       │                  │
          └──────────────────┘                  │
                    │                           │
                    │                           └──────┐
                    ▼                                  │
          ┌──────────────────┐                        │
          │ Determine Role:   │                        │
          │ • admin           │                        │
          │ • retailer        │                        │
          │ • wholesaler      │                        │
          └──────────────────┘                        │
                    │                                  │
        ┌───────────┼───────────┐                     │
        │           │           │                     │
        ▼           ▼           ▼                     │
┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  Admin   │ │ Retailer │ │Wholesaler│               │
│  Role    │ │   Role   │ │   Role   │               │
└──────────┘ └──────────┘ └──────────┘               │
        │           │           │                     │
        ▼           ▼           ▼                     │
┌──────────┐ ┌──────────┐ ┌──────────┐               │
│ redirect:│ │ redirect:│ │ redirect:│               │
│  /admin  │ │/retailer │ │/wholesaler               │
│          │ │          │ │/dashboard│               │
└──────────┘ └──────────┘ └──────────┘               │
        │           │           │                     │
        │           │           │                     │
        └───────────┴───────────┘                     │
                    │                                  │
                    ▼                                  │
          ┌──────────────────┐                        │
          │ JavaScript        │                        │
          │ window.location   │                        │
          │ .href = redirect  │                        │
          └──────────────────┘                        │
                    │                                  │
        ┌───────────┼───────────┐                     │
        │           │           │                     │
        ▼           ▼           ▼                     │
┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  /admin  │ │/retailer │ │/wholesaler               │
│  Route   │ │  Route   │ │/dashboard│               │
└──────────┘ └──────────┘ └──────────┘               │
        │           │           │                     │
        ▼           ▼           ▼                     │
┌──────────┐ ┌──────────┐ ┌──────────┐               │
│ Check    │ │ Check    │ │ Check    │               │
│ Session  │ │ Session  │ │ Session  │               │
│ & Role   │ │ & Role   │ │ & Role   │               │
└──────────┘ └──────────┘ └──────────┘               │
        │           │           │                     │
        ▼           ▼           ▼                     │
┌──────────┐ ┌──────────┐ ┌──────────┐               │
│ Serve    │ │ Serve    │ │ Serve    │               │
│ admin_   │ │retailer_ │ │wholesaler│               │
│dashboard │ │dashboard │ │_dashboard│               │
│.html     │ │.html     │ │.html     │               │
└──────────┘ └──────────┘ └──────────┘               │
        │           │           │                     │
        └───────────┴───────────┘                     │
                    │                                  │
                    ▼                                  │
          ┌──────────────────┐                        │
          │ ✅ USER LOGGED IN │                        │
          │ Dashboard Loaded  │                        │
          └──────────────────┘                        │
                                                       │
                                                       ▼
                                            ┌──────────────────┐
                                            │ ❌ LOGIN FAILED   │
                                            │ Stay on Login     │
                                            │ Show Error        │
                                            └──────────────────┘
```

---

## 📋 Detailed Step-by-Step Flow

### **Phase 1: Portal Selection**
```
1. User visits /login
2. login.html displays three cards:
   ├─ Admin Login
   ├─ Retailer Login
   └─ Wholesaler Login
3. User clicks on one card
4. Redirects to specific portal page
```

### **Phase 2: Credential Entry**
```
1. Portal page loads (admin.html, retailer.html, or wholesaler.html)
2. User sees login form with:
   ├─ Email/Username field
   ├─ Password field
   └─ Submit button
3. User enters credentials
4. Clicks "Sign In" button
```

### **Phase 3: Form Submission**
```
1. JavaScript prevents default form submission
2. api.js login() function called
3. Validates input fields
4. Shows loading state on button
5. Sends POST request to /api/auth/login with:
   {
     "email": "user@email.com",
     "password": "password123"
   }
```

### **Phase 4: Backend Authentication**
```
1. Flask route /api/auth/login receives request
2. Extracts email and password from JSON
3. Queries database for user:
   SELECT * FROM users WHERE email = ? OR username = ?
4. If user not found → Return 401 error
5. If user found → Check password with check_password_hash()
6. If password wrong → Return 401 error
7. If password correct → Continue to next phase
```

### **Phase 5: Session Creation**
```
1. Generate JWT access token
2. Create Flask session:
   session.clear()
   session["user_id"] = user["id"]
   session["role"] = user["role"]
   session.permanent = True
3. Determine redirect URL based on role:
   ├─ admin → /admin
   ├─ retailer → /retailer
   └─ wholesaler → /wholesaler/dashboard
```

### **Phase 6: Response & Redirect**
```
1. Backend returns JSON response:
   {
     "message": "Login successful",
     "access_token": "eyJ0eXAi...",
     "redirect": "/wholesaler/dashboard",
     "user": {
       "id": 8,
       "username": "wholesaler",
       "email": "wholesaler@tradzy.com",
       "role": "wholesaler"
     }
   }
2. JavaScript receives response
3. Stores JWT token in localStorage
4. Stores user data in localStorage
5. Shows success message
6. Redirects to dashboard: window.location.href = redirect
```

### **Phase 7: Dashboard Access**
```
1. Browser navigates to dashboard route
2. Flask route checks:
   ├─ Is user_id in session? → No → Redirect to login
   └─ Is role correct? → No → Redirect to login
3. If both checks pass → Serve dashboard template
4. Dashboard loads with full functionality
```

---

## 🔄 Error Handling Flow

```
User Input Error
├─ Empty email → "Please enter both email and password"
├─ Empty password → "Please enter both email and password"
└─ Invalid format → Validation error message

Backend Error
├─ 401 Unauthorized → "Invalid credentials"
├─ 400 Bad Request → "Missing required fields"
├─ 500 Server Error → "Login failed - Server error"
└─ Network Error → "Connection failed"

Role Mismatch
├─ Admin tries retailer → Redirect to login
├─ Retailer tries admin → Redirect to login
└─ Wholesaler tries retailer → Redirect to login
```

---

## 🔐 Security Features

### **Session Management:**
- ✅ Secure session cookies
- ✅ Permanent sessions (persistent login)
- ✅ Session cleared on logout
- ✅ CSRF protection (Talisman)

### **Password Security:**
- ✅ Passwords hashed with werkzeug.security
- ✅ No plain text passwords stored
- ✅ Secure password comparison

### **Role-Based Access:**
- ✅ Routes protected by role checks
- ✅ Unauthorized access redirects to login
- ✅ Each role has specific dashboard

### **Token Management:**
- ✅ JWT tokens for API authentication
- ✅ Tokens stored securely in localStorage
- ✅ Token included in API requests

---

## 📊 Data Flow Summary

```
Frontend              API Layer           Backend              Database
────────              ─────────           ───────              ────────
login.html     →                                            
              ↓
[Portal Card Click]
              ↓
wholesaler.html →                                            
              ↓
[Form Submit]  →     POST /api/         →                    
              ↓      auth/login          ↓                    
                                    Validate                  
                                    Credentials  →     Query users
                                         ↓                    table
                                         ←─────────────  Return user
                                         ↓                    
                                    Create Session            
                                    Generate JWT              
                                         ↓                    
              ←─────  Return JSON   ←────┘                    
              ↓       with redirect                           
[Redirect]    →                                               
              ↓                                                
/wholesaler/  →     GET /wholesaler/→                         
dashboard           dashboard        ↓                        
              ↓                  Check Session                
              ←─────  Return HTML ←────┘                      
              ↓                                                
[Dashboard                                                    
Loaded]                                                       
```

---

## 🎯 Key Files Involved

| File | Purpose |
|------|---------|
| `login.html` | Portal selection page |
| `wholesaler.html` | Wholesaler login form |
| `api.js` | Frontend API communication |
| `routes/auth.py` | Backend authentication logic |
| `app.py` | Dashboard route definitions |
| `db.py` | Database connection utilities |
| `wholesaler_dashboard.html` | Dashboard interface |

---

## ✨ Login Credentials (Test Users)

```
Admin:
📧 admin@tradzy.com
🔑 admin123

Retailer:
📧 retailer@tradzy.com
🔑 retailer123

Wholesaler:
📧 wholesaler@tradzy.com
🔑 wholesaler123
```

---

**🎉 Complete, Secure, and Production-Ready Login Flow!**
