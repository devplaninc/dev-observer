#!/bin/bash
set -e

# This script creates a default SDS configuration file for Envoy if it doesn't exist
# This allows Envoy to start successfully even if no certificates are available yet

# Configuration
ENVOY_CERTS_DIR=/etc/envoy/certs
SDS_CONFIG_FILE=${ENVOY_CERTS_DIR}/sds_envoy_cert.json
CERTS_FOLDER="${ENVOY_CERTS_DIR}/live/${CERT_NAME}"

# Create the certs directory if it doesn't exist
mkdir -p ${ENVOY_CERTS_DIR}

echo "Checking SDS config at ${SDS_CONFIG_FILE}"

cert_exists=false
[ -d "$CERTS_FOLDER" ] && cert_exists=true

echo "ENABLE_SSL=$ENABLE_SSL, cert_exists=$cert_exists"

if [ "$ENABLE_SSL" = "true" ] && [ "$cert_exists" = true ]; then
  cat > ${SDS_CONFIG_FILE} << EOF
{
  "resources": [
    {
      "@type": "type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.Secret",
      "name": "envoy_cert",
      "tls_certificate": {
        "certificate_chain": {
          "filename": "${ENVOY_CERTS_DIR}/live/${CERT_NAME}/fullchain.pem"
        },
        "private_key": {
          "filename": "${ENVOY_CERTS_DIR}/live/${CERT_NAME}/privkey.pem"
        }
      }
    }
  ]
}
EOF
  echo "SDS configuration file created with certificate info."

elif [ ! -f "${SDS_CONFIG_FILE}" ]; then
  echo "Creating default SDS configuration file at ${SDS_CONFIG_FILE}"
  cat > ${SDS_CONFIG_FILE} << EOF
{
  "resources": []
}
EOF
fi

# Start Envoy
exec /usr/local/bin/envoy -c /etc/envoy/envoy.yaml --service-node ${HOSTNAME} --service-cluster dev-observer