import React from "react";
import {Link} from "react-router";
import {Card, CardContent, CardFooter, CardHeader, CardTitle} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import AddRepositoryForm from "@/components/AddRepositoryForm";
import {useRepositoriesQuery} from "@/hooks/useRepositoryQueries";
import type {Repository} from "@/types/repository";
import {ErrorAlert} from "@/components/ErrorAlert.tsx";
import {Loader} from "@/components/Loader.tsx";

const RepositoryListPage: React.FC = () => {
  const {repositories, error, reload} = useRepositoriesQuery();

  if (repositories === undefined) {
    if (error) {
      return <ErrorAlert err={error}/>
    }
    return <Loader/>
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8">GitHub Repositories</h1>

      <div className="mb-8">
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
          {repositories.map((repo: Repository) => (
            <Link to={`/repositories/${repo.id}`} key={repo.id}>
              <Card className="h-full hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle>{repo.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground break-all">{repo.url}</p>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" size="sm">View Details</Button>
                </CardFooter>
              </Card>
            </Link>
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
