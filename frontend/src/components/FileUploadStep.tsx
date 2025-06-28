
import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { uploadFile } from '@/lib/api';
import { validateFileType, validateFileSize, formatFileSize } from '@/lib/utils-hr';
import { Upload, File, X, CheckCircle } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface FileUploadStepProps {
  onFileUploaded: (fileData: { file_id: string; filename: string }) => void;
}

const FileUploadStep = ({ onFileUploaded }: FileUploadStepProps) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setError('');

    if (rejectedFiles.length > 0) {
      setError('Please upload a valid PDF or DOCX file (max 5MB)');
      return;
    }

    const file = acceptedFiles[0];
    if (!file) return;

    // Additional validation
    if (!validateFileType(file)) {
      setError('Invalid file type. Please upload a PDF or DOCX file.');
      return;
    }

    if (!validateFileSize(file)) {
      setError('File size too large. Please upload a file smaller than 5MB.');
      return;
    }

    setSelectedFile(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024, // 5MB
  });

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);
    setError('');

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      const response = await uploadFile(selectedFile);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        onFileUploaded({
          file_id: response.file_id,
          filename: response.filename,
        });

        toast({
          title: 'File uploaded successfully!',
          description: `${response.filename} has been uploaded.`,
        });
      }, 500);

    } catch (error: any) {
      console.error('Upload error:', error);
      setError(error.response?.data?.error || 'Failed to upload file. Please try again.');
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setError('');
    setUploadProgress(0);
  };

  if (uploading) {
    return (
      <div className="text-center py-8">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Upload className="w-8 h-8 text-blue-600 animate-bounce" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Uploading your resume...</h3>
        <div className="max-w-xs mx-auto">
          <Progress value={uploadProgress} className="mb-2" />
          <p className="text-sm text-gray-500">{uploadProgress}% uploaded</p>
        </div>
      </div>
    );
  }

  if (selectedFile) {
    return (
      <div className="space-y-4">
        <div className="border rounded-lg p-4 bg-green-50 border-green-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <File className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="font-medium text-gray-900">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRemoveFile}
              className="text-gray-400 hover:text-red-600"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="flex space-x-3">
          <Button onClick={handleRemoveFile} variant="outline" className="flex-1">
            Choose Different File
          </Button>
          <Button onClick={handleUpload} className="flex-1">
            <CheckCircle className="w-4 h-4 mr-2" />
            Upload & Continue
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
        }`}
      >
        <input {...getInputProps()} />
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Upload className="w-8 h-8 text-blue-600" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          {isDragActive ? 'Drop your resume here' : 'Upload your resume'}
        </h3>
        <p className="text-gray-500 mb-4">
          Drag and drop your file here, or click to browse
        </p>
        <p className="text-sm text-gray-400">
          Supports PDF and DOCX files up to 5MB
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default FileUploadStep;
