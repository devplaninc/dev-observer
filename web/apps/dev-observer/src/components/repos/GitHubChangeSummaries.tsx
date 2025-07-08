import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Calendar, GitCommit, Users, FileText, TrendingUp, TrendingDown } from 'lucide-react';
import { useRepositoryQueries } from '@/hooks/useRepositoryQueries';
import { GitHubChangeSummary } from '@devplan/api';

interface GitHubChangeSummariesProps {
  repoId: string;
  repoName: string;
}

interface ChangeAnalysis {
  files_changed: string[];
  commits: string[];
  analysis_summary: string;
  key_changes: string[];
  authors: string[];
  total_additions: number;
  total_deletions: number;
}

export const GitHubChangeSummaries: React.FC<GitHubChangeSummariesProps> = ({ repoId, repoName }) => {
  const [selectedAnalysisType, setSelectedAnalysisType] = useState<string>('weekly');
  const [summaries, setSummaries] = useState<GitHubChangeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const pageSize = 10;

  const { repositoriesClient } = useRepositoryQueries();

  useEffect(() => {
    fetchChangeSummaries();
  }, [repoId, selectedAnalysisType, currentPage]);

  const fetchChangeSummaries = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await repositoriesClient.listChangeSummaries(repoId, {
        analysisType: selectedAnalysisType,
        limit: pageSize,
        offset: currentPage * pageSize
      });
      
      setSummaries(response.summaries || []);
      setTotalCount(response.totalCount || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch change summaries');
      console.error('Error fetching change summaries:', err);
    } finally {
      setLoading(false);
    }
  };

  const parseChangesData = (changesData: string): ChangeAnalysis | null => {
    try {
      return JSON.parse(changesData) as ChangeAnalysis;
    } catch {
      return null;
    }
  };

  const formatDate = (timestamp: any): string => {
    if (!timestamp) return 'Unknown';
    
    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getAnalysisTypeColor = (type: string): string => {
    switch (type) {
      case 'daily': return 'bg-green-100 text-green-800';
      case 'weekly': return 'bg-blue-100 text-blue-800';
      case 'monthly': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const totalPages = Math.ceil(totalCount / pageSize);

  if (loading && summaries.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Recent Changes</h3>
          <Skeleton className="h-8 w-24" />
        </div>
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Alert>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Recent Changes - {repoName}</h3>
        <div className="flex gap-2">
          {['daily', 'weekly', 'monthly'].map((type) => (
            <Button
              key={type}
              variant={selectedAnalysisType === type ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                setSelectedAnalysisType(type);
                setCurrentPage(0);
              }}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {summaries.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-gray-500">No change summaries found for this repository.</p>
            <p className="text-sm text-gray-400 mt-1">
              Change summaries are generated automatically when changes are detected.
            </p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid gap-4">
            {summaries.map((summary) => {
              const analysis = parseChangesData(summary.changesData || '{}');
              
              return (
                <Card key={summary.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <CardTitle className="text-lg">
                          {formatDate(summary.analysisPeriodStart)} - {formatDate(summary.analysisPeriodEnd)}
                        </CardTitle>
                        <Badge className={getAnalysisTypeColor(summary.analysisType || 'unknown')}>
                          {summary.analysisType || 'unknown'}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Calendar className="h-4 w-4" />
                        {formatDate(summary.createdAt)}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="prose max-w-none">
                        <p className="text-gray-700 leading-relaxed">{summary.summary}</p>
                      </div>
                      
                      {analysis && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <GitCommit className="h-4 w-4 text-gray-500" />
                              <span className="text-sm font-medium">
                                {analysis.commits?.length || 0} commits
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Users className="h-4 w-4 text-gray-500" />
                              <span className="text-sm font-medium">
                                {analysis.authors?.length || 0} contributors
                              </span>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <div className="flex items-center gap-2">
                              <TrendingUp className="h-4 w-4 text-green-500" />
                              <span className="text-sm font-medium text-green-600">
                                +{analysis.total_additions || 0} additions
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <TrendingDown className="h-4 w-4 text-red-500" />
                              <span className="text-sm font-medium text-red-600">
                                -{analysis.total_deletions || 0} deletions
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {analysis?.key_changes && analysis.key_changes.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium mb-2">Key Changes:</h4>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {analysis.key_changes.slice(0, 3).map((change, index) => (
                              <li key={index} className="flex items-start gap-2">
                                <span className="text-gray-400">•</span>
                                <span>{change}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                disabled={currentPage === 0}
              >
                Previous
              </Button>
              
              <span className="text-sm text-gray-500">
                Page {currentPage + 1} of {totalPages}
              </span>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                disabled={currentPage === totalPages - 1}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};