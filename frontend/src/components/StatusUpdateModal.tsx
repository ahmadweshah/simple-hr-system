
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { updateCandidateStatus, CandidateListItem, ApplicationStatus } from '@/lib/api';
import { getStatusColor, getStatusLabel } from '@/lib/utils-hr';
import { Loader2, Save } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

const statusUpdateSchema = z.object({
  status: z.enum(['submitted', 'under_review', 'interview_scheduled', 'rejected', 'accepted']),
  feedback: z.string().max(1000, 'Feedback must be less than 1000 characters').optional(),
});

type StatusUpdateForm = z.infer<typeof statusUpdateSchema>;

interface StatusUpdateModalProps {
  candidate: CandidateListItem;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onStatusUpdated: () => void;
}

const StatusUpdateModal = ({ candidate, open, onOpenChange, onStatusUpdated }: StatusUpdateModalProps) => {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>('');

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<StatusUpdateForm>({
    resolver: zodResolver(statusUpdateSchema),
    defaultValues: {
      status: candidate.current_status,
      feedback: '',
    },
  });

  const selectedStatus = watch('status');

  const onSubmit = async (data: StatusUpdateForm) => {
    setSubmitting(true);
    setError('');

    try {
      await updateCandidateStatus(candidate.id, {
        status: data.status,
        feedback: data.feedback || undefined,
      });

      toast({
        title: 'Status updated successfully!',
        description: `${candidate.full_name}'s status has been updated to ${getStatusLabel(data.status)}.`,
      });

      onStatusUpdated();
      reset();
    } catch (error: any) {
      console.error('Status update error:', error);

      let errorMessage = 'Failed to update status. Please try again.';

      if (error.code === 'ERR_NETWORK') {
        errorMessage = error.message || 'Unable to connect to server. Please check your internet connection.';
      } else if (error.response?.data) {
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
      }

      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      onOpenChange(false);
      reset();
      setError('');
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Update Application Status</DialogTitle>
          <DialogDescription>
            Update the status for {candidate.full_name}'s application
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Candidate Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-medium text-gray-900">{candidate.full_name}</h3>
              <Badge className={getStatusColor(candidate.current_status)}>
                {getStatusLabel(candidate.current_status)}
              </Badge>
            </div>
            <div className="text-sm text-gray-600 space-y-1">
              <p>Email: {candidate.email}</p>
              <p>Department: {candidate.department}</p>
              <p>Experience: {candidate.years_of_experience} years</p>
            </div>
          </div>

          {/* Update Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Status Selection */}
            <div className="space-y-2">
              <Label htmlFor="status">New Status *</Label>
              <Select
                value={selectedStatus}
                onValueChange={(value: ApplicationStatus) => setValue('status', value)}
              >
                <SelectTrigger className={errors.status ? 'border-red-500' : ''}>
                  <SelectValue placeholder="Select new status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="submitted">
                    <Badge className={getStatusColor('submitted')} variant="secondary">
                      {getStatusLabel('submitted')}
                    </Badge>
                  </SelectItem>
                  <SelectItem value="under_review">
                    <Badge className={getStatusColor('under_review')} variant="secondary">
                      {getStatusLabel('under_review')}
                    </Badge>
                  </SelectItem>
                  <SelectItem value="interview_scheduled">
                    <Badge className={getStatusColor('interview_scheduled')} variant="secondary">
                      {getStatusLabel('interview_scheduled')}
                    </Badge>
                  </SelectItem>
                  <SelectItem value="accepted">
                    <Badge className={getStatusColor('accepted')} variant="secondary">
                      {getStatusLabel('accepted')}
                    </Badge>
                  </SelectItem>
                  <SelectItem value="rejected">
                    <Badge className={getStatusColor('rejected')} variant="secondary">
                      {getStatusLabel('rejected')}
                    </Badge>
                  </SelectItem>
                </SelectContent>
              </Select>
              {errors.status && (
                <p className="text-sm text-red-600">{errors.status.message}</p>
              )}
            </div>

            {/* Feedback */}
            <div className="space-y-2">
              <Label htmlFor="feedback">Feedback (Optional)</Label>
              <Textarea
                id="feedback"
                {...register('feedback')}
                placeholder="Add any feedback or notes for the candidate..."
                rows={4}
                className={errors.feedback ? 'border-red-500' : ''}
              />
              {errors.feedback && (
                <p className="text-sm text-red-600">{errors.feedback.message}</p>
              )}
              <p className="text-xs text-gray-500">
                This feedback will be visible to the candidate when they check their status.
              </p>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Actions */}
            <div className="flex space-x-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={submitting}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button type="submit" disabled={submitting} className="flex-1">
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Updating...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Update Status
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default StatusUpdateModal;
