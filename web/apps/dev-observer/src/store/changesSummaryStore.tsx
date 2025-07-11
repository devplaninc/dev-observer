import type {StateCreator} from "zustand";
import {changesSummariesAPI, changesSummaryAPI} from "@/store/apiPaths.tsx";
import {
  ListChangesSummariesRequest,
  ListChangesSummariesResponse,
  CreateChangesSummaryRequest,
  CreateChangesSummaryResponse,
  DeleteChangesSummaryResponse,
  GitHubChangesSummary
} from "@devplan/observer-api";
import {fetchWithAuth, VoidParser} from "@/store/api.tsx";

export interface ChangesSummaryState {
  summaries: Record<string, GitHubChangesSummary[]>;
  loading: Record<string, boolean>;
  error: Record<string, string | null>;

  fetchSummaries: (repoId: string, limit?: number, offset?: number) => Promise<void>;
  createSummary: (repoId: string, daysBack?: number) => Promise<void>;
  deleteSummary: (summaryId: string, repoId: string) => Promise<void>;
  clearError: (repoId: string) => void;
}

export const createChangesSummarySlice: StateCreator<
  ChangesSummaryState,
  [],
  [],
  ChangesSummaryState
> = ((set, get) => ({
  summaries: {},
  loading: {},
  error: {},

  fetchSummaries: async (repoId: string, limit = 20, offset = 0) => {
    set(state => ({
      ...state,
      loading: { ...state.loading, [repoId]: true },
      error: { ...state.error, [repoId]: null }
    }));

    try {
      const response = await fetchWithAuth(
        `${changesSummariesAPI()}?repo_id=${repoId}&limit=${limit}&offset=${offset}`,
        ListChangesSummariesResponse
      ) as ListChangesSummariesResponse;
      
      set(state => ({
        ...state,
        summaries: { ...state.summaries, [repoId]: response.summaries },
        loading: { ...state.loading, [repoId]: false }
      }));
    } catch (err) {
      set(state => ({
        ...state,
        error: { ...state.error, [repoId]: err instanceof Error ? err.message : 'Failed to fetch summaries' },
        loading: { ...state.loading, [repoId]: false }
      }));
    }
  },

  createSummary: async (repoId: string, daysBack = 7) => {
    try {
      await fetchWithAuth(
        changesSummariesAPI(),
        CreateChangesSummaryResponse,
        {
          method: "POST",
          body: JSON.stringify(CreateChangesSummaryRequest.toJSON({ repoId, daysBack }))
        }
      );
      
      // Refresh the summaries for this repo
      await get().fetchSummaries(repoId);
    } catch (err) {
      set(state => ({
        ...state,
        error: { ...state.error, [repoId]: err instanceof Error ? err.message : 'Failed to create summary' }
      }));
    }
  },

  deleteSummary: async (summaryId: string, repoId: string) => {
    try {
      await fetchWithAuth(
        changesSummaryAPI(summaryId),
        DeleteChangesSummaryResponse,
        { method: "DELETE" }
      );
      
      // Remove from local state
      set(state => ({
        ...state,
        summaries: {
          ...state.summaries,
          [repoId]: state.summaries[repoId]?.filter(s => s.id !== summaryId) || []
        }
      }));
    } catch (err) {
      set(state => ({
        ...state,
        error: { ...state.error, [repoId]: err instanceof Error ? err.message : 'Failed to delete summary' }
      }));
    }
  },

  clearError: (repoId: string) => {
    set(state => ({
      ...state,
      error: { ...state.error, [repoId]: null }
    }));
  }
})); 