
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import FileUploadStep from '@/components/FileUploadStep';
import RegistrationFormStep from '@/components/RegistrationFormStep';
import RegistrationSuccess from '@/components/RegistrationSuccess';

export type RegistrationStep = 'upload' | 'form' | 'success';

interface UploadedFile {
  file_id: string;
  filename: string;
}

const CandidatePortal = () => {
  const [currentStep, setCurrentStep] = useState<RegistrationStep>('upload');
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [registrationId, setRegistrationId] = useState<string>('');

  const handleFileUploaded = (fileData: UploadedFile) => {
    setUploadedFile(fileData);
    setCurrentStep('form');
  };

  const handleRegistrationComplete = (id: string) => {
    setRegistrationId(id);
    setCurrentStep('success');
  };

  const handleStartOver = () => {
    setCurrentStep('upload');
    setUploadedFile(null);
    setRegistrationId('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">HR</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">Simple HR System</h1>
            </div>
            <div className="flex space-x-4">
              <Link to="/status">
                <Button variant="outline" size="sm">
                  Check Application Status
                </Button>
              </Link>
              <Link to="/admin">
                <Button variant="outline" size="sm">
                  Admin Portal
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Join Our Team
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Start your career journey with us. Upload your resume and complete your application in just two simple steps.
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="flex justify-center mb-8">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 ${
              currentStep === 'upload' ? 'text-blue-600' :
              currentStep === 'form' || currentStep === 'success' ? 'text-green-600' : 'text-gray-400'
            }`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                currentStep === 'upload' ? 'bg-blue-100 text-blue-600' :
                currentStep === 'form' || currentStep === 'success' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
              }`}>
                1
              </div>
              <span className="font-medium">Upload Resume</span>
            </div>

            <div className={`h-px w-16 ${
              currentStep === 'form' || currentStep === 'success' ? 'bg-green-600' : 'bg-gray-300'
            }`} />

            <div className={`flex items-center space-x-2 ${
              currentStep === 'form' ? 'text-blue-600' :
              currentStep === 'success' ? 'text-green-600' : 'text-gray-400'
            }`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                currentStep === 'form' ? 'bg-blue-100 text-blue-600' :
                currentStep === 'success' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
              }`}>
                2
              </div>
              <span className="font-medium">Personal Details</span>
            </div>

            <div className={`h-px w-16 ${
              currentStep === 'success' ? 'bg-green-600' : 'bg-gray-300'
            }`} />

            <div className={`flex items-center space-x-2 ${
              currentStep === 'success' ? 'text-green-600' : 'text-gray-400'
            }`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                currentStep === 'success' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
              }`}>
                ✓
              </div>
              <span className="font-medium">Complete</span>
            </div>
          </div>
        </div>

        {/* Step Content */}
        <Card className="max-w-2xl mx-auto">
          {currentStep === 'upload' && (
            <>
              <CardHeader>
                <CardTitle>Step 1: Upload Your Resume</CardTitle>
                <CardDescription>
                  Please upload your resume in PDF or DOCX format (max 5MB)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileUploadStep onFileUploaded={handleFileUploaded} />
              </CardContent>
            </>
          )}

          {currentStep === 'form' && uploadedFile && (
            <>
              <CardHeader>
                <CardTitle>Step 2: Complete Your Application</CardTitle>
                <CardDescription>
                  Fill in your personal details to complete your application
                </CardDescription>
              </CardHeader>
              <CardContent>
                <RegistrationFormStep
                  uploadedFile={uploadedFile}
                  onRegistrationComplete={handleRegistrationComplete}
                  onBack={() => setCurrentStep('upload')}
                />
              </CardContent>
            </>
          )}

          {currentStep === 'success' && (
            <CardContent className="pt-6">
              <RegistrationSuccess
                registrationId={registrationId}
                onStartOver={handleStartOver}
              />
            </CardContent>
          )}
        </Card>
      </main>
    </div>
  );
};

export default CandidatePortal;
