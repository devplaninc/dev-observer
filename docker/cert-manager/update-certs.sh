#!/bin/bash
set -e

# This script updates the SDS configuration file for Envoy based on the certificates obtained by Certbot

# Configuration
DOMAIN_NAME=${DOMAIN_NAME:-localhost}
CERT_NAME=${CERT_NAME:-envoy-cert}
LETSENCRYPT_DIR=/etc/letsencrypt
ENVOY_CERTS_DIR=/etc/envoy/certs
SDS_CONFIG_FILE=${ENVOY_CERTS_DIR}/sds_envoy_cert.json

# Check if certificates exist
if [ ! -d "${LETSENCRYPT_DIR}/live/${CERT_NAME}" ]; then
  echo "Certificates not found for ${CERT_NAME}. Exiting."
  exit 1
fi