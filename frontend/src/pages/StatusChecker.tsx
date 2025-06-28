
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { getCandidateStatus, CandidateStatus } from '@/lib/api';
import { getStatusColor, getStatusLabel, formatDateTime } from '@/lib/utils-hr';
import { Search, ArrowLeft, Clock, Loader2 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

const statusSchema = z.object({
  candidateId: z.string().min(1, 'Please enter your application ID'),
});

type StatusForm = z.infer<typeof statusSchema>;

const StatusChecker = () => {
  const [loading, setLoading] = useState(false);
  const [candidateStatus, setCandidateStatus] = useState<CandidateStatus | null>(null);
  const [error, setError] = useState<string>('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<StatusForm>({
    resolver: zodResolver(statusSchema),
  });

  const onSubmit = async (data: StatusForm) => {
    setLoading(true);
    setError('');
    setCandidateStatus(null);

    try {
      const status = await getCandidateStatus(data.candidateId);
      setCandidateStatus(status);

      toast({
        title: 'Status retrieved successfully!',
        description: `Current status: ${getStatusLabel(status.current_status)}`,
      });
    } catch (error: any) {
      console.error('Status check error:', error);

      let errorMessage = 'Failed to retrieve status. Please try again.';

      if (error.code === 'ERR_NETWORK') {
        errorMessage = error.message || 'Unable to connect to server. Please check your internet connection.';
      } else if (error.response?.status === 404) {
        errorMessage = 'Application ID not found. Please check your ID and try again.';
      } else if (error.response?.data) {
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
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
            <Link to="/">
              <Button variant="outline" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Applications
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Check Application Status
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Enter your application ID to view the current status and history of your application.
          </p>
        </div>

        <div className="max-w-2xl mx-auto space-y-6">
          {/* Status Check Form */}
          <Card>
            <CardHeader>
              <CardTitle>Application Status Lookup</CardTitle>
              <CardDescription>
                Enter the application ID you received after submitting your application
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="candidateId">Application ID</Label>
                  <Input
                    id="candidateId"
                    {...register('candidateId')}
                    placeholder="Enter your application ID"
                    className={errors.candidateId ? 'border-red-500' : ''}
                  />
                  {errors.candidateId && (
                    <p className="text-sm text-red-600">{errors.candidateId.message}</p>
                  )}
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Button type="submit" disabled={loading} className="w-full">
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Checking Status...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4 mr-2" />
                      Check Status
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Status Results */}
          {candidateStatus && (
            <div className="space-y-6">
              {/* Current Status */}
              <Card>
                <CardHeader>
                  <CardTitle>Current Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {candidateStatus.full_name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          Application ID: {candidateStatus.id}
                        </p>
                      </div>
                      <Badge className={getStatusColor(candidateStatus.current_status)}>
                        {getStatusLabel(candidateStatus.current_status)}
                      </Badge>
                    </div>

                    <div className="text-sm text-gray-600">
                      <p>Applied on: {formatDateTime(candidateStatus.created_at)}</p>
                      <p>Last updated: {formatDateTime(candidateStatus.updated_at)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Status History */}
              <Card>
                <CardHeader>
                  <CardTitle>Status History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {candidateStatus.status_history.map((history, index) => (
                      <div key={index} className="flex items-start space-x-4 pb-4 border-b last:border-b-0">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                          <Clock className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <Badge className={getStatusColor(history.status)} variant="secondary">
                              {getStatusLabel(history.status)}
                            </Badge>
                            <span className="text-sm text-gray-500">
                              {formatDateTime(history.changed_at)}
                            </span>
                          </div>
                          {history.feedback && (
                            <p className="text-sm text-gray-600 mt-1">{history.feedback}</p>
                          )}
                          {history.admin_info && (
                            <p className="text-xs text-gray-500 mt-1">
                              Updated by: {history.admin_info}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default StatusChecker;
