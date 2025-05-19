import {create} from 'zustand';
import {delay, extractRepoName, validateGitHubUrl} from '@/utils/repositoryUtils';
import type {ApiError, Repository} from '@/types/repository';

export interface RepositoryState {
  repositories: Record<string, Repository>;

  // Actions
  fetchRepositories: () => Promise<void>;
  fetchRepositoryById: (id: string) => Promise<void>;
  addRepository: (url: string) => Promise<void>;
  reset: () => void;
}

// Initial repositories data
const initialRepositories: Record<string, Repository> = {
  "1": {
    id: "1",
    name: "devplaninc/webapp",
    url: "https://github.com/devplaninc/webapp",
  },
  "2": {
    id: "2",
    name: "devplaninc/dev-observer",
    url: "https://github.com/devplaninc/dev-observer",
  },
};

export const useRepositoryStore = create<RepositoryState>((set: (state: Partial<RepositoryState> | ((state: RepositoryState) => Partial<RepositoryState>)) => void, get: () => RepositoryState) => ({
  repositories: initialRepositories,

  fetchRepositories: async () => {
    try {
      // Simulate network latency (500-1000ms)
      const latency = Math.floor(Math.random() * 500) + 500;
      await delay(latency);

      // Randomly simulate an error (10% chance)
      if (Math.random() < 0.1) {
        const apiError = new Error("Failed to fetch repositories. Please try again.") as Error & ApiError;
        apiError.status = 500;
        throw apiError;
      }
    } catch (err) {
      const error = err as Error;
      console.error("Error loading repositories:", error);
      throw err;
    }
  },

  fetchRepositoryById: async id => {
    try {
      // Simulate network latency (500-1000ms)
      const latency = Math.floor(Math.random() * 500) + 500;
      await delay(latency);

      // Randomly simulate an error (10% chance)
      if (Math.random() < 0.1) {
        const apiError = new Error("Failed to fetch repository. Please try again.") as Error & ApiError;
        apiError.status = 500;
        throw apiError;
      }

      const repository = get().repositories[id]

      if (!repository) {
        const apiError = new Error("Repository not found") as Error & ApiError;
        apiError.status = 404;
        throw apiError;
      }

    } catch (err) {
      const error = err as Error;
      console.error("Error loading repository:", error);
      throw err;
    }
  },

  addRepository: async url => {
    // Simulate network latency (500-1000ms)
    const latency = Math.floor(Math.random() * 500) + 500;
    await delay(latency);

    // Update repositories for validation
    const {repositories} = get();
    // Validate URL
    const validationError = validateGitHubUrl(url, repositories);
    if (validationError) {
      const apiError = new Error("Validation failed") as Error & ApiError;
      apiError.errors = [validationError];
      apiError.status = 400;
      throw apiError;
    }

    // Randomly simulate an error (10% chance)
    if (Math.random() < 0.1) {
      const apiError = new Error("Failed to add repository. Please try again.") as Error & ApiError;
      apiError.status = 500;
      throw apiError;
    }

    // Create new repository
    const newRepository: Repository = {
      id: (Object.values(repositories).length + 1).toString(),
      name: extractRepoName(url),
      url,
    };

    // Update state
    set(s => ({...s, repositories: {...s.repositories, [newRepository.id]: newRepository}}));
  },

  reset: () => set({repositories: {}}),
}));
