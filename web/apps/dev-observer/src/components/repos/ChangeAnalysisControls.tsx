import React, {useCallback, useState} from "react";
import {Button} from "@/components/ui/button.tsx";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Badge} from "@/components/ui/badge.tsx";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {toast} from "sonner";
import {Loader} from "@/components/Loader.tsx";
import {GitHubRepository} from "@devplan/observer-api";

interface ChangeAnalysisControlsProps {
  repository: GitHubRepository;
}

export const ChangeAnalysisControls: React.FC<ChangeAnalysisControlsProps> = ({repository}) => {
  const {enrollForChangeAnalysis, unenrollFromChangeAnalysis} = useBoundStore();
  const [enrolling, setEnrolling] = useState(false);
  const [unenrolling, setUnenrolling] = useState(false);

  const isEnrolled = repository.properties?.changeAnalysis?.enrolled || false;
  const enrolledAt = repository.properties?.changeAnalysis?.enrolledAt;

  const handleEnroll = useCallback(async () => {
    setEnrolling(true);
    try {
      await enrollForChangeAnalysis(repository.id);
      toast.success("Repository enrolled for daily change analysis");
    } catch (error) {
      toast.error(`Failed to enroll repository: ${error}`);
    } finally {
      setEnrolling(false);
    }
  }, [enrollForChangeAnalysis, repository.id]);

  const handleUnenroll = useCallback(async () => {
    setUnenrolling(true);
    try {
      await unenrollFromChangeAnalysis(repository.id);
      toast.success("Repository unenrolled from daily change analysis");
    } catch (error) {
      toast.error(`Failed to unenroll repository: ${error}`);
    } finally {
      setUnenrolling(false);
    }
  }, [unenrollFromChangeAnalysis, repository.id]);

  const formatDate = (timestamp: any) => {
    if (!timestamp) return 'Never';
    try {
      // Handle protobuf timestamp format
      const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch {
      return 'Invalid date';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Daily Change Analysis
          {isEnrolled ? (
            <Badge variant="default">Enrolled</Badge>
          ) : (
            <Badge variant="secondary">Not Enrolled</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Enable daily AI-powered summaries of repository changes including merged pull requests and commits.
          </p>
          
          {isEnrolled && enrolledAt && (
            <div className="text-sm">
              <span className="font-medium">Enrolled since:</span> {formatDate(enrolledAt)}
            </div>
          )}

          <div className="flex gap-2">
            {isEnrolled ? (
              <Button 
                variant="outline" 
                onClick={handleUnenroll} 
                disabled={unenrolling}
              >
                {unenrolling && <Loader />}
                Unenroll
              </Button>
            ) : (
              <Button 
                onClick={handleEnroll} 
                disabled={enrolling}
              >
                {enrolling && <Loader />}
                Enroll for Change Analysis
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};