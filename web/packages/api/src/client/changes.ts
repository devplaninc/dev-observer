import {BaseClient} from "./base";
import {
  ListChangesSummariesRequest,
  ListChangesSummariesResponse,
  GetChangesSummaryRequest,
  GetChangesSummaryResponse,
  CreateChangesSummaryRequest,
  CreateChangesSummaryResponse,
  DeleteChangesSummaryRequest,
  DeleteChangesSummaryResponse
} from "../pb/dev_observer/api/web/changes";

/**
 * Client for changes summary operations
 */
export class ChangesClient extends BaseClient {
  /**
   * List changes summaries for a repository
   */
  async listChangesSummaries(request: ListChangesSummariesRequest): Promise<ListChangesSummariesResponse> {
    const params = new URLSearchParams();
    params.append('repo_id', request.repoId);
    if (request.limit) params.append('limit', request.limit.toString());
    if (request.offset) params.append('offset', request.offset.toString());
    
    return this._get(`/api/v1/changes-summaries?${params.toString()}`, ListChangesSummariesResponse);
  }

  /**
   * Get a specific changes summary
   */
  async getChangesSummary(request: GetChangesSummaryRequest): Promise<GetChangesSummaryResponse> {
    return this._get(`/api/v1/changes-summaries/${request.summaryId}`, GetChangesSummaryResponse);
  }

  /**
   * Create a new changes summary
   */
  async createChangesSummary(request: CreateChangesSummaryRequest): Promise<CreateChangesSummaryResponse> {
    return this._post('/api/v1/changes-summaries', CreateChangesSummaryResponse, CreateChangesSummaryRequest.toJSON(request));
  }

  /**
   * Delete a changes summary
   */
  async deleteChangesSummary(request: DeleteChangesSummaryRequest): Promise<DeleteChangesSummaryResponse> {
    return this._delete(`/api/v1/changes-summaries/${request.summaryId}`, DeleteChangesSummaryResponse);
  }
} 