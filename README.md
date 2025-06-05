# dev-observer
Observer of all the important stuff.

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

### Testing

You can test the setup by sending HTTP requests to the Envoy proxy:

- Web service: `http://localhost:8080/`
- Server API: `http://localhost:8080/api/`

Replace `localhost` with your server's hostname and `8080` with the configured `ENVOY_PORT` if different.


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
