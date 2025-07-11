import React from "react";
import {Link} from "react-router";
import {Card, CardContent, CardFooter, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {Button} from "@/components/ui/button.tsx";
import AddRepositoryForm from "@/components/AddRepositoryForm.tsx";
import {useRepositories} from "@/hooks/useRepositoryQueries.ts";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";
import {EnrollmentToggle} from "@/components/repos/EnrollmentToggle.tsx";
import {useBoundStore} from "@/store/use-bound-store.tsx";

const RepositoryListPage: React.FC = () => {
  const {repositories, error, reload} = useRepositories();
  const {enrollRepository, unenrollRepository} = useBoundStore();

  const handleEnrollmentToggle = async (repoId: string, enrolled: boolean) => {
    try {
      if (enrolled) {
        await enrollRepository(repoId);
      } else {
        await unenrollRepository(repoId);
      }
    } catch (error) {
      console.error('Failed to toggle enrollment:', error);
    }
  };

  if (repositories === undefined) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">GitHub Repositories</h1>

      <div>
        <AddRepositoryForm/>
      </div>

      {repositories.length === 0 ? (
        <div className="bg-muted p-8 rounded-lg text-center">
          <h3 className="text-xl font-medium mb-2">No repositories found</h3>
          <p className="text-muted-foreground mb-4">
            Add your first GitHub repository using the form above.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {repositories.map(repo => (
            <Card key={repo.id} className="h-full hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle>{repo.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground break-all">{repo.url}</p>
                <EnrollmentToggle
                  repoId={repo.id}
                  repoName={repo.fullName}
                  isEnrolled={repo.changeAnalysisEnrolled || false}
                  onToggle={(enrolled) => handleEnrollmentToggle(repo.id, enrolled)}
                />
              </CardContent>
              <CardFooter>
                <Link to={`/repositories/${repo.id}`} className="w-full">
                  <Button variant="outline" size="sm" className="w-full">View Details</Button>
                </Link>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {repositories.length > 0 && (
        <div className="mt-6 text-center">
          <Button onClick={() => {
            void reload();
          }} variant="outline">
            Refresh Repositories
          </Button>
        </div>
      )}
    </div>
  );
};

export default RepositoryListPage;
