import os
import logging
from typing import List
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from dev_observer.api.types.observations_pb2 import Observation, ObservationKey
from dev_observer.observations.provider import ObservationsProvider


_log = logging.getLogger(__name__)


class S3ObservationsProvider(ObservationsProvider):
    """
    Implementation of ObservationsProvider that stores observations in an S3-compatible storage.
    """
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str, region: str = "us-east-1"):
        """
        Initialize the S3ObservationsProvider.
        
        Args:
            endpoint: The S3-compatible endpoint URL
            access_key: The access key for authentication
            secret_key: The secret key for authentication
            bucket: The bucket name where observations will be stored
            region: The region of the S3 bucket (default: "us-east-1")
        
        Raises:
            ValueError: If the S3 configuration is invalid or the bucket is not accessible
        """
        self._endpoint = endpoint
        self._bucket = bucket
        
        # Initialize the S3 client with custom endpoint
        self._s3 = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Validate the configuration by checking bucket existence and permissions
        self._validate_configuration()
    
    def _validate_configuration(self):
        """
        Validate the S3 configuration by checking bucket existence and permissions.
        
        Raises:
            ValueError: If the S3 configuration is invalid or the bucket is not accessible
        """
        try:
            # Try to list objects in the bucket to check permissions
            self._s3.list_objects_v2(Bucket=self._bucket, MaxKeys=1)
            _log.info(f"Successfully connected to S3 bucket '{self._bucket}' at {self._endpoint}")
        except EndpointConnectionError as e:
            error_msg = f"Unable to connect to S3 endpoint {self._endpoint}. Please check the endpoint URL and network connectivity."
            _log.error(error_msg)
            raise ValueError(error_msg) from e
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code == 'NoSuchBucket':
                error_msg = f"Bucket '{self._bucket}' does not exist. Please create the bucket or check the bucket name."
                _log.error(error_msg)
                raise ValueError(error_msg) from e
            elif error_code in ('AccessDenied', 'Forbidden'):
                error_msg = f"Access denied to bucket '{self._bucket}'. Please check your credentials and permissions."
                _log.error(error_msg)
                raise ValueError(error_msg) from e
            else:
                error_msg = f"Error accessing S3 bucket '{self._bucket}': {str(e)}"
                _log.error(error_msg)
                raise ValueError(error_msg) from e
    
    def _get_object_key(self, key: ObservationKey) -> str:
        """
        Convert an ObservationKey to an S3 object key.
        
        Args:
            key: The ObservationKey to convert
            
        Returns:
            The S3 object key
        """
        return f"{key.kind}/{key.key}"
    
    async def store(self, o: Observation):
        """
        Store an observation in S3.
        
        Args:
            o: The observation to store
        
        Raises:
            RuntimeError: If there's an error storing the observation
        """
        object_key = self._get_object_key(o.key)
        
        try:
            self._s3.put_object(
                Bucket=self._bucket,
                Key=object_key,
                Body=o.content
            )
            _log.debug(f"Stored observation {o.key.kind}/{o.key.name} in S3")
        except ClientError as e:
            error_msg = f"Error storing observation {o.key.kind}/{o.key.name} in S3: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    async def list(self, kind: str) -> List[ObservationKey]:
        """
        List all observations of a specific kind.
        
        Args:
            kind: The kind of observations to list
            
        Returns:
            A list of ObservationKey objects
            
        Raises:
            RuntimeError: If there's an error listing the observations
        """
        result: List[ObservationKey] = []
        prefix = f"{kind}/"
        
        try:
            # List all objects with the given prefix
            paginator = self._s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self._bucket, Prefix=prefix)
            
            for page in pages:
                for obj in page.get('Contents', []):
                    # Extract the key part after the kind prefix
                    full_key = obj['Key']
                    if full_key.startswith(prefix):
                        key_part = full_key[len(prefix):]
                        # Use the last part of the path as the name
                        name = os.path.basename(key_part)
                        result.append(ObservationKey(kind=kind, key=key_part, name=name))
            
            return result
        except ClientError as e:
            error_msg = f"Error listing observations of kind '{kind}' from S3: {str(e)}"
            _log.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    async def get(self, key: ObservationKey) -> Observation:
        """
        Get an observation from S3.
        
        Args:
            key: The key of the observation to get
            
        Returns:
            The observation
            
        Raises:
            RuntimeError: If there's an error getting the observation
        """
        object_key = self._get_object_key(key)
        
        try:
            response = self._s3.get_object(Bucket=self._bucket, Key=object_key)
            content = response['Body'].read().decode('utf-8')
            return Observation(key=key, content=content)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            if error_code == 'NoSuchKey':
                error_msg = f"Observation {key.kind}/{key.name} not found in S3"
                _log.error(error_msg)
                raise RuntimeError(error_msg) from e
            else:
                error_msg = f"Error getting observation {key.kind}/{key.name} from S3: {str(e)}"
                _log.error(error_msg)
                raise RuntimeError(error_msg) from e