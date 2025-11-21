# Project Analysis: Student Course Selection System

## Project Overview
**Name**: Online University Course Selection System (在线大学生选课系统)
**Version**: v1.2.3
**Tech Stack**: Vue.js 3 + FastAPI + MySQL

---

## What Was Cleaned Up

### Removed Files (15,782 files, 193MB)
| Category | Files | Size | Purpose |
|----------|-------|------|---------|
| `node_modules/` | 15,777 | 193MB | NPM dependencies - should be regenerated with `npm install` |
| `__pycache__/` | 5 | ~50KB | Python bytecode cache - auto-generated |

**Why removed**: These files should never be committed to git. They are generated files that:
- Can be recreated with `npm install` and running Python
- Waste repository space
- Cause merge conflicts
- Slow down git operations

---

## Current Project Features

### Core Academic Features
- Student registration and authentication (JWT-based)
- Course browsing and enrollment
- Grade management and viewing
- Department/faculty management
- My courses view with enrollment status

### Social Features
- Friend request system (send/accept/reject/block)
- Friend recommendations based on mutual friends & department
- Student-to-student private messaging
- Message read/unread status tracking

### Financial Features
- Student wallet balance management
- Peer-to-peer money transfers
- Transaction history with timestamps
- Risk level assessment for suspicious transfers
- Daily transaction limits

### System Features
- Health check endpoint
- Logging and slow request monitoring
- CORS support for frontend
- Global exception handling
- Admin panel endpoints

---

## Frontend Files List

### Core Files
| File | Description |
|------|-------------|
| `frontend/index.html` | HTML entry point |
| `frontend/package.json` | Dependencies: Vue 3, Element Plus, Axios, ECharts, Pinia |
| `frontend/vite.config.js` | Vite build configuration |
| `frontend/src/main.js` | Vue app bootstrap and plugin setup |
| `frontend/src/App.vue` | Root Vue component |

### Routing & State
| File | Description |
|------|-------------|
| `frontend/src/router/index.js` | Vue Router configuration with guards |
| `frontend/src/stores/auth.js` | Pinia store for authentication state |
| `frontend/src/api/request.js` | Axios HTTP client with interceptors |

### Layout & Styles
| File | Description |
|------|-------------|
| `frontend/src/layout/index.vue` | Main app layout with sidebar/header |
| `frontend/src/style/main.scss` | Global SCSS styles |

### Views (Pages)
| File | Description | Status |
|------|-------------|--------|
| `src/views/Welcome.vue` | Landing/welcome page | Complete |
| `src/views/auth/Login.vue` | User login form | Complete |
| `src/views/auth/Register.vue` | User registration form | Complete |
| `src/views/dashboard/index.vue` | User dashboard | Complete |
| `src/views/courses/List.vue` | Browse all courses | Complete |
| `src/views/courses/MyCourses.vue` | Enrolled courses list | Complete |
| `src/views/messages/index.vue` | Message inbox | Complete |
| `src/views/messages/Compose.vue` | Send new message | Complete |
| `src/views/transactions/Transfer.vue` | Money transfer form | Complete |
| `src/views/error/404.vue` | 404 error page | Complete |

### Missing Frontend Views (TODO)
These are referenced in router but not implemented:
- `CourseDetail.vue` - Course details page
- `FriendList.vue` - Friends list
- `FriendRequests.vue` - Pending friend requests
- `FriendRecommendations.vue` - Suggested friends
- `TransactionHistory.vue` - Transfer history
- `Balance.vue` - Wallet balance
- `Profile.vue` - User profile

---

## Backend Files List

### Core Files
| File | Description |
|------|-------------|
| `backend/main.py` | FastAPI app entry point |
| `backend/requirements.txt` | Python dependencies |
| `backend/app/core/config.py` | Settings with pydantic |
| `backend/app/db/mysql_client.py` | MySQL database client |
| `backend/app/utils/security.py` | JWT, password hashing |

### API Endpoints
| File | Endpoints |
|------|-----------|
| `auth.py` | Login, Register, Refresh, Logout, Me |
| `courses.py` | CRUD for courses, enrollment info |
| `departments.py` | CRUD + related students/courses |
| `enrollments.py` | Enroll, drop, grades, statistics |
| `students.py` | Profile, list, status management |
| `friendships.py` | Friend requests, list, recommendations |
| `transactions.py` | Transfer, balance, history |
| `messages.py` | Send, inbox, sent, read status |

### Database Schema
Located in `database/init.sql`:
- **10 tables**: departments, students, administrators, courses, enrollments, friendships, transactions, messages, login_logs, system_config
- **Triggers**: Auto-update enrollment counts
- **Views**: student_grades, friend_relationships
- **Stored Procedures**: RecommendFriends()

---

## Feature Roadmap (Brainstorm)

### High Priority (Next Sprint)
1. **Complete missing frontend views** - Profile, Friends, Transaction History
2. **Admin dashboard** - Manage users, courses, view statistics
3. **Course search/filter** - By department, instructor, schedule
4. **Notification system** - In-app notifications for events

### Medium Priority (Future)
5. **Course scheduling conflict detection** - Prevent double-booking
6. **Email verification** - Verify student emails
7. **Password reset** - Forgot password flow
8. **File uploads** - Course materials, profile photos
9. **Real-time messaging** - WebSocket for instant messages
10. **Course prerequisites** - Enforce course requirements

### Nice to Have (Backlog)
11. **Course ratings/reviews** - Student feedback on courses
12. **Academic calendar** - Important dates integration
13. **Export to PDF** - Download grades/transcripts
14. **PWA support** - Mobile-friendly progressive web app
15. **2FA authentication** - Two-factor security
16. **Analytics dashboard** - Charts with ECharts library
17. **Bulk operations** - Mass enrollment/messaging
18. **API rate limiting** - Prevent abuse
19. **Audit logging** - Track all system changes
20. **Data export** - GDPR compliance

---

## Technical Improvements Needed

### Code Quality
1. Remove duplicate `app/core/config_simple.py`
2. Move test files to `tests/` directory
3. Add proper pytest test suite
4. Add `.env.example` for environment setup
5. Standardize Chinese/English in codebase

### DevOps
1. Add Docker configuration
2. Add CI/CD pipeline (GitHub Actions)
3. Add database migrations (Alembic)
4. Add API documentation (Swagger is built-in)
5. Add monitoring/logging infrastructure

### Security
1. Add input validation for all endpoints
2. Implement rate limiting
3. Add CSRF protection
4. Secure sensitive data in logs
5. Add security headers

---

## Getting Started

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Database
```bash
mysql -u root -p < database/init.sql
```

---

## Summary

This is a well-architected full-stack student portal with academic, social, and financial features. The backend API is comprehensive with 8 endpoint modules. The main gaps are:
- Several frontend views are incomplete
- No admin panel
- Missing automated tests
- No deployment configuration

The project is estimated at **70% complete** for core functionality.
