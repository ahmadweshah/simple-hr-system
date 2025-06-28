
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle, Copy, RefreshCw } from 'lucide-react';
import { toast } from '@/hooks/use-toast';
import { Link } from 'react-router-dom';

interface RegistrationSuccessProps {
  registrationId: string;
  onStartOver: () => void;
}

const RegistrationSuccess = ({ registrationId, onStartOver }: RegistrationSuccessProps) => {
  const copyToClipboard = () => {
    navigator.clipboard.writeText(registrationId);
    toast({
      title: 'Copied to clipboard!',
      description: 'Application ID has been copied to your clipboard.',
    });
  };

  return (
    <div className="text-center space-y-6">
      <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
        <CheckCircle className="w-12 h-12 text-green-600" />
      </div>

      <div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          Application Submitted Successfully!
        </h3>
        <p className="text-gray-600">
          Thank you for applying. We have received your application and will review it shortly.
        </p>
      </div>

      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-4">
          <div className="space-y-3">
            <p className="text-sm font-medium text-blue-900">
              Your Application ID:
            </p>
            <div className="flex items-center space-x-2">
              <code className="flex-1 bg-white px-3 py-2 rounded border text-sm font-mono">
                {registrationId}
              </code>
              <Button size="sm" variant="outline" onClick={copyToClipboard}>
                <Copy className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-blue-700">
              Save this ID to check your application status later
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">What's Next?</h4>
        <div className="grid gap-3 text-sm text-gray-600">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs font-semibold text-blue-600 mt-0.5">
              1
            </div>
            <p>We'll review your application and resume within 2-3 business days</p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs font-semibold text-blue-600 mt-0.5">
              2
            </div>
            <p>You'll receive an email notification about your application status</p>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs font-semibold text-blue-600 mt-0.5">
              3
            </div>
            <p>If selected, we'll contact you to schedule an interview</p>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <Link to="/status" className="flex-1">
          <Button variant="outline" className="w-full">
            Check Application Status
          </Button>
        </Link>
        <Button onClick={onStartOver} variant="outline" className="flex-1">
          <RefreshCw className="w-4 h-4 mr-2" />
          Submit Another Application
        </Button>
      </div>
    </div>
  );
};

export default RegistrationSuccess;
