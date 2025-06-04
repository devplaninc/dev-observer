import type {StateCreator} from "zustand";
import {repoAPI, repoRescanAPI, reposAPI} from "@/store/apiPaths.tsx";
import {
  AddGithubRepositoryRequest,
  AddGithubRepositoryResponse,
  DeleteRepositoryResponse,
  GetRepositoryResponse,
  ListGithubRepositoriesResponse
} from "@/pb/dev_observer/api/web/repositories.ts";
import type {GitHubRepository} from "@/pb/dev_observer/api/types/repo.ts";

export interface RepositoryState {
  repositories: Record<string, GitHubRepository>;

  fetchRepositories: () => Promise<void>;
  fetchRepositoryById: (id: string) => Promise<void>;
  addRepository: (url: string) => Promise<void>;
  deleteRepository: (id: string) => Promise<void>;
  rescanRepository: (id: string) => Promise<void>;
}

export const createRepositoriesSlice: StateCreator<
  RepositoryState,
  [],
  [],
  RepositoryState
> = ((set) => ({
  repositories: {},

  fetchRepositories: async () => fetch(reposAPI())
    .then(r => r.ok ? r.json() : Promise.resolve(new Error(r.statusText)))
    .then(js => {
      const {repos} = ListGithubRepositoriesResponse.fromJSON(js)
      const repositories = repos.reduce((a, r) => ({...a, [r.id]: r}), {} as Record<string, GitHubRepository>)
      set(s => ({...s, repositories}))
    }),

  fetchRepositoryById: async id => fetch(repoAPI(id))
    .then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
    .then(js => {
      const {repo} = GetRepositoryResponse.fromJSON(js)
      if (repo) {
        set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}))
      }
    }),

  addRepository: async url => fetch(reposAPI(),
    {method: "POST", body: JSON.stringify(AddGithubRepositoryRequest.toJSON({url}))}
  ).then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
    .then(js => {
      const {repo} = AddGithubRepositoryResponse.fromJSON(js)
      if (repo) {
        set(s => ({...s, repositories: {...s.repositories, [repo.id]: repo}}))
      }
    }),
  deleteRepository: async id => fetch(repoAPI(id), {method: "DELETE"})
    .then(r => r.ok ? r.json() : Promise.reject(new Error(r.statusText)))
    .then(js => {
      const {repos} = DeleteRepositoryResponse.fromJSON(js)
      const repositories = repos.reduce((a, r) => ({...a, [r.id]: r}), {} as Record<string, GitHubRepository>)
      set(s => ({...s, repositories}))
    }),
  rescanRepository: async id => fetch(repoRescanAPI(id), {method: "POST"})
    .then(r => {
      if (!r.ok) {
        return Promise.reject(new Error(r.statusText))
      }
    }),
}));
