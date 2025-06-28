
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent } from '@/components/ui/card';
import { registerCandidate, Department, CandidateRegistrationData } from '@/lib/api';
import { getDepartmentIcon } from '@/lib/utils-hr';
import { File, ArrowLeft, Loader2 } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

// Helper function to get realistic date constraints
const getDateConstraints = () => {
  const today = new Date();
  const maxDate = new Date(today.getFullYear() - 16, today.getMonth(), today.getDate()); // Minimum 16 years old
  const minDate = new Date(today.getFullYear() - 80, today.getMonth(), today.getDate()); // Maximum 80 years old

  return {
    min: minDate.toISOString().split('T')[0],
    max: maxDate.toISOString().split('T')[0],
  };
};

const registrationSchema = z.object({
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  phone: z.string().min(10, 'Please enter a valid phone number'),
  date_of_birth: z.string().min(1, 'Date of birth is required').refine((date) => {
    const birthDate = new Date(date);
    const today = new Date();
    const age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      return age - 1 >= 16 && age - 1 <= 80;
    }
    return age >= 16 && age <= 80;
  }, 'You must be between 16 and 80 years old'),
  years_of_experience: z.number().min(0, 'Experience cannot be negative').max(50, 'Experience seems too high'),
  department: z.enum(['IT', 'HR', 'Finance'], {
    required_error: 'Please select a department',
  }),
}).refine((data) => {
  // Cross-field validation: years of experience vs age
  if (data.date_of_birth && data.years_of_experience !== undefined) {
    const birthDate = new Date(data.date_of_birth);
    const today = new Date();
    const age = today.getFullYear() - birthDate.getFullYear() -
      ((today.getMonth() < birthDate.getMonth() ||
        (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) ? 1 : 0);

    // Assuming minimum working age is 16
    const maxPossibleExperience = Math.max(0, age - 16);

    return data.years_of_experience <= maxPossibleExperience;
  }
  return true;
}, {
  message: "Years of experience cannot exceed the maximum possible based on your age (assuming you started working at 16)",
  path: ["years_of_experience"], // This will show the error on the years_of_experience field
});

type RegistrationForm = z.infer<typeof registrationSchema>;

interface FieldErrors {
  [key: string]: string[];
}

interface RegistrationFormStepProps {
  uploadedFile: { file_id: string; filename: string };
  onRegistrationComplete: (id: string) => void;
  onBack: () => void;
}

const RegistrationFormStep = ({ uploadedFile, onRegistrationComplete, onBack }: RegistrationFormStepProps) => {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>('');
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<RegistrationForm>({
    resolver: zodResolver(registrationSchema),
  });

  const selectedDepartment = watch('department');
  const watchedDateOfBirth = watch('date_of_birth');
  const dateConstraints = getDateConstraints();

  // Calculate max possible experience based on date of birth
  const getMaxExperience = () => {
    if (!watchedDateOfBirth) return 50; // Default max if no date

    const birthDate = new Date(watchedDateOfBirth);
    const today = new Date();
    const age = today.getFullYear() - birthDate.getFullYear() -
      ((today.getMonth() < birthDate.getMonth() ||
        (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) ? 1 : 0);

    // Assuming minimum working age is 16
    return Math.max(0, age - 16);
  };

  const maxExperience = getMaxExperience();

  // Helper function to get field error (backend error takes precedence over form validation error)
  const getFieldError = (fieldName: string) => {
    if (fieldErrors[fieldName] && fieldErrors[fieldName].length > 0) {
      return fieldErrors[fieldName][0]; // Show first error
    }
    return errors[fieldName as keyof typeof errors]?.message;
  };

  // Helper function to check if field has error
  const hasFieldError = (fieldName: string) => {
    return !!(fieldErrors[fieldName] && fieldErrors[fieldName].length > 0) ||
           !!(errors[fieldName as keyof typeof errors]);
  };

  const onSubmit = async (data: RegistrationForm) => {
    setSubmitting(true);
    setError('');
    setFieldErrors({});

    try {
      const registrationData: CandidateRegistrationData = {
        full_name: data.full_name,
        email: data.email,
        phone: data.phone,
        date_of_birth: data.date_of_birth,
        years_of_experience: data.years_of_experience,
        department: data.department,
        file_id: uploadedFile.file_id,
      };

      const response = await registerCandidate(registrationData);

      toast({
        title: 'Application submitted successfully!',
        description: 'You will receive an email confirmation shortly.',
      });

      // Use the actual candidate ID returned from the API
      onRegistrationComplete(response.candidate_id);

    } catch (error: any) {
      console.error('Registration error:', error);

      let errorMessage = 'Failed to submit application. Please try again.';

      if (error.code === 'ERR_NETWORK') {
        errorMessage = error.message || 'Unable to connect to server. Please check your internet connection.';
        setError(errorMessage);
      } else if (error.response?.data) {
        // Check if it's field-specific errors
        if (typeof error.response.data === 'object' && !error.response.data.error && !error.response.data.detail) {
          // This looks like field-specific errors
          const fieldErrorsData: FieldErrors = {};
          let hasFieldErrors = false;

          Object.entries(error.response.data).forEach(([field, messages]) => {
            if (Array.isArray(messages)) {
              fieldErrorsData[field] = messages;
              hasFieldErrors = true;
            }
          });

          if (hasFieldErrors) {
            setFieldErrors(fieldErrorsData);
            errorMessage = 'Please correct the errors below and try again.';
          }
        } else {
          // General error message
          if (error.response.data.error) {
            errorMessage = error.response.data.error;
          } else if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (typeof error.response.data === 'string') {
            errorMessage = error.response.data;
          }
        }

        setError(errorMessage);
      } else if (error.message) {
        errorMessage = error.message;
        setError(errorMessage);
      }

      toast({
        title: 'Registration Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Uploaded File Display */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <File className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="font-medium text-blue-900">Resume uploaded:</p>
              <p className="text-sm text-blue-700">{uploadedFile.filename}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Registration Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Full Name */}
        <div className="space-y-2">
          <Label htmlFor="full_name">Full Name *</Label>
          {hasFieldError('full_name') && (
            <div className="bg-red-50 border border-red-200 rounded-md p-2">
              <p className="text-sm text-red-600">{getFieldError('full_name')}</p>
            </div>
          )}
          <Input
            id="full_name"
            {...register('full_name')}
            placeholder="Enter your full name"
            className={hasFieldError('full_name') ? 'border-red-500' : ''}
          />
        </div>

        {/* Email */}
        <div className="space-y-2">
          <Label htmlFor="email">Email Address *</Label>
          {hasFieldError('email') && (
            <div className="bg-red-50 border border-red-200 rounded-md p-2">
              <p className="text-sm text-red-600">{getFieldError('email')}</p>
            </div>
          )}
          <Input
            id="email"
            type="email"
            {...register('email')}
            placeholder="Enter your email address"
            className={hasFieldError('email') ? 'border-red-500' : ''}
          />
        </div>

        {/* Phone */}
        <div className="space-y-2">
          <Label htmlFor="phone">Phone Number *</Label>
          {hasFieldError('phone') && (
            <div className="bg-red-50 border border-red-200 rounded-md p-2">
              <p className="text-sm text-red-600">{getFieldError('phone')}</p>
            </div>
          )}
          <Input
            id="phone"
            type="tel"
            {...register('phone')}
            placeholder="Enter your phone number"
            className={hasFieldError('phone') ? 'border-red-500' : ''}
          />
        </div>

        {/* Date of Birth */}
        <div className="space-y-2">
          <Label htmlFor="date_of_birth">Date of Birth *</Label>
          <p className="text-xs text-gray-500">You must be between 16 and 80 years old</p>
          {hasFieldError('date_of_birth') && (
            <div className="bg-red-50 border border-red-200 rounded-md p-2">
              <p className="text-sm text-red-600">{getFieldError('date_of_birth')}</p>
            </div>
          )}
          <Input
            id="date_of_birth"
            type="date"
            min={dateConstraints.min}
            max={dateConstraints.max}
            {...register('date_of_birth')}
            className={hasFieldError('date_of_birth') ? 'border-red-500' : ''}
          />
        </div>

        {/* Years of Experience */}
        <div className="space-y-2">
          <Label htmlFor="years_of_experience">Years of Experience *</Label>
          {watchedDateOfBirth && (
            <p className="text-xs text-gray-500">
              Maximum: {maxExperience} years (based on your age, assuming you started working at 16)
            </p>
          )}
          {hasFieldError('years_of_experience') && (
            <div className="bg-red-50 border border-red-200 rounded-md p-2">
              <p className="text-sm text-red-600">{getFieldError('years_of_experience')}</p>
            </div>
          )}
          <Input
            id="years_of_experience"
            type="number"
            min="0"
            max={maxExperience}
            {...register('years_of_experience', { valueAsNumber: true })}
            placeholder="Enter years of experience"
            className={hasFieldError('years_of_experience') ? 'border-red-500' : ''}
          />
        </div>

        {/* Department */}
        <div className="space-y-2">
          <Label htmlFor="department">Department *</Label>
          {hasFieldError('department') && (
            <div className="bg-red-50 border border-red-200 rounded-md p-2">
              <p className="text-sm text-red-600">{getFieldError('department')}</p>
            </div>
          )}
          <Select onValueChange={(value: Department) => setValue('department', value)}>
            <SelectTrigger className={hasFieldError('department') ? 'border-red-500' : ''}>
              <SelectValue placeholder="Select a department" />
            </SelectTrigger>
            <SelectContent>
              {(['IT', 'HR', 'Finance'] as Department[]).map((dept) => (
                <SelectItem key={dept} value={dept}>
                  <div className="flex items-center space-x-2">
                    <span>{getDepartmentIcon(dept)}</span>
                    <span>{dept}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Form Actions */}
        <div className="flex space-x-3 pt-4">
          <Button type="button" variant="outline" onClick={onBack} className="flex-1">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <Button type="submit" disabled={submitting} className="flex-1">
            {submitting ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              'Submit Application'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default RegistrationFormStep;
