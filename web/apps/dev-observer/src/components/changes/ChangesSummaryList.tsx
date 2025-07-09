import React, { useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Loader } from '../Loader';
import { ErrorAlert } from '../ErrorAlert';
import { useBoundStore } from '../../store/use-bound-store';
import { GitHubChangesSummary, ChangesSummaryStatus } from '@devplan/observer-api';
import { formatDistanceToNow } from 'date-fns';

interface ChangesSummaryListProps {
  repoId: string;
  repoName: string;
}

export const ChangesSummaryList: React.FC<ChangesSummaryListProps> = ({ repoId, repoName }) => {
  const { 
    summaries, 
    loading, 
    error, 
    fetchSummaries, 
    createSummary, 
    deleteSummary, 
    clearError 
  } = useBoundStore(state => ({
    summaries: state.summaries[repoId] || [],
    loading: state.loading[repoId] || false,
    error: state.error[repoId] || null,
    fetchSummaries: state.fetchSummaries,
    createSummary: state.createSummary,
    deleteSummary: state.deleteSummary,
    clearError: state.clearError
  }));

  const [creating, setCreating] = React.useState(false);

  const handleCreateSummary = async () => {
    try {
      setCreating(true);
      await createSummary(repoId, 7);
    } catch (err) {
      // Error is handled by the store
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteSummary = async (summaryId: string) => {
    await deleteSummary(summaryId, repoId);
  };

  useEffect(() => {
    fetchSummaries(repoId);
  }, [repoId, fetchSummaries]);

  const getStatusIndicator = (status: ChangesSummaryStatus) => {
    const getStatusColor = (status: ChangesSummaryStatus) => {
      switch (status) {
        case ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_PENDING:
          return 'bg-gray-500';
        case ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_PROCESSING:
          return 'bg-blue-500';
        case ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_COMPLETED:
          return 'bg-green-500';
        case ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_FAILED:
          return 'bg-red-500';
        default:
          return 'bg-gray-400';
      }
    };

    const getStatusText = (status: ChangesSummaryStatus) => {
      switch (status) {
        case ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_PENDING:
          return 'Pending';
        case ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_PROCESSING:
          return 'Processing';
        case ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_COMPLETED:
          return 'Completed';
        case ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_FAILED:
          return 'Failed';
        default:
          return 'Unknown';
      }
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${getStatusColor(status)}`}>
        {getStatusText(status)}
      </span>
    );
  };

  const formatDate = (date: Date) => {
    return formatDistanceToNow(date, { addSuffix: true });
  };

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Changes Summaries for {repoName}</h2>
        <Button 
          onClick={handleCreateSummary} 
          disabled={creating}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {creating ? 'Creating...' : 'Create New Summary'}
        </Button>
      </div>

      {error && <ErrorAlert err={error} />}

      {summaries.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground text-center">
              No changes summaries found. Create one to get started.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {summaries.map((summary) => (
            <Card key={summary.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">
                      Changes Summary
                    </CardTitle>
                                         <p className="text-sm text-muted-foreground">
                       Created {summary.createdAt ? formatDate(summary.createdAt) : 'Unknown'}
                     </p>
                     <p className="text-sm text-muted-foreground">
                       Period: {summary.analysisPeriodStart ? formatDate(summary.analysisPeriodStart) : 'Unknown'} - {summary.analysisPeriodEnd ? formatDate(summary.analysisPeriodEnd) : 'Unknown'}
                     </p>
                   </div>
                   <div className="flex items-center space-x-2">
                     {getStatusIndicator(summary.status)}
                     <Button
                       variant="outline"
                       size="sm"
                       onClick={() => handleDeleteSummary(summary.id)}
                       className="text-red-600 hover:text-red-700"
                     >
                       Delete
                     </Button>
                   </div>
                </div>
              </CardHeader>
              <CardContent>
                {summary.status === ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_COMPLETED && summary.content && (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold mb-2">Summary</h4>
                      <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                        {summary.content.summary}
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {summary.content.statistics?.totalCommits || 0}
                        </div>
                        <div className="text-sm text-muted-foreground">Commits</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">
                          +{summary.content.statistics?.totalAdditions || 0}
                        </div>
                        <div className="text-sm text-muted-foreground">Additions</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">
                          -{summary.content.statistics?.totalDeletions || 0}
                        </div>
                        <div className="text-sm text-muted-foreground">Deletions</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">
                          {summary.content.statistics?.totalFilesChanged || 0}
                        </div>
                        <div className="text-sm text-muted-foreground">Files Changed</div>
                      </div>
                    </div>

                    {summary.content.statistics?.languageStats && summary.content.statistics.languageStats.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Top Languages</h4>
                                                 <div className="flex flex-wrap gap-2">
                           {summary.content.statistics.languageStats.slice(0, 5).map((lang, index) => (
                             <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border">
                               {lang.language}: {lang.filesChanged} files
                             </span>
                           ))}
                         </div>
                      </div>
                    )}
                  </div>
                )}

                {summary.status === ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_FAILED && (
                  <div className="text-red-600">
                    <p className="font-semibold">Analysis failed</p>
                    {summary.errorMessage && (
                      <p className="text-sm mt-1">{summary.errorMessage}</p>
                    )}
                  </div>
                )}

                                 {summary.status === ChangesSummaryStatus.CHANGES_SUMMARY_STATUS_PROCESSING && (
                   <div className="flex items-center space-x-2">
                     <Loader />
                     <span className="text-sm text-muted-foreground">Processing changes summary...</span>
                   </div>
                 )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}; 