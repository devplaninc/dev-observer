import { BaseClient } from './base';
import {
  AddGithubRepositoryRequest,
  AddGithubRepositoryResponse,
  ListGithubRepositoriesResponse,
  GetRepositoryResponse,
  DeleteRepositoryResponse,
  RescanRepositoryResponse,
  EnrollRepositoryForChangeAnalysisRequest,
  EnrollRepositoryForChangeAnalysisResponse,
  UnenrollRepositoryFromChangeAnalysisRequest,
  UnenrollRepositoryFromChangeAnalysisResponse,
  GetChangeAnalysesResponse,
  GetChangeAnalysisResponse
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
   * Enroll a repository for change analysis
   * @param repoId - The repository ID
   * @returns The enroll repository response
   */
  async enrollForChangeAnalysis(repoId: string): Promise<EnrollRepositoryForChangeAnalysisResponse> {
    const request: EnrollRepositoryForChangeAnalysisRequest = { repoId };
    return this._post(`/api/v1/repositories/${repoId}/change-analysis/enroll`, EnrollRepositoryForChangeAnalysisResponse, EnrollRepositoryForChangeAnalysisRequest.toJSON(request));
  }

  /**
   * Unenroll a repository from change analysis
   * @param repoId - The repository ID
   * @returns The unenroll repository response
   */
  async unenrollFromChangeAnalysis(repoId: string): Promise<UnenrollRepositoryFromChangeAnalysisResponse> {
    const request: UnenrollRepositoryFromChangeAnalysisRequest = { repoId };
    return this._post(`/api/v1/repositories/${repoId}/change-analysis/unenroll`, UnenrollRepositoryFromChangeAnalysisResponse, UnenrollRepositoryFromChangeAnalysisRequest.toJSON(request));
  }

  /**
   * Get change analyses for a repository
   * @param repoId - The repository ID
   * @param dateFrom - Optional start date filter
   * @param dateTo - Optional end date filter
   * @param status - Optional status filter
   * @returns The change analyses response
   */
  async getChangeAnalyses(repoId: string, dateFrom?: string, dateTo?: string, status?: string): Promise<GetChangeAnalysesResponse> {
    const params = new URLSearchParams();
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (status) params.append('status', status);
    
    const url = `/api/v1/repositories/${repoId}/change-analyses${params.toString() ? `?${params.toString()}` : ''}`;
    return this._get(url, GetChangeAnalysesResponse);
  }

  /**
   * Get a specific change analysis
   * @param analysisId - The analysis ID
   * @returns The change analysis response
   */
  async getChangeAnalysis(analysisId: string): Promise<GetChangeAnalysisResponse> {
    return this._get(`/api/v1/change-analyses/${analysisId}`, GetChangeAnalysisResponse);
  }
}