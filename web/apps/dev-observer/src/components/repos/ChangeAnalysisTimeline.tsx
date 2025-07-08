import React, {useEffect, useState} from "react";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Badge} from "@/components/ui/badge.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select.tsx";
import {Input} from "@/components/ui/input.tsx";
import {Label} from "@/components/ui/label.tsx";
import {Alert, AlertDescription} from "@/components/ui/alert.tsx";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {GitHubRepository, RepoChangeAnalysis} from "@devplan/observer-api";
import {Loader} from "@/components/Loader.tsx";
import {Markdown} from "@/components/text/Markdown.tsx";

interface ChangeAnalysisTimelineProps {
  repository: GitHubRepository;
}

export const ChangeAnalysisTimeline: React.FC<ChangeAnalysisTimelineProps> = ({repository}) => {
  const {changeAnalyses, fetchChangeAnalyses} = useBoundStore();
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [dateFromFilter, setDateFromFilter] = useState<string>("");
  const [dateToFilter, setDateToFilter] = useState<string>("");
  const [expandedAnalysis, setExpandedAnalysis] = useState<string | null>(null);

  const analyses = changeAnalyses[repository.id] || [];

  const loadAnalyses = async () => {
    setLoading(true);
    try {
      const status = statusFilter === "all" ? undefined : statusFilter;
      await fetchChangeAnalyses(repository.id, dateFromFilter || undefined, dateToFilter || undefined, status);
    } catch (error) {
      console.error("Failed to load change analyses:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalyses();
  }, [repository.id]);

  const formatDate = (timestamp: any) => {
    if (!timestamp) return 'Not analyzed';
    try {
      const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return 'Invalid date';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default">Completed</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const toggleExpanded = (analysisId: string) => {
    setExpandedAnalysis(expandedAnalysis === analysisId ? null : analysisId);
  };

  if (!repository.properties?.changeAnalysis?.enrolled) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Change Analysis Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>
              This repository is not enrolled for change analysis. Enable it above to see AI-powered summaries of daily changes.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change Analysis Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="status-filter">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex-1">
              <Label htmlFor="date-from">From Date</Label>
              <Input
                type="date"
                value={dateFromFilter}
                onChange={(e) => setDateFromFilter(e.target.value)}
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="date-to">To Date</Label>
              <Input
                type="date"
                value={dateToFilter}
                onChange={(e) => setDateToFilter(e.target.value)}
              />
            </div>
            <Button onClick={loadAnalyses} disabled={loading}>
              {loading && <Loader />}
              Filter
            </Button>
          </div>

          {/* Timeline */}
          <div className="space-y-4">
            {loading && analyses.length === 0 ? (
              <div className="flex justify-center items-center py-8">
                <Loader />
                <span className="ml-2">Loading analyses...</span>
              </div>
            ) : analyses.length === 0 ? (
              <Alert>
                <AlertDescription>
                  No change analyses found for this repository. Analyses are generated daily for enrolled repositories.
                </AlertDescription>
              </Alert>
            ) : (
              analyses.map((analysis) => (
                <AnalysisCard
                  key={analysis.id}
                  analysis={analysis}
                  repository={repository}
                  expanded={expandedAnalysis === analysis.id}
                  onToggleExpanded={() => toggleExpanded(analysis.id)}
                />
              ))
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

interface AnalysisCardProps {
  analysis: RepoChangeAnalysis;
  repository: GitHubRepository;
  expanded: boolean;
  onToggleExpanded: () => void;
}

const AnalysisCard: React.FC<AnalysisCardProps> = ({analysis, repository, expanded, onToggleExpanded}) => {
  const [summary, setSummary] = useState<string | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  const formatDate = (timestamp: any) => {
    if (!timestamp) return 'Not analyzed';
    try {
      const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return 'Invalid date';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default">Completed</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const loadSummary = async () => {
    if (!analysis.observationKey || loadingSummary || summary) return;

    setLoadingSummary(true);
    try {
      // TODO: Load the actual observation content via observations API
      // For now, show a placeholder
      setSummary("Summary content would be loaded here from the observations API using the observation key: " + analysis.observationKey);
    } catch (error) {
      console.error("Failed to load summary:", error);
      setSummary("Failed to load summary content");
    } finally {
      setLoadingSummary(false);
    }
  };

  useEffect(() => {
    if (expanded && analysis.observationKey) {
      loadSummary();
    }
  }, [expanded, analysis.observationKey]);

  return (
    <Card className="border-l-4 border-l-blue-200">
      <CardContent className="pt-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              {getStatusBadge(analysis.status)}
              <span className="text-sm text-muted-foreground">
                {formatDate(analysis.analyzedAt || analysis.createdAt)}
              </span>
            </div>
            
            {analysis.status === 'failed' && analysis.errorMessage && (
              <Alert variant="destructive">
                <AlertDescription>{analysis.errorMessage}</AlertDescription>
              </Alert>
            )}
          </div>
          
          {analysis.observationKey && (
            <Button variant="ghost" size="sm" onClick={onToggleExpanded}>
              {expanded ? "Hide Summary" : "Show Summary"}
            </Button>
          )}
        </div>

        {expanded && analysis.observationKey && (
          <div className="mt-4 pt-4 border-t">
            {loadingSummary ? (
              <div className="flex items-center gap-2">
                <Loader />
                <span>Loading summary...</span>
              </div>
            ) : summary ? (
              <div className="prose max-w-none">
                <Markdown content={summary} />
              </div>
            ) : (
              <p className="text-muted-foreground">No summary available</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};