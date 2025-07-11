import type {StateCreator} from "zustand";
import {repoAPI, repoRescanAPI, reposAPI} from "@/store/apiPaths.tsx";
import {
  AddGithubRepositoryRequest,
  AddGithubRepositoryResponse,
  DeleteRepositoryResponse,
  GetRepositoryResponse,
  ListGithubRepositoriesResponse,
  EnrollRepositoryForChangeAnalysisResponse,
  UnenrollRepositoryFromChangeAnalysisResponse,
  GetChangeAnalysesResponse,
  GetChangeAnalysisResponse
} from "@devplan/observer-api";
import type {GitHubRepository, RepoChangeAnalysis} from "@devplan/observer-api";
import {fetchWithAuth, VoidParser} from "@/store/api.tsx";

export interface RepositoryState {
  repositories: Record<string, GitHubRepository>;
  changeAnalyses: Record<string, RepoChangeAnalysis[]>;

  fetchRepositories: () => Promise<void>;
  fetchRepositoryById: (id: string) => Promise<void>;
  addRepository: (url: string) => Promise<void>;
  deleteRepository: (id: string) => Promise<void>;
  rescanRepository: (id: string) => Promise<void>;
  
  enrollForChangeAnalysis: (repoId: string) => Promise<void>;
  unenrollFromChangeAnalysis: (repoId: string) => Promise<void>;
  fetchChangeAnalyses: (repoId: string, dateFrom?: string, dateTo?: string, status?: string) => Promise<void>;
  fetchChangeAnalysis: (analysisId: string) => Promise<RepoChangeAnalysis | null>;
}

export const createRepositoriesSlice: StateCreator<
  RepositoryState,
  [],
  [],
  RepositoryState
> = ((set, get) => ({
  repositories: {},
  changeAnalyses: {},

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

  enrollForChangeAnalysis: async repoId => fetchWithAuth(
    `/api/v1/repositories/${repoId}/change-analysis/enroll`,
    EnrollRepositoryForChangeAnalysisResponse,
    {method: "POST"}
  ).then(r => {
    const {repo} = r;
    if (repo) {
      set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}));
    }
  }),

  unenrollFromChangeAnalysis: async repoId => fetchWithAuth(
    `/api/v1/repositories/${repoId}/change-analysis/unenroll`,
    UnenrollRepositoryFromChangeAnalysisResponse,
    {method: "POST"}
  ).then(r => {
    const {repo} = r;
    if (repo) {
      set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}));
    }
  }),

  fetchChangeAnalyses: async (repoId, dateFrom, dateTo, status) => {
    const params = new URLSearchParams();
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (status) params.append('status', status);
    
    const url = `/api/v1/repositories/${repoId}/change-analyses${params.toString() ? `?${params.toString()}` : ''}`;
    
    return fetchWithAuth(url, GetChangeAnalysesResponse).then(res => {
      const {analyses} = res;
      set(s => ({...s, changeAnalyses: {...s.changeAnalyses, [repoId]: analyses}}));
    });
  },

  fetchChangeAnalysis: async analysisId => fetchWithAuth(
    `/api/v1/change-analyses/${analysisId}`,
    GetChangeAnalysisResponse
  ).then(r => {
    const {analysis} = r;
    return analysis || null;
  }),
}));
