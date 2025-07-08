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
    // Add OpenAI API key from localStorage if available
    const apiKey = localStorage.getItem('openai_api_key');
    if (apiKey) {
      formData.append('openai_api_key', apiKey);
    }

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
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/csv': ['.csv'],
      'application/csv': ['.csv'],
    },
    maxFiles: 1,
    multiple: false
  });

  return (
    <div className="w-full max-w-2xl mx-auto p-4">
      <div
        {...getRootProps()}
        className={[
          'bloomberg-upload',
          isDragActive ? 'drag-active' : '',
          isUploading ? 'opacity-50 cursor-wait' : 'cursor-pointer',
          error ? 'error' : '',
        ].join(' ')}
      >
        <input {...getInputProps()} />
        <div className="text-center">
          {isUploading ? (
            <div className="flex flex-col items-center space-y-2">
              <div className="w-8 h-8 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin" />
              <p className="text-yellow-400">Uploading...</p>
              {uploadProgress > 0 && (
                <p className="text-sm text-yellow-300">{uploadProgress}%</p>
              )}
            </div>
          ) : isDragActive ? (
            <p className="text-green-400 font-medium">Drop your file here</p>
          ) : (
            <div className="space-y-2">
              <p className="text-yellow-300">
                Drag and drop your file here, or click to select
              </p>
              <p className="text-sm text-yellow-400">
                Supported formats: TXT, PDF, DOC, DOCX, CSV (Max 4.5MB for Vercel)
              </p>
            </div>
          )}
        </div>
      </div>
      {error && (
        <div className="mt-4 p-4 bg-red-900 border border-red-400 text-red-400 rounded-lg text-sm font-mono">
          <p className="font-medium">Error uploading file:</p>
          <p>{error}</p>
          <p className="mt-2 text-xs text-red-400">
            Check the browser console for detailed error information.
          </p>
        </div>
      )}
    </div>
  );
} 