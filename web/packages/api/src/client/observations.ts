import { BaseClient } from './base';
import {
  GetObservationResponse,
  GetObservationsResponse,
  GetChangeSummariesRequest,
  GetChangeSummariesResponse
} from '../pb/dev_observer/api/web/observations';

/**
 * Client for interacting with the Observations API
 */
export class ObservationsClient extends BaseClient {
  async listByKind(kind: string): Promise<GetObservationsResponse> {
    return this._get(`/api/v1/observations/kind/${kind}`, GetObservationsResponse);
  }

  async get(kind: string, name: string, key: string): Promise<GetObservationResponse> {
    // The server replaces / with | in the key parameter
    const encodedKey = key.replace(/\//g, '|');
    return this._get(`/api/v1/observation/${kind}/${name}/${encodedKey}`, GetObservationResponse);
  }

  async getChangeSummaries(request: GetChangeSummariesRequest): Promise<GetChangeSummariesResponse> {
    return this._post('/change-summaries', GetChangeSummariesResponse, request);
  }
}