# File Upload Troubleshooting Guide

## Problem Description
The frontend UI on Vercel fails when trying to upload a 5MB PDF file. This is likely due to Vercel's serverless function limitations.

## Root Cause Analysis

### Vercel Limitations
- **Payload Size Limit**: Vercel serverless functions have a 4.5MB payload limit
- **Execution Time**: Functions timeout after 10 seconds (Hobby plan) or 60 seconds (Pro plan)
- **Memory**: Limited memory allocation for processing large files

### Current Implementation Issues
1. No client-side file size validation for Vercel limits
2. Insufficient error logging and user feedback
3. No progress indication for large uploads
4. PDF files are not properly supported (only text files work)

## Solutions Implemented

### 1. Enhanced Frontend Error Handling
- Added detailed console logging for debugging
- Implemented Vercel-specific file size warnings (4.5MB limit)
- Improved error messages with specific guidance
- Added progress indication for uploads

### 2. Enhanced API Error Handling
- Added comprehensive logging throughout the upload process
- Implemented multiple file size checks (before and after reading)
- Better error messages for different failure scenarios
- Detailed logging for debugging Vercel deployment issues

### 3. Test Script
- Created `test_upload.py` for local testing
- Tests various file sizes to identify breaking points
- Helps diagnose issues before deployment

## Testing Instructions

### Local Testing
1. **Start the API locally** (from root directory):
   ```bash
   # Option 1: Use the convenience script (recommended)
   python run_api.py
   
   # Option 2: Manual setup
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r api/requirements.txt
   python run_api.py
   ```

2. **Start the frontend locally**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Test with the test script**:
   ```bash
   python test_upload.py
   ```

4. **Test specific file**:
   ```bash
   python test_upload.py path/to/your/5mb.pdf
   ```

### Vercel Testing
1. Deploy the updated code to Vercel
2. Open browser developer tools (F12)
3. Try uploading your 5MB PDF
4. Check console logs for detailed error information
5. Check Vercel function logs in the dashboard

## Expected Behavior

### Files Under 4.5MB
- Should upload successfully
- Progress indication shown
- Success message displayed

### Files 4.5MB - 10MB
- Client-side warning about Vercel limits
- Upload may fail with specific error message
- Detailed error logging in console

### Files Over 10MB
- Client-side rejection
- Clear error message about size limit

## Debugging Steps

### 1. Check Browser Console
Look for these log messages:
- File upload details (name, size, type)
- Upload request/response information
- Detailed error messages

### 2. Check Vercel Function Logs
- Go to Vercel dashboard
- Navigate to your project
- Check "Functions" tab for error logs
- Look for timeout or memory errors

### 3. Test File Types
- **Text files (.txt)**: Should work up to 4.5MB
- **PDF files (.pdf)**: Will fail (not supported in current implementation)
- **Word documents (.doc, .docx)**: Will fail (not supported)

## Alternative Solutions

### 1. Reduce File Size
- Compress PDFs before upload
- Split large documents into smaller chunks
- Use text files instead of PDFs

### 2. Use Different Platform
- Deploy API to a platform without payload limits (Railway, Heroku, AWS)
- Use cloud storage (S3, Cloudinary) for file uploads
- Implement chunked uploads for large files

### 3. Implement PDF Support
- Add PDF text extraction using PyPDF2 (already in requirements)
- Process PDFs server-side to extract text
- Store extracted text instead of raw PDF

### 4. Chunked Uploads
- Split large files into smaller chunks
- Upload chunks separately
- Reassemble on server

## Immediate Fix for 5MB PDF

### Option 1: Use Text File
1. Convert your PDF to text
2. Save as .txt file
3. Upload the text file (should work if under 4.5MB)

### Option 2: Compress PDF
1. Use online PDF compression tools
2. Reduce file size to under 4.5MB
3. Upload compressed PDF

### Option 3: Split Document
1. Split your 5MB PDF into smaller sections
2. Upload each section separately
3. Process each section individually

## Next Steps

1. **Test locally** with the provided test script
2. **Check browser console** for detailed error logs
3. **Implement PDF support** if needed
4. **Consider alternative deployment** for larger files
5. **Add chunked upload** for better user experience

## Files Modified

- `frontend/app/components/FileUpload.tsx`: Enhanced error handling and logging
- `api/app.py`: Improved upload endpoint with better error handling
- `test_upload.py`: Test script for debugging upload issues
- `UPLOAD_TROUBLESHOOTING.md`: This troubleshooting guide 