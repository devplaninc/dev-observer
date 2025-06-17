import {BaseClient} from "./base";
import {ConfigClient} from "./config";
import {ObservationsClient} from "./observations";
import {RepositoriesClient} from "./repositories";
import {AxiosRequestConfig} from "axios";

/**
 * Main API client that combines all service clients
 */
export class ApiClient extends BaseClient {
  readonly config: ConfigClient;
  readonly observations: ObservationsClient;
  readonly repositories: RepositoriesClient;

  /**
   * Create a new ApiClient
   * @param baseUrl - The base URL for the API
   * @param config - Additional Axios configuration
   */
  constructor(baseUrl: string = 'http://localhost:8090', config: AxiosRequestConfig = {}) {
    super(baseUrl, config);
    this.config = new ConfigClient(baseUrl, config);
    this.observations = new ObservationsClient(baseUrl, config);
    this.repositories = new RepositoriesClient(baseUrl, config);
  }

  /**
   * Set the authorization token for all service clients
   * @param token - The authorization token
   */
  override setAuthToken(token: string): void {
    super.setAuthToken(token);
    this.config.setAuthToken(token);
    this.observations.setAuthToken(token);
    this.repositories.setAuthToken(token);
  }

  /**
   * Clear the authorization token for all service clients
   */
  override clearAuthToken(): void {
    super.clearAuthToken();
    this.config.clearAuthToken();
    this.observations.clearAuthToken();
    this.repositories.clearAuthToken();
  }
}