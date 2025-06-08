# dev-observer
Observer of all the important stuff.

## Setup:

Create file [server/.env.local.secrets](server/.env.local.secrets) and add following there:
```
DEV_OBSERVER__GIT__GITHUB__PERSONAL_TOKEN=<Github personal token, use `gh auth token` to get>
GOOGLE_API_KEY=<GOOGLE_API_TOKEN to use for google-genai>
DEV_OBSERVER__USERS_MANAGEMENT__CLERK__SECRET_KEY=<get key from Clerk>
```

## Docker Images

This repository provides Docker images for both the web frontend and server backend components. These images are built and published to GitHub Packages using GitHub Actions.

### Available Images

- Web Frontend: `ghcr.io/devplaninc/dev-observer-web:<version>`
- Server Backend: `ghcr.io/devplaninc/dev-observer-server:<version>`

### Building and Publishing Docker Images

#### Using GitHub Actions

Docker images can be built and published manually using the GitHub Actions workflow:

1. Go to the "Actions" tab in the GitHub repository
2. Select the "Build and Publish Docker Images" workflow
3. Click "Run workflow"
4. Enter a semantic version tag (e.g., `v1.0.0`)
5. Click "Run workflow"

The workflow will build both Docker images, tag them with the provided version, and publish them to GitHub Packages.

#### Building Locally

You can also build the Docker images locally:

```bash
# Navigate to the repository root
# Build the web frontend image
docker build -t dev-observer-web:local -f docker/web/Dockerfile .

# Build the server backend image
docker build -t dev-observer-server:local -f docker/server/Dockerfile .
```

Note that you must run these commands from the repository root directory, as the Dockerfiles reference files relative to this location.

##### Troubleshooting Local Builds

If you encounter issues during local builds:

- Ensure Docker is installed and running on your system
- Make sure you're running the commands from the repository root directory
- Check that all required files exist (e.g., `web/package.json`, `server/pyproject.toml`, `server/uv.lock`)
- For the server build, the Dockerfile installs the necessary system dependencies (build-essential, libpq-dev) for building Python packages from source
- If you encounter "pg_config executable not found" errors, this indicates that the PostgreSQL development package (libpq-dev) is missing, which is required to build the psycopg2 package

### Using the Docker Images

#### Using Published Images

To pull and run the published Docker images:

```bash
# Pull the images
docker pull ghcr.io/devplaninc/dev-observer-web:<version>
docker pull ghcr.io/devplaninc/dev-observer-server:<version>

# Run the web frontend
docker run -p 3000:3000 ghcr.io/devplaninc/dev-observer-web:<version>

# Run the server backend
docker run -p 8090:8090 ghcr.io/devplaninc/dev-observer-server:<version>
```

#### Using Locally Built Images

If you've built the images locally, you can run them directly:

```bash
# Run the web frontend
docker run -p 3000:3000 dev-observer-web:local

# Run the server backend
docker run -p 8090:8090 dev-observer-server:local
```

## Docker Compose Setup

This repository includes a Docker Compose configuration that runs the web and server services behind a single Envoy proxy container, enabling unified domain and port access with path-based routing.

### Services

The Docker Compose setup includes three services:

1. **Envoy Proxy**: Routes requests based on path prefixes:
   - `/api/*` → routes to the `server` container
   - All other paths → route to the `web` container

2. **Web Service**: Serves the frontend application

3. **Server Service**: Provides the backend API

### Configuration

All service ports, Docker image tags, and logging levels are configurable via environment variables. The following environment variables are available:

#### Envoy Configuration
- `ENVOY_PORT`: The port on which Envoy listens (default: 8080)
- `ENVOY_IMAGE_TAG`: The Docker image tag for Envoy (default: v1.25-latest)
- `ENVOY_LOG_LEVEL`: The log level for Envoy (default: info)

#### Web Service Configuration
- `WEB_IMAGE_TAG`: The Docker image tag for the web service (default: dev-observer-web:latest)
- `WEB_PORT`: The internal port on which the web service listens (default: 3000)
- `WEB_LOG_LEVEL`: The log level for the web service (default: info)
- `NODE_ENV`: The Node.js environment (default: development)

#### Server Service Configuration
- `SERVER_IMAGE_TAG`: The Docker image tag for the server service (default: dev-observer-server:latest)
- `SERVER_PORT`: The internal port on which the server service listens (default: 8000)
- `SERVER_LOG_LEVEL`: The log level for the server service (default: info)
- `PYTHON_ENV`: The Python environment (default: development)

