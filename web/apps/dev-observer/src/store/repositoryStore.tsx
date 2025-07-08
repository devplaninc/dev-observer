import type {StateCreator} from "zustand";
import {repoAPI, repoRescanAPI, reposAPI, repoChangeAnalysisEnrollAPI, repoChangeAnalysisUnenrollAPI, repoChangeAnalysisStatusAPI, changeSummariesAPI} from "@/store/apiPaths.tsx";
import {
  AddGithubRepositoryRequest,
  AddGithubRepositoryResponse,
  DeleteRepositoryResponse,
  GetRepositoryResponse,
  ListGithubRepositoriesResponse,
  EnrollRepositoryResponse,
  UnenrollRepositoryResponse,
  GetRepositoryEnrollmentStatusResponse,
  GetChangeSummariesResponse,
  ChangeSummary
} from "@devplan/observer-api";
import type {GitHubRepository} from "@devplan/observer-api";
import {fetchWithAuth, VoidParser} from "@/store/api.tsx";

export interface RepositoryState {
  repositories: Record<string, GitHubRepository>;
  changeSummaries: Record<string, ChangeSummary[]>;

  fetchRepositories: () => Promise<void>;
  fetchRepositoryById: (id: string) => Promise<void>;
  addRepository: (url: string) => Promise<void>;
  deleteRepository: (id: string) => Promise<void>;
  rescanRepository: (id: string) => Promise<void>;

  // Change Analysis functions
  enrollRepositoryForChangeAnalysis: (id: string) => Promise<void>;
  unenrollRepositoryFromChangeAnalysis: (id: string) => Promise<void>;
  getRepositoryEnrollmentStatus: (id: string) => Promise<GetRepositoryEnrollmentStatusResponse>;
  fetchChangeSummaries: (repoId?: string, status?: string, startDate?: string, endDate?: string) => Promise<void>;
}

export const createRepositoriesSlice: StateCreator<
  RepositoryState,
  [],
  [],
  RepositoryState
> = ((set) => ({
  repositories: {},
  changeSummaries: {},

  fetchRepositories: async () => fetchWithAuth(reposAPI(), ListGithubRepositoriesResponse)
    .then(res => {
      const {repos} = res
      const repositories = repos.reduce((a, r) => ({...a, [r.id]: r}), {} as Record<string, GitHubRepository>)
      set(s => ({...s, repositories}))
    }),

  fetchRepositoryById: async id => fetchWithAuth(repoAPI(id), GetRepositoryResponse)
    .then(r => {
      const {repo} = r
      if (repo) {
        set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}))
      }
    }),

  addRepository: async url => fetchWithAuth(
    reposAPI(),
    AddGithubRepositoryResponse,
    {method: "POST", body: JSON.stringify(AddGithubRepositoryRequest.toJSON({url}))},
  ).then(r => {
    const {repo} = r
    if (repo) {
      set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}))
    }
  }),
  deleteRepository: async id => fetchWithAuth(repoAPI(id), DeleteRepositoryResponse, {method: "DELETE"})
    .then(r => {
      const {repos} = r
      const repositories = repos.reduce((a, r) => ({...a, [r.id]: r}), {} as Record<string, GitHubRepository>)
      set(s => ({...s, repositories}))
    }),
  rescanRepository: async id => fetchWithAuth(repoRescanAPI(id), new VoidParser(), {method: "POST"}),

  // Change Analysis functions
  enrollRepositoryForChangeAnalysis: async id => fetchWithAuth(
    repoChangeAnalysisEnrollAPI(id),
    EnrollRepositoryResponse,
    {method: "POST"}
  ).then(() => {
    // Optionally refresh repository data to get updated enrollment status
    // This could be enhanced to update local state directly
  }),

  unenrollRepositoryFromChangeAnalysis: async id => fetchWithAuth(
    repoChangeAnalysisUnenrollAPI(id),
    UnenrollRepositoryResponse,
    {method: "POST"}
  ).then(() => {
    // Optionally refresh repository data to get updated enrollment status
    // This could be enhanced to update local state directly
  }),

  getRepositoryEnrollmentStatus: async id => fetchWithAuth(
    repoChangeAnalysisStatusAPI(id),
    GetRepositoryEnrollmentStatusResponse
  ),

  fetchChangeSummaries: async (repoId, status, startDate, endDate) => {
    const params = new URLSearchParams();
    if (repoId) params.append('repo_id', repoId);
    if (status) params.append('status', status);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const url = params.toString() ? `${changeSummariesAPI()}?${params.toString()}` : changeSummariesAPI();

    return fetchWithAuth(url, GetChangeSummariesResponse)
      .then(res => {
        const {summaries} = res;
        const key = repoId || 'all';
        set(s => ({...s, changeSummaries: {...s.changeSummaries, [key]: summaries}}));
      });
  },
}));
