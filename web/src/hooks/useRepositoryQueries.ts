import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import type {RepositoryState} from '@/store/useRepositoryStore';
import {useRepositoryStore} from '@/store/useRepositoryStore';
import {useCallback} from "react";
import {useShallow} from "zustand/react/shallow";
import type {Repository} from "@/types/repository.ts";

export interface QueryResultCommon {
  error: Error | null
  loading: boolean,
  reload: () => Promise<void>
}

// Query keys for caching and invalidation
export const repositoryKeys = {
  all: ['repositories'] as const,
  lists: () => [...repositoryKeys.all, 'list'] as const,
  detail: (id: string) => [...repositoryKeys.all, 'detail', id] as const,
};

export function useRepositoriesQuery(): { repositories: Repository[] | undefined } & QueryResultCommon {
  const {fetchRepositories} = useRepositoryStore();
  const queryFn = useCallback(async () => {
    await fetchRepositories();
    return true
  }, [fetchRepositories])
  const {isFetching, error, refetch} = useQuery({queryKey: repositoryKeys.lists(), queryFn});
  const repositories = useRepositoryStore(useShallow(s => Object.values(s.repositories)));
  return {
    repositories, loading: isFetching, error: error,
    reload: async () => {
      await refetch()
    }
  }
}

// Hook for fetching a single repository by ID
export function useRepositoryQuery(id: string): { repository: Repository | undefined } & QueryResultCommon {
  const fetchRepositoryById = useRepositoryStore((state: RepositoryState) => state.fetchRepositoryById);
  const queryFn = useCallback(async () => {
    await fetchRepositoryById(id);
    return true
  }, [fetchRepositoryById, id])
  const {error, isFetching, refetch} = useQuery({queryKey: repositoryKeys.detail(id), queryFn, enabled: !!id});
  const repository = useRepositoryStore(useShallow(s => s.repositories[id]));
  return {
    repository, loading: isFetching, error: error,
    reload: async () => {
      await refetch()
    }
  }
}

// Hook for adding a repository
export const useAddRepositoryMutation = () => {
  const queryClient = useQueryClient();
  const addRepository = useRepositoryStore((state: RepositoryState) => state.addRepository);

  return useMutation({
    mutationFn: (url: string) => addRepository(url),
    onSuccess: () => {
      // Invalidate the repositories list query to refetch the updated list
      void queryClient.invalidateQueries({queryKey: repositoryKeys.lists()});
    },
  });
};
