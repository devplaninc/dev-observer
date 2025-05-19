import React from "react";
import {useNavigate, useParams} from "react-router";
import {Card, CardContent, CardHeader, CardTitle} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import {Alert, AlertDescription, AlertTitle} from "@/components/ui/alert";
import {useRepositoryQuery} from "@/hooks/useRepositoryQueries";

const RepositoryDetailsPage: React.FC = () => {
  const {id} = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {repository, loading, error} = useRepositoryQuery(id ?? '');

  const errorMessage = error instanceof Error ? error.message : 'An error occurred';

  const handleBack = () => navigate("/repositories");

  return (
    <div className="container mx-auto py-8 px-4">
      <Button
        variant="outline"
        onClick={() => {
          void handleBack();
        }}
        className="mb-6"
      >
        ← Back to Repositories
      </Button>

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
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground">Repository URL</h3>
                  <p className="break-all">{repository.url}</p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-muted-foreground">Repository ID</h3>
                  <p>{repository.id}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Analysis Data</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-muted p-8 rounded-lg text-center">
                <h3 className="text-xl font-medium mb-2">No analysis data available</h3>
                <p className="text-muted-foreground">
                  This is a placeholder for future detailed analysis data.
                </p>
              </div>
            </CardContent>
          </Card>
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

export default RepositoryDetailsPage;
