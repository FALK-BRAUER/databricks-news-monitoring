"""Configuration loader for the news monitoring project."""

import yaml
import os
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load and manage configuration from YAML files."""

    def __init__(self, config_path: str = None):
        """Initialize the config loader.

        Args:
            config_path: Path to the config file. If None, uses default location.
        """
        if config_path is None:
            # Default to config/config.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"

        self.config_path = Path(config_path)
        self._config = None

    def load(self) -> Dict[str, Any]:
        """Load the configuration file.

        Returns:
            Dictionary containing the configuration.
        """
        if self._config is None:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.

        Args:
            key: Dot-notation key (e.g., 'aws.region')
            default: Default value if key not found

        Returns:
            The configuration value or default.
        """
        config = self.load()
        keys = key.split('.')
        value = config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_table_config(self, table_name: str) -> Dict[str, str]:
        """Get Delta table configuration.

        Args:
            table_name: Name of the table configuration to retrieve

        Returns:
            Dictionary with table configuration
        """
        tables = self.get('tables.tables', {})
        return tables.get(table_name, {})


# Singleton instance
_config_loader = None


def get_config_loader() -> ConfigLoader:
    """Get the singleton config loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
