'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface FileUploadProps {
  onFileProcessed: (success: boolean, documentId?: string) => void;
}

export default function FileUpload({ onFileProcessed }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Enhanced logging for debugging
    console.log('File upload started:', {
      name: file.name,
      size: file.size,
      type: file.type,
      sizeInMB: (file.size / (1024 * 1024)).toFixed(2)
    });

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      const errorMsg = 'File size must be less than 10MB';
      console.error('File size validation failed:', errorMsg);
      setError(errorMsg);
      return;
    }

    // Check for Vercel's 4.5MB limit
    if (file.size > 4.5 * 1024 * 1024) {
      const warningMsg = 'Warning: File size exceeds Vercel\'s 4.5MB limit. Upload may fail.';
      console.warn(warningMsg);
      setError(warningMsg);
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Sending upload request to /api/upload');
      
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      console.log('Upload response received:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch (parseError) {
          console.error('Failed to parse error response:', parseError);
          errorData = { detail: 'Upload failed' };
        }
        
        const errorMessage = errorData.detail || `Upload failed with status ${response.status}`;
        console.error('Upload failed:', {
          status: response.status,
          statusText: response.statusText,
          error: errorMessage,
          errorData
        });
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log('Upload successful:', data);
      onFileProcessed(true, data.document_id);
    } catch (err) {
      console.error('Upload error:', {
        error: err,
        message: err instanceof Error ? err.message : 'Unknown error',
        stack: err instanceof Error ? err.stack : undefined
      });
      
      let errorMessage = 'Failed to upload file. Please try again.';
      
      if (err instanceof Error) {
        if (err.message.includes('413')) {
          errorMessage = 'File too large. Please use a smaller file (under 4.5MB for Vercel).';
        } else if (err.message.includes('413')) {
          errorMessage = 'File too large. Please use a smaller file.';
        } else if (err.message.includes('timeout') || err.message.includes('fetch')) {
          errorMessage = 'Upload timed out. This may be due to file size or network issues.';
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
      onFileProcessed(false);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [onFileProcessed]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    multiple: false
  });

  return (
    <div className="w-full max-w-2xl mx-auto p-4">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-8
          transition-all duration-200 ease-in-out
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-slate-300 hover:border-slate-400'
          }
          ${isUploading ? 'opacity-50 cursor-wait' : 'cursor-pointer'}
          ${error ? 'border-red-300 bg-red-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        <div className="text-center">
          {isUploading ? (
            <div className="flex flex-col items-center space-y-2">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-slate-600">Uploading...</p>
              {uploadProgress > 0 && (
                <p className="text-sm text-slate-500">{uploadProgress}%</p>
              )}
            </div>
          ) : isDragActive ? (
            <p className="text-blue-600 font-medium">Drop your file here</p>
          ) : (
            <div className="space-y-2">
              <p className="text-slate-600">
                Drag and drop your file here, or click to select
              </p>
              <p className="text-sm text-slate-500">
                Supported formats: TXT, PDF, DOC, DOCX (Max 4.5MB for Vercel)
              </p>
            </div>
          )}
        </div>
      </div>
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          <p className="font-medium">Error uploading file:</p>
          <p>{error}</p>
          <p className="mt-2 text-xs text-red-600">
            Check the browser console for detailed error information.
          </p>
        </div>
      )}
    </div>
  );
} 