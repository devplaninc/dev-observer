import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError, EndpointConnectionError

from dev_observer.api.types.observations_pb2 import ObservationKey, Observation
from dev_observer.observations.s3 import S3ObservationsProvider


class TestS3ObservationsProvider(unittest.IsolatedAsyncioTestCase):
    @patch('boto3.client')
    async def test_initialization_success(self, mock_boto_client):
        # Setup mock
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # Test successful initialization
        provider = S3ObservationsProvider(
            endpoint="https://s3.example.com",
            access_key="test_access_key",
            secret_key="test_secret_key",
            bucket="test-bucket",
            region="us-west-2"
        )
        
        # Verify boto3 client was created with correct parameters
        mock_boto_client.assert_called_once_with(
            's3',
            endpoint_url="https://s3.example.com",
            aws_access_key_id="test_access_key",
            aws_secret_access_key="test_secret_key",
            region_name="us-west-2"
        )
        
        # Verify bucket validation was called
        mock_s3.list_objects_v2.assert_called_once_with(Bucket="test-bucket", MaxKeys=1)
    
    @patch('boto3.client')
    async def test_initialization_endpoint_error(self, mock_boto_client):
        # Setup mock to raise endpoint connection error
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.list_objects_v2.side_effect = EndpointConnectionError(
            endpoint_url="https://invalid.example.com"
        )
        
        # Test initialization with invalid endpoint
        with self.assertRaises(ValueError) as context:
            S3ObservationsProvider(
                endpoint="https://invalid.example.com",
                access_key="test_access_key",
                secret_key="test_secret_key",
                bucket="test-bucket"
            )
        
        # Verify error message
        self.assertIn("Unable to connect to S3 endpoint", str(context.exception))
    
    @patch('boto3.client')
    async def test_initialization_no_such_bucket(self, mock_boto_client):
        # Setup mock to raise no such bucket error
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.list_objects_v2.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchBucket', 'Message': 'The specified bucket does not exist'}},
            'ListObjectsV2'
        )
        
        # Test initialization with non-existent bucket
        with self.assertRaises(ValueError) as context:
            S3ObservationsProvider(
                endpoint="https://s3.example.com",
                access_key="test_access_key",
                secret_key="test_secret_key",
                bucket="nonexistent-bucket"
            )
        
        # Verify error message
        self.assertIn("Bucket 'nonexistent-bucket' does not exist", str(context.exception))
    
    @patch('boto3.client')
    async def test_initialization_access_denied(self, mock_boto_client):
        # Setup mock to raise access denied error
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.list_objects_v2.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}},
            'ListObjectsV2'
        )
        
        # Test initialization with invalid credentials
        with self.assertRaises(ValueError) as context:
            S3ObservationsProvider(
                endpoint="https://s3.example.com",
                access_key="invalid_access_key",
                secret_key="invalid_secret_key",
                bucket="test-bucket"
            )
        
        # Verify error message
        self.assertIn("Access denied to bucket", str(context.exception))
    
    @patch('boto3.client')
    async def test_store(self, mock_boto_client):
        # Setup mock
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # Create provider
        provider = S3ObservationsProvider(
            endpoint="https://s3.example.com",
            access_key="test_access_key",
            secret_key="test_secret_key",
            bucket="test-bucket"
        )
        
        # Test store method
        observation = Observation(
            key=ObservationKey(kind="test", name="test.md", key="test.md"),
            content="Test content"
        )
        await provider.store(observation)
        
        # Verify S3 put_object was called with correct parameters
        mock_s3.put_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="test/test.md",
            Body="Test content"
        )
    
    @patch('boto3.client')
    async def test_list(self, mock_boto_client):
        # Setup mock
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # Setup paginator mock
        mock_paginator = MagicMock()
        mock_s3.get_paginator.return_value = mock_paginator
        
        # Setup pages mock
        mock_pages = [
            {
                'Contents': [
                    {'Key': 'test/file1.md'},
                    {'Key': 'test/subdir/file2.md'}
                ]
            }
        ]
        mock_paginator.paginate.return_value = mock_pages
        
        # Create provider
        provider = S3ObservationsProvider(
            endpoint="https://s3.example.com",
            access_key="test_access_key",
            secret_key="test_secret_key",
            bucket="test-bucket"
        )
        
        # Test list method
        result = await provider.list("test")
        
        # Verify paginator was called with correct parameters
        mock_s3.get_paginator.assert_called_once_with('list_objects_v2')
        mock_paginator.paginate.assert_called_once_with(Bucket="test-bucket", Prefix="test/")
        
        # Verify result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].kind, "test")
        self.assertEqual(result[0].key, "file1.md")
        self.assertEqual(result[0].name, "file1.md")
        self.assertEqual(result[1].kind, "test")
        self.assertEqual(result[1].key, "subdir/file2.md")
        self.assertEqual(result[1].name, "file2.md")
    
    @patch('boto3.client')
    async def test_get(self, mock_boto_client):
        # Setup mock
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # Setup get_object mock
        mock_body = MagicMock()
        mock_body.read.return_value = b"Test content"
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        # Create provider
        provider = S3ObservationsProvider(
            endpoint="https://s3.example.com",
            access_key="test_access_key",
            secret_key="test_secret_key",
            bucket="test-bucket"
        )
        
        # Test get method
        key = ObservationKey(kind="test", name="test.md", key="test.md")
        result = await provider.get(key)
        
        # Verify get_object was called with correct parameters
        mock_s3.get_object.assert_called_once_with(Bucket="test-bucket", Key="test/test.md")
        
        # Verify result
        self.assertEqual(result.key, key)
        self.assertEqual(result.content, "Test content")
    
    @patch('boto3.client')
    async def test_get_not_found(self, mock_boto_client):
        # Setup mock
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # Setup get_object mock to raise NoSuchKey error
        mock_s3.get_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'The specified key does not exist.'}},
            'GetObject'
        )
        
        # Create provider
        provider = S3ObservationsProvider(
            endpoint="https://s3.example.com",
            access_key="test_access_key",
            secret_key="test_secret_key",
            bucket="test-bucket"
        )
        
        # Test get method with non-existent key
        key = ObservationKey(kind="test", name="nonexistent.md", key="nonexistent.md")
        with self.assertRaises(RuntimeError) as context:
            await provider.get(key)
        
        # Verify error message
        self.assertIn("Observation test/nonexistent.md not found in S3", str(context.exception))