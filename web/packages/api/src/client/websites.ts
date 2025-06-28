import { BaseClient } from './base';
import {
  AddWebSiteRequest,
  AddWebSiteResponse,
  ListWebSitesResponse,
  GetWebSiteResponse,
  DeleteWebSiteResponse,
  RescanWebSiteResponse
} from '../pb/dev_observer/api/web/sites';

/**
 * Client for interacting with the Websites API
 */
export class WebsitesClient extends BaseClient {
  /**
   * Add a website
   * @param request - The add website request
   * @returns The add website response
   */
  async add(request: AddWebSiteRequest): Promise<AddWebSiteResponse> {
    return this._post('/api/v1/websites', AddWebSiteResponse, AddWebSiteRequest.toJSON(request));
  }

  /**
   * List all websites
   * @returns The list websites response
   */
  async list(): Promise<ListWebSitesResponse> {
    return this._get('/api/v1/websites', ListWebSitesResponse);
  }

  /**
   * Get a specific website
   * @param siteId - The website ID
   * @returns The get website response
   */
  async get(siteId: string): Promise<GetWebSiteResponse> {
    return this._get(`/api/v1/websites/${siteId}`, GetWebSiteResponse);
  }

  /**
   * Delete a specific website
   * @param siteId - The website ID
   * @returns The delete website response
   */
  async delete(siteId: string): Promise<DeleteWebSiteResponse> {
    return this._delete(`/api/v1/websites/${siteId}`, DeleteWebSiteResponse);
  }

  /**
   * Trigger a rescan of a specific website
   * @param siteId - The website ID
   * @returns The rescan website response
   */
  async rescan(siteId: string): Promise<RescanWebSiteResponse> {
    return this._post(`/api/v1/websites/${siteId}/rescan`, RescanWebSiteResponse);
  }
}