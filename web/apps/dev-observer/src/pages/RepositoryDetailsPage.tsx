import React, {type ReactNode, useCallback, useState, useEffect} from "react";
import {useNavigate, useParams} from "react-router";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import {Alert, AlertDescription, AlertTitle} from "@/components/ui/alert.tsx";
import {useRepositoryQuery} from "@/hooks/useRepositoryQueries.ts";
import {useBoundStore} from "@/store/use-bound-store.tsx";
import {toast} from "sonner";
import {Loader} from "@/components/Loader.tsx";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger
} from "@/components/ui/alert-dialog.tsx";
import {RepoAnalysisList} from "@/components/repos/RepoAnalysisList.tsx";
import {ChangeAnalysisList} from "@/components/repos/ChangeAnalysisList.tsx";
import type {GetRepositoryEnrollmentStatusResponse} from "@devplan/observer-api";

const RepositoryDetailsPage: React.FC = () => {
  const {id} = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {repository, loading, error} = useRepositoryQuery(id ?? '');
  const errorMessage = error instanceof Error ? error.message : 'An error occurred';
  const {rescanRepository, enrollRepositoryForChangeAnalysis, unenrollRepositoryFromChangeAnalysis, getRepositoryEnrollmentStatus} = useBoundStore()
  const [enrollmentStatus, setEnrollmentStatus] = useState<GetRepositoryEnrollmentStatusResponse | null>(null);
  const [enrollmentLoading, setEnrollmentLoading] = useState(false);

  const rescan = useCallback(() => {
    rescanRepository(id!)
      .then(() => toast.success(`Rescan started`))
      .catch(e => toast.error(`Failed to initialize rescan: ${e}`))
  }, [id, rescanRepository])

  const fetchEnrollmentStatus = useCallback(async () => {
    if (!id) return;
    try {
      const status = await getRepositoryEnrollmentStatus(id);
      setEnrollmentStatus(status);
    } catch (e) {
      console.error('Failed to fetch enrollment status:', e);
    }
  }, [id, getRepositoryEnrollmentStatus]);

  const handleEnroll = useCallback(async () => {
    if (!id) return;
    setEnrollmentLoading(true);
    try {
      await enrollRepositoryForChangeAnalysis(id);
      await fetchEnrollmentStatus();
      toast.success('Repository enrolled for change analysis');
    } catch (e) {
      toast.error(`Failed to enroll repository: ${e}`);
    } finally {
      setEnrollmentLoading(false);
    }
  }, [id, enrollRepositoryForChangeAnalysis, fetchEnrollmentStatus]);

  const handleUnenroll = useCallback(async () => {
    if (!id) return;
    setEnrollmentLoading(true);
    try {
      await unenrollRepositoryFromChangeAnalysis(id);
      await fetchEnrollmentStatus();
      toast.success('Repository unenrolled from change analysis');
    } catch (e) {
      toast.error(`Failed to unenroll repository: ${e}`);
    } finally {
      setEnrollmentLoading(false);
    }
  }, [id, unenrollRepositoryFromChangeAnalysis, fetchEnrollmentStatus]);

  useEffect(() => {
    if (id) {
      fetchEnrollmentStatus();
    }
  }, [id, fetchEnrollmentStatus]);

  const handleBack = () => navigate("/repositories");

  return (
    <div className="container mx-auto py-8 px-4">
      {error ? (
        <Alert variant="destructive" className="mb-6">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      ) : null}

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <p className="text-lg">Loading repository details...</p>
        </div>
      ) : repository ? (
        <div>
          <h1 className="text-3xl font-bold mb-6">{repository.name}</h1>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Repository Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <RepoProp name="URL" value={repository.url}/>
                <RepoProp name="Full Name" value={repository.fullName}/>
                <RepoProp name="Description" value={repository.description}/>
                <RepoProp name="ID" value={repository.id}/>
                <RepoProp name="Installation id" value={repository.properties?.appInfo?.installationId}/>
                <RepoProp name="Size Kb" value={repository.properties?.meta?.sizeKb}/>
                <div className="flex gap-2 items-center">
                  <DeleteRepoButton repoId={id!}/>
                  <Button onClick={rescan}>Rescan</Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Change Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2 items-center">
                  <h3 className="text-sm font-medium text-muted-foreground">Status:</h3>
                  {enrollmentStatus ? (
                    <span className={`px-2 py-1 rounded text-sm ${
                      enrollmentStatus.enrolled 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {enrollmentStatus.enrolled ? 'Enrolled' : 'Not Enrolled'}
                    </span>
                  ) : (
                    <Loader />
                  )}
                </div>

                {enrollmentStatus?.lastAnalysis && (
                  <RepoProp 
                    name="Last Analysis" 
                    value={new Date(enrollmentStatus.lastAnalysis.seconds * 1000).toLocaleString()}
                  />
                )}

                <div className="flex gap-2 items-center">
                  {enrollmentStatus?.enrolled ? (
                    <Button 
                      variant="outline" 
                      onClick={handleUnenroll}
                      disabled={enrollmentLoading}
                    >
                      {enrollmentLoading && <Loader />}
                      Unenroll from Change Analysis
                    </Button>
                  ) : (
                    <Button 
                      onClick={handleEnroll}
                      disabled={enrollmentLoading}
                    >
                      {enrollmentLoading && <Loader />}
                      Enroll for Change Analysis
                    </Button>
                  )}
                </div>

                <div className="text-sm text-muted-foreground">
                  {enrollmentStatus?.enrolled ? (
                    <p>This repository is enrolled for daily change analysis. Summaries are generated automatically at 9:00 AM daily.</p>
                  ) : (
                    <p>Enroll this repository to receive daily AI-powered summaries of changes, including commits and merged pull requests.</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <ChangeAnalysisList repo={repository}/>

          <RepoAnalysisList repo={repository}/>
        </div>
      ) : (
        <div className="bg-muted p-8 rounded-lg text-center">
          <h3 className="text-xl font-medium mb-2">Repository not found</h3>
          <p className="text-muted-foreground mb-4">
            The repository you're looking for doesn't exist or has been removed.
          </p>
          <Button onClick={() => {
            void handleBack();
          }}>Go Back to Repository List</Button>
        </div>
      )}
    </div>
  );
};

function RepoProp({name, value}: { name: ReactNode, value: ReactNode }) {
  return <div className="flex gap-2 items-center">
    <h3 className="text-sm font-medium text-muted-foreground">{name}:</h3>
    <p className="break-all">{value}</p>
  </div>
}

function DeleteRepoButton({repoId}: { repoId: string }) {
  const {deleteRepository} = useBoundStore()
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();
  const onDelete = useCallback(() => {
    setDeleting(true);
    deleteRepository(repoId)
      .then(() => navigate("/repositories"))
      .catch(e => {
        toast.error(`Failed to delete repo: ${e}`)
        throw e
      }).finally(() => setDeleting(false));
  }, [deleteRepository, repoId, navigate])
  return <div>
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure you want to delete repo?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction asChild>
            <Button onClick={onDelete} disabled={deleting}>{deleting && <Loader/>} Delete</Button>
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
}

export default RepositoryDetailsPage;
