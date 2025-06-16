import { BaseClient } from './base';
import {
  GetGlobalConfigResponse,
  UpdateGlobalConfigRequest,
  UpdateGlobalConfigResponse,
  GetUserManagementStatusResponse
} from '../pb/dev_observer/api/web/config';

/**
 * Client for interacting with the Config API
 */
export class ConfigClient extends BaseClient {
  /**
   * Get the global configuration
   * @returns The global configuration response
   */
  async getGlobalConfig(): Promise<GetGlobalConfigResponse> {
    return this._get('/api/v1/config', GetGlobalConfigResponse);
  }

  async updateGlobalConfig(request: UpdateGlobalConfigRequest): Promise<UpdateGlobalConfigResponse> {
    return this._post('/api/v1/config', UpdateGlobalConfigResponse, UpdateGlobalConfigRequest.toJSON(request));
  }

  /**
   * Get the user management status
   * @returns The user management status response
   */
  async getUserManagementStatus(): Promise<GetUserManagementStatusResponse> {
    return this._get('/api/v1/config/users/status', GetUserManagementStatusResponse);
  }
}