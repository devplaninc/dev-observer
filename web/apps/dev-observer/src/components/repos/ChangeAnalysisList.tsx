import React, {useCallback, useEffect, useState} from "react";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Input} from "@/components/ui/input.tsx";
import {DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger} from "@/components/ui/dropdown-menu.tsx";
import {Accordion, AccordionContent, AccordionItem, AccordionTrigger} from "@/components/ui/accordion.tsx";
import {Markdown} from "@/components/text/Markdown.tsx";
import {Loader} from "@/components/Loader.tsx";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {toast} from "sonner";
import type {GitHubRepository, ChangeSummary} from "@devplan/observer-api";

interface ChangeAnalysisListProps {
  repo: GitHubRepository;
}

export function ChangeAnalysisList({repo}: ChangeAnalysisListProps) {
  const {fetchChangeSummaries, changeSummaries} = useBoundStore();
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const summaries = changeSummaries[repo.id] || [];

  const fetchSummaries = useCallback(async () => {
    setLoading(true);
    try {
      await fetchChangeSummaries(
        repo.id,
        statusFilter || undefined,
        startDate || undefined,
        endDate || undefined
      );
    } catch (e) {
      toast.error(`Failed to fetch change summaries: ${e}`);
    } finally {
      setLoading(false);
    }
  }, [repo.id, statusFilter, startDate, endDate, fetchChangeSummaries]);

  const handleFilterChange = useCallback(() => {
    fetchSummaries();
  }, [fetchSummaries]);

  const clearFilters = useCallback(() => {
    setStatusFilter('');
    setStartDate('');
    setEndDate('');
  }, []);

  useEffect(() => {
    fetchSummaries();
  }, [repo.id, fetchChangeSummaries]);

  const formatDate = (timestamp: any) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp.seconds * 1000);
    return date.toLocaleString();
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      completed: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800'
    };

    return (
      <span className={`px-2 py-1 rounded text-sm ${statusColors[status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Change Analysis History</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Filters */}
        <div className="mb-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="w-full justify-start">
                  {statusFilter ? 
                    statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1) : 
                    "Filter by status"
                  }
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem onClick={() => setStatusFilter("")}>
                  All statuses
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter("completed")}>
                  Completed
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter("pending")}>
                  Pending
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setStatusFilter("failed")}>
                  Failed
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Input
              type="date"
              placeholder="Start date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />

            <Input
              type="date"
              placeholder="End date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />

            <div className="flex gap-2">
              <Button onClick={handleFilterChange} disabled={loading}>
                {loading && <Loader />}
                Apply Filters
              </Button>
              <Button variant="outline" onClick={clearFilters}>
                Clear
              </Button>
            </div>
          </div>
        </div>

        {/* Summaries List */}
        {loading && summaries.length === 0 ? (
          <div className="flex justify-center items-center py-12">
            <Loader />
          </div>
        ) : summaries.length === 0 ? (
          <div className="bg-muted p-8 rounded-lg text-center">
            <h3 className="text-xl font-medium mb-2">No change summaries available</h3>
            <p className="text-muted-foreground mb-4">
              {repo.properties?.changeAnalysis?.enrolled 
                ? "Change summaries will appear here once analysis jobs are completed."
                : "Enroll this repository for change analysis to see summaries here."
              }
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <Accordion type="multiple" className="w-full">
              {summaries.map((summary) => (
                <AccordionItem value={summary.id} key={summary.id}>
                  <AccordionTrigger className="text-left">
                    <div className="flex items-center justify-between w-full mr-4">
                      <div className="flex items-center gap-3">
                        <span className="font-medium">
                          Analysis {formatDate(summary.analyzedAt)}
                        </span>
                        {getStatusBadge(summary.status)}
                      </div>
                      <span className="text-sm text-muted-foreground">
                        Created: {formatDate(summary.createdAt)}
                      </span>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="pl-4">
                    <SummaryContent summary={summary} />
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function SummaryContent({summary}: {summary: ChangeSummary}) {
  if (summary.status === 'failed') {
    return (
      <ErrorAlert err={new Error(summary.errorMessage || 'Analysis failed')} />
    );
  }

  if (summary.status === 'pending') {
    return (
      <div className="flex items-center gap-2 text-muted-foreground">
        <Loader />
        <span>Analysis in progress...</span>
      </div>
    );
  }

  if (summary.observation?.content) {
    return <Markdown content={summary.observation.content} />;
  }

  return (
    <div className="text-muted-foreground">
      <p>Summary content not available.</p>
    </div>
  );
}
