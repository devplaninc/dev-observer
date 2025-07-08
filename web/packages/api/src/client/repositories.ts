import { BaseClient } from './base';
import {
  AddGithubRepositoryRequest,
  AddGithubRepositoryResponse,
  ListGithubRepositoriesResponse,
  GetRepositoryResponse,
  DeleteRepositoryResponse,
  RescanRepositoryResponse,
  ListGithubChangeSummariesRequest,
  ListGithubChangeSummariesResponse,
  GetGithubChangeSummaryRequest,
  GetGithubChangeSummaryResponse
} from '../pb/dev_observer/api/web/repositories';

/**
 * Client for interacting with the Repositories API
 */
export class RepositoriesClient extends BaseClient {
  /**
   * Add a GitHub repository
   * @param request - The add repository request
   * @returns The add repository response
   */
  async add(request: AddGithubRepositoryRequest): Promise<AddGithubRepositoryResponse> {
    return this._post('/api/v1/repositories', AddGithubRepositoryResponse,  AddGithubRepositoryRequest.toJSON(request));
  }

  /**
   * List all GitHub repositories
   * @returns The list repositories response
   */
  async list(): Promise<ListGithubRepositoriesResponse> {
    return this._get('/api/v1/repositories', ListGithubRepositoriesResponse);
  }

  /**
   * Get a specific GitHub repository
   * @param repoId - The repository ID
   * @returns The get repository response
   */
  async get(repoId: string): Promise<GetRepositoryResponse> {
    return this._get(`/api/v1/repositories/${repoId}`, GetRepositoryResponse);
  }

  /**
   * Delete a specific GitHub repository
   * @param repoId - The repository ID
   * @returns The delete repository response
   */
  async delete(repoId: string): Promise<DeleteRepositoryResponse> {
    return this._delete(`/api/v1/repositories/${repoId}`, DeleteRepositoryResponse);
  }

  /**
   * Trigger a rescan of a specific GitHub repository
   * @param repoId - The repository ID
   * @returns The rescan repository response
   */
  async rescan(repoId: string): Promise<RescanRepositoryResponse> {
    return this._post(`/api/v1/repositories/${repoId}/rescan`, RescanRepositoryResponse);
  }

  /**
   * List GitHub change summaries for a repository
   * @param repoId - The repository ID
   * @param options - Optional query parameters
   * @returns The list change summaries response
   */
  async listChangeSummaries(
    repoId: string,
    options?: {
      analysisType?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<ListGithubChangeSummariesResponse> {
    const params = new URLSearchParams();
    if (options?.analysisType) params.append('analysis_type', options.analysisType);
    if (options?.limit) params.append('limit', options.limit.toString());
    if (options?.offset) params.append('offset', options.offset.toString());
    
    const queryString = params.toString();
    const url = `/api/v1/repositories/${repoId}/change-summaries${queryString ? `?${queryString}` : ''}`;
    
    return this._get(url, ListGithubChangeSummariesResponse);
  }

  /**
   * Get a specific GitHub change summary
   * @param summaryId - The change summary ID
   * @returns The get change summary response
   */
  async getChangeSummary(summaryId: string): Promise<GetGithubChangeSummaryResponse> {
    return this._get(`/api/v1/repositories/change-summaries/${summaryId}`, GetGithubChangeSummaryResponse);
  }
}