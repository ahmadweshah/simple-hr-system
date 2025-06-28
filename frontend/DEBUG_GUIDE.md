# Frontend Debug & Troubleshooting Guide

## ✅ Issues Fixed

### 1. **Port Mismatch Fixed**
- **Problem**: Frontend was hardcoded to use `http://localhost:8003/api/`
- **Solution**: Backend runs on port 8002, frontend now uses environment variables
- **Config**: Set `VITE_API_BASE_URL=http://localhost:8002/api/` in `.env`

### 2. **Environment Variables Implementation**
- **Added**: `.env` file for frontend configuration
- **Variables**:
  ```
  VITE_API_BASE_URL=http://localhost:8002/api/
  VITE_APP_TITLE=Simple HR System
  VITE_APP_DESCRIPTION=Modern HR System for Candidate Management
  ```

### 3. **CORS Configuration Fixed**
- **Updated**: Backend `.env` to include frontend port 8080
- **Enabled**: CORS middleware in Django settings
- **Config**: `CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8080,http://127.0.0.1:8080`

### 4. **Error Handling Improved**
- **Enhanced**: Network error detection and user-friendly messages
- **Added**: Proper error parsing from backend responses
- **Implemented**: Better error messages in all components

### 5. **API Response Handling Fixed**
- **Problem**: Frontend expected wrong response format from registration API
- **Solution**: Updated `CandidateRegistrationResponse` interface to match backend
- **Fix**: Now properly extracts `candidate_id` from response

### 6. **Download Functionality Implemented**
- **Added**: Complete resume download functionality for admin dashboard
- **Features**: File download with proper filename and error handling

### 7. **Request/Response Debugging**
- **Added**: Axios interceptors for debugging API calls
- **Logging**: All API requests and responses are logged in development mode

## 🔧 Architecture Overview

### Frontend (Port 8080)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS + shadcn/ui
- **HTTP Client**: Axios with interceptors
- **State Management**: React hooks + Context

### Backend (Port 8002)
- **Framework**: Django + Django REST Framework
- **Documentation**: Available at `http://localhost:8002/swagger/`
- **Features**: File upload, candidate management, admin endpoints

### API Flow
1. **File Upload**: `POST /api/upload/` → Returns `file_id`
2. **Registration**: `POST /api/candidates/` → Uses `file_id`, returns `candidate_id`
3. **Status Check**: `GET /api/candidates/{id}/status/`
4. **Admin Functions**: Require `X-ADMIN: 1` header

## 🐛 Debugging Checklist

### If frontend shows connection errors:
1. ✅ Check backend is running on port 8002: `ss -tlnp | grep 8002`
2. ✅ Verify API base URL in browser console logs
3. ✅ Check CORS settings in backend `.env`
4. ✅ Ensure frontend is on port 8080

### If API requests fail:
1. ✅ Check browser Network tab for actual HTTP status codes
2. ✅ Verify request URLs in console logs (should show interceptor logs)
3. ✅ Check backend logs for errors
4. ✅ Test backend API directly: `python test_api_new.py`

### If registration doesn't complete:
1. ✅ Verify file upload returns `file_id`
2. ✅ Check registration request includes valid `file_id`
3. ✅ Ensure backend returns `candidate_id` in response
4. ✅ Check for validation errors in Network tab

## 📊 Test Results

Backend API tests all pass:
- ✅ File upload: Working
- ✅ Candidate registration: Returns proper `candidate_id`
- ✅ Status checking: Working
- ✅ Admin endpoints: Working with `X-ADMIN` header
- ✅ Resume download: Working
- ✅ Status updates: Working

## 🚀 Next Steps

1. **Test the complete frontend flow**:
   - Upload a file
   - Fill out registration form
   - Check if success page shows with real candidate ID

2. **Admin dashboard testing**:
   - Load candidates list
   - Update candidate status
   - Download resumes

3. **Error scenarios**:
   - Test with invalid file types
   - Test without backend running
   - Test with invalid candidate IDs

## 📝 Monitoring

Check browser console for:
- Environment configuration logs
- API request logs (from interceptors)
- Any error messages
- Network failures

All logs are prefixed with component names for easy identification.
