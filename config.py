import json
import logging
from typing import Dict
import os


class ConfigLoader:
    """Load and validate configuration from JSON file"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.config = None
        self.logger = logging.getLogger(__name__)
    
    def load(self) -> Dict:
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            
            self._validate_config()
            return self.config
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {str(e)}")
    
    def _validate_config(self):
        """Validate configuration structure"""
        required_keys = ['general', 'blockchains']
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config section: {key}")
        
        # Validate at least one blockchain is enabled
        enabled_blockchains = [
            bc for bc, cfg in self.config['blockchains'].items()
            if cfg.get('enabled', False)
        ]
        
        if not enabled_blockchains:
            raise ValueError("At least one blockchain must be enabled in config")
        
        self.logger.info(f"Configuration valid. Enabled blockchains: {enabled_blockchains}")
    
    def get_enabled_blockchains(self) -> list:
        """Get list of enabled blockchains"""
        return [
            bc for bc, cfg in self.config['blockchains'].items()
            if cfg.get('enabled', False)
        ]
    
    def get_blockchain_config(self, blockchain: str) -> Dict:
        """Get configuration for specific blockchain"""
        if blockchain not in self.config['blockchains']:
            raise ValueError(f"Unknown blockchain: {blockchain}")
        
        return self.config['blockchains'][blockchain]
