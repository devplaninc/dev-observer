import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Loader} from "@/components/Loader.tsx";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";

interface ChangeSummary {
  jobId: string;
  repoId: string;
  repoName: string;
  status: string;
  observationKey?: string;
  errorMessage?: string;
  analyzedAt?: string;
  summaryContent?: string;
}

interface ChangeSummaryTimelineProps {
  summaries?: ChangeSummary[];
  error?: Error;
  isLoading?: boolean;
}

export function ChangeSummaryTimeline({summaries, error, isLoading}: ChangeSummaryTimelineProps) {
  if (isLoading) {
    return <Loader />;
  }

  if (error) {
    return <ErrorAlert err={error} />;
  }

  if (!summaries || summaries.length === 0) {
    return (
      <div className="bg-muted p-8 rounded-lg text-center">
        <h3 className="text-xl font-medium mb-2">No change summaries found</h3>
        <p className="text-muted-foreground">
          Change summaries will appear here once repositories are enrolled and analyzed.
        </p>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Completed</span>;
      case "pending":
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Pending</span>;
      case "failed":
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Failed</span>;
      default:
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{status}</span>;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Change Summaries</h2>
      <div className="space-y-4">
        {summaries.map((summary) => (
          <Card key={summary.jobId}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{summary.repoName}</CardTitle>
                {getStatusBadge(summary.status)}
              </div>
              <p className="text-sm text-muted-foreground">
                Analyzed on {formatDate(summary.analyzedAt)}
              </p>
            </CardHeader>
            <CardContent>
              {summary.status === "completed" && summary.summaryContent && (
                <div className="prose prose-sm max-w-none">
                  <p>{summary.summaryContent}</p>
                </div>
              )}
              {summary.status === "failed" && summary.errorMessage && (
                <div className="bg-destructive/10 border border-destructive/20 rounded p-3">
                  <p className="text-destructive text-sm">
                    <strong>Error:</strong> {summary.errorMessage}
                  </p>
                </div>
              )}
              {summary.status === "pending" && (
                <div className="bg-muted rounded p-3">
                  <p className="text-muted-foreground text-sm">
                    Analysis is pending. Check back later for results.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
} 