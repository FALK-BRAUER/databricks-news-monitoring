"""AWS Secrets Manager integration."""

import json
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError


class AWSSecretsManager:
    """Manage secrets from AWS Secrets Manager."""

    def __init__(self, region_name: str = "ap-southeast-1"):
        """Initialize the secrets manager client.

        Args:
            region_name: AWS region name
        """
        self.region_name = region_name
        self.client = boto3.client('secretsmanager', region_name=region_name)
        self._cache = {}

    def get_secret(self, secret_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """Retrieve a secret from AWS Secrets Manager.

        Args:
            secret_name: Name of the secret to retrieve
            use_cache: Whether to use cached value if available

        Returns:
            Dictionary containing the secret values

        Raises:
            ClientError: If the secret cannot be retrieved
        """
        if use_cache and secret_name in self._cache:
            return self._cache[secret_name]

        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_string = response['SecretString']
            secret_dict = json.loads(secret_string)

            if use_cache:
                self._cache[secret_name] = secret_dict

            return secret_dict

        except ClientError as e:
            raise Exception(f"Error retrieving secret {secret_name}: {str(e)}")

    def get_secret_value(self, secret_name: str, key: str, default: Any = None) -> Any:
        """Get a specific value from a secret.

        Args:
            secret_name: Name of the secret
            key: Key within the secret
            default: Default value if key not found

        Returns:
            The secret value or default
        """
        secret = self.get_secret(secret_name)
        return secret.get(key, default)

    def get_github_token(self) -> Optional[str]:
        """Get the GitHub API token.

        Returns:
            GitHub token or None
        """
        return self.get_secret_value('AWS', 'GITHUB')

    def get_api_key(self, api_name: str) -> Optional[str]:
        """Get an API key from secrets.

        Args:
            api_name: Name of the API key to retrieve

        Returns:
            API key or None
        """
        return self.get_secret_value('AWS', api_name.upper())


# Singleton instance
_secrets_manager = None


def get_secrets_manager() -> AWSSecretsManager:
    """Get the singleton secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = AWSSecretsManager()
    return _secrets_manager