### Environment Files

The repository includes three environment files for different deployment stages:

- `.env.local`: Configuration for local development
- `.env.beta`: Configuration for beta deployment
- `.env.prod`: Configuration for production deployment

To use a specific environment file, use the `--env-file` option with the `docker-compose` command:

```bash
docker-compose --env-file .env.local up
```

### Usage

To start the services:

```bash
# Using the default environment
docker-compose up

# Using a specific environment
docker-compose --env-file .env.beta up

# Running in detached mode
docker-compose up -d
```

To stop the services:

```bash
docker-compose down
```

### SSL Support

The Docker Compose setup includes support for SSL termination at the Envoy proxy level. When enabled, Envoy will terminate SSL connections and forward plain HTTP requests to the web and server services. This feature uses Let's Encrypt for automatic certificate issuance and renewal.

#### How It Works

1. When `ENABLE_SSL=true` and the `ssl` profile is included, the cert-manager service is started alongside Envoy
2. The cert-manager service obtains SSL certificates from Let's Encrypt using the HTTP-01 challenge
3. Envoy is configured to route HTTP-01 challenge requests to the cert-manager service
4. Certificates are automatically renewed before they expire
5. Envoy loads certificates dynamically using SDS (Secret Discovery Service)

#### Enabling SSL

To enable SSL, you need to do two things:

1. Set the `ENABLE_SSL` environment variable to `true` in your environment file:

```bash
# In .env.local, .env.beta, or .env.prod
ENABLE_SSL=true
DOMAIN_NAME=your-domain.com
```

2. Include the `ssl` profile when starting the services:

```bash
docker-compose --env-file .env.beta --profile ssl up
```

Both steps are required for SSL to work properly:
- The `ENABLE_SSL=true` setting is passed to Envoy (but note that the HTTPS listener is always active in the Envoy configuration)
- The `--profile ssl` option starts the cert-manager service that obtains and manages SSL certificates

Without the cert-manager service running, the HTTPS listener in Envoy will not have access to the required SSL certificates and will not be able to handle HTTPS traffic properly.

The cert-manager service will obtain SSL certificates from Let's Encrypt and configure Envoy to use them for SSL termination.

#### Requirements for SSL

- Port 80 must be accessible from the internet for the HTTP-01 challenge
- Port 443 must be accessible for HTTPS connections
- The `DOMAIN_NAME` must resolve to the server's IP address
- The `CERT_EMAIL` must be a valid email address for Let's Encrypt notifications

#### Troubleshooting SSL

If you encounter issues with SSL:

1. Check the cert-manager logs for certificate issuance errors:
   ```bash
   docker-compose logs cert-manager
   ```

2. Verify that ports 80 and 443 are accessible from the internet:
   ```bash
   curl -v http://your-domain.com/.well-known/acme-challenge/test
   ```

3. Check the Envoy logs for certificate loading errors:
   ```bash
   docker-compose logs envoy
   ```

4. Verify that the SDS configuration file exists:
   ```bash
   docker-compose exec envoy ls -la /etc/envoy/certs/sds_envoy_cert.json
   ```

5. If you see an error about missing SDS configuration file:
   ```
   error initializing configuration '/etc/envoy/envoy.yaml': paths must refer to an existing path in the system: '/etc/envoy/certs/sds_envoy_cert.json' does not exist
   ```
   This means the SDS configuration file wasn't created properly. Try restarting the services with:
   ```bash
   docker-compose down
   docker-compose --env-file .env.beta --profile ssl up
   ```

### Testing

You can test the setup by sending HTTP/HTTPS requests to the Envoy proxy:

- Web service (HTTP): `http://localhost:8080/`
- Web service (HTTPS, if SSL enabled): `https://your-domain.com/`
- Server API (HTTP): `http://localhost:8080/api/`
- Server API (HTTPS, if SSL enabled): `https://your-domain.com/api/`

Replace `localhost` with your server's hostname, `8080` with the configured `ENVOY_PORT` if different, and `your-domain.com` with your actual domain name.


## TODO:

- Storage:
  - local
  - Postgres
- Upload configuration:
  - local
  - S3-compatible
- Serving API.
- UI for serving
- Offline testing:
  - Fully local cloning
  - Fully local analysis
