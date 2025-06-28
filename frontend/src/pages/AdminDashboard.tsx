
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { getCandidates, downloadResume, CandidateListItem, Department, ApplicationStatus } from '@/lib/api';
import { getStatusColor, getStatusLabel, formatDate, getDepartmentIcon } from '@/lib/utils-hr';
import {
  Search,
  Filter,
  Download,
  Edit,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  ArrowLeft,
  RefreshCw,
  Loader2
} from 'lucide-react';
import StatusUpdateModal from '@/components/StatusUpdateModal';
import { toast } from '@/hooks/use-toast';

const AdminDashboard = () => {
  const [candidates, setCandidates] = useState<CandidateListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<ApplicationStatus | 'all'>('all');
  const [departmentFilter, setDepartmentFilter] = useState<Department | 'all'>('all');
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateListItem | null>(null);
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [hasPrevPage, setHasPrevPage] = useState(false);

  const loadCandidates = async (page: number = 1) => {
    setLoading(true);
    setError('');

    try {
      const params: any = { page };

      if (statusFilter !== 'all') {
        params.current_status = statusFilter;
      }

      if (departmentFilter !== 'all') {
        params.department = departmentFilter;
      }

      const response = await getCandidates(params);
      setCandidates(response.results);
      setTotalCount(response.count);
      setHasNextPage(!!response.next);
      setHasPrevPage(!!response.previous);
      setCurrentPage(page);
    } catch (error: any) {
      console.error('Failed to load candidates:', error);

      let errorMessage = 'Failed to load candidates. Please try again.';

      if (error.code === 'ERR_NETWORK') {
        errorMessage = error.message || 'Unable to connect to server. Please check if the backend is running.';
      } else if (error.response?.status === 401 || error.response?.status === 403) {
        errorMessage = 'Admin access required. Please ensure you have proper permissions.';
      } else if (error.response?.data) {
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
      }

      setError(errorMessage);

      toast({
        title: 'Failed to Load Candidates',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, [statusFilter, departmentFilter]);

  const handleStatusUpdate = () => {
    setStatusModalOpen(false);
    setSelectedCandidate(null);
    loadCandidates(currentPage);
    toast({
      title: 'Status updated successfully!',
      description: 'The candidate status has been updated.',
    });
  };

  const handleDownloadResume = async (candidate: CandidateListItem) => {
    try {
      toast({
        title: 'Download started',
        description: `Downloading resume for ${candidate.full_name}`,
      });

      const blob = await downloadResume(candidate.id);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${candidate.full_name}_Resume.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Download completed',
        description: `Resume for ${candidate.full_name} has been downloaded successfully.`,
      });
    } catch (error: any) {
      console.error('Download error:', error);

      let errorMessage = 'Failed to download resume. Please try again.';

      if (error.code === 'ERR_NETWORK') {
        errorMessage = error.message || 'Unable to connect to server.';
      } else if (error.response?.data) {
        if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
      }

      toast({
        title: 'Download failed',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  const filteredCandidates = candidates.filter(candidate => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        candidate.full_name.toLowerCase().includes(searchLower) ||
        candidate.email.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  const getStatusStats = () => {
    const stats = candidates.reduce((acc, candidate) => {
      acc[candidate.current_status] = (acc[candidate.current_status] || 0) + 1;
      return acc;
    }, {} as Record<ApplicationStatus, number>);

    return {
      total: candidates.length,
      submitted: stats.submitted || 0,
      under_review: stats.under_review || 0,
      interview_scheduled: stats.interview_scheduled || 0,
      accepted: stats.accepted || 0,
      rejected: stats.rejected || 0,
    };
  };

  const stats = getStatusStats();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">HR</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">Admin Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadCandidates(currentPage)}
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Link to="/">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Portal
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <Card>
            <CardContent className="flex items-center p-6">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center p-6">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Submitted</p>
                <p className="text-2xl font-bold text-gray-900">{stats.submitted}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center p-6">
              <Search className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Under Review</p>
                <p className="text-2xl font-bold text-gray-900">{stats.under_review}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center p-6">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Accepted</p>
                <p className="text-2xl font-bold text-gray-900">{stats.accepted}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center p-6">
              <XCircle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Rejected</p>
                <p className="text-2xl font-bold text-gray-900">{stats.rejected}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Search */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Candidate Management</CardTitle>
            <CardDescription>
              Manage and review candidate applications
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search by name or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <Select value={statusFilter} onValueChange={(value: ApplicationStatus | 'all') => setStatusFilter(value)}>
                <SelectTrigger className="w-full lg:w-[200px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="submitted">Submitted</SelectItem>
                  <SelectItem value="under_review">Under Review</SelectItem>
                  <SelectItem value="interview_scheduled">Interview Scheduled</SelectItem>
                  <SelectItem value="accepted">Accepted</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>

              <Select value={departmentFilter} onValueChange={(value: Department | 'all') => setDepartmentFilter(value)}>
                <SelectTrigger className="w-full lg:w-[200px]">
                  <SelectValue placeholder="Filter by department" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Departments</SelectItem>
                  <SelectItem value="IT">💻 IT</SelectItem>
                  <SelectItem value="HR">👥 HR</SelectItem>
                  <SelectItem value="Finance">💰 Finance</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Candidates Table */}
        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">Loading candidates...</span>
              </div>
            ) : filteredCandidates.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No candidates found</h3>
                <p className="text-gray-500">Try adjusting your search criteria or filters.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Candidate</TableHead>
                      <TableHead>Department</TableHead>
                      <TableHead>Experience</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Applied</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredCandidates.map((candidate) => (
                      <TableRow key={candidate.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium text-gray-900">{candidate.full_name}</div>
                            <div className="text-sm text-gray-500">{candidate.email}</div>
                            <div className="text-sm text-gray-500">{candidate.phone}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center space-x-2">
                            <span>{getDepartmentIcon(candidate.department)}</span>
                            <span>{candidate.department}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          {candidate.years_of_experience} years
                        </TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(candidate.current_status)}>
                            {getStatusLabel(candidate.current_status)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {formatDate(candidate.created_at)}
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setSelectedCandidate(candidate);
                                setStatusModalOpen(true);
                              }}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDownloadResume(candidate)}
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pagination */}
        {totalCount > 0 && (
          <div className="flex items-center justify-between mt-6">
            <p className="text-sm text-gray-700">
              Showing {((currentPage - 1) * 20) + 1} to {Math.min(currentPage * 20, totalCount)} of {totalCount} candidates
            </p>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadCandidates(currentPage - 1)}
                disabled={!hasPrevPage || loading}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => loadCandidates(currentPage + 1)}
                disabled={!hasNextPage || loading}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </main>

      {/* Status Update Modal */}
      {selectedCandidate && (
        <StatusUpdateModal
          candidate={selectedCandidate}
          open={statusModalOpen}
          onOpenChange={setStatusModalOpen}
          onStatusUpdated={handleStatusUpdate}
        />
      )}
    </div>
  );
};

export default AdminDashboard;
