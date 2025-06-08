#!/bin/bash
set -e

# This script creates a default SDS configuration file for Envoy if it doesn't exist
# This allows Envoy to start successfully even if no certificates are available yet

# Configuration
ENVOY_CERTS_DIR=/etc/envoy/certs
SDS_CONFIG_FILE=${ENVOY_CERTS_DIR}/sds_envoy_cert.json

# Create the certs directory if it doesn't exist
mkdir -p ${ENVOY_CERTS_DIR}

# Create a default SDS configuration file if it doesn't exist
if [ ! -f "${SDS_CONFIG_FILE}" ]; then
  echo "Creating default SDS configuration file at ${SDS_CONFIG_FILE}"
  cat > ${SDS_CONFIG_FILE} << EOF
{
  "resources": []
}
EOF
fi

# Start Envoy
exec /usr/local/bin/envoy -c /etc/envoy/envoy.yaml --service-node ${HOSTNAME} --service-cluster dev-observer