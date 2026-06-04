"""
Abstract base class for blockchain implementations
Provides interface for key generation and balance checking across all blockchains
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
import logging


class BaseBlockchain(ABC):
    """Abstract base class for blockchain implementations"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        """
        Initialize blockchain handler
        
        Args:
            config: Blockchain-specific configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate_key(self) -> Dict[str, str]:
        """
        Generate a random private key and derive address
        
        Returns:
            Dictionary containing:
                - address: Public address
                - private_key_hex: Private key in hex format
                - public_key: Public key
                - [additional blockchain-specific fields]
        """
        pass
    
    @abstractmethod
    def check_balance(self, address: str) -> Optional[float]:
        """
        Check native token balance for address
        
        Args:
            address: Public address to check
            
        Returns:
            Balance in native token units or None if check fails
        """
        pass
    
    @abstractmethod
    def check_token_balance(self, address: str, token_address: str, decimals: int = 18) -> Optional[float]:
        """
        Check token balance for address on this blockchain
        
        Args:
            address: Public address to check
            token_address: Token contract address
            decimals: Token decimal places
            
        Returns:
            Token balance or None if check fails
        """
        pass
    
    def validate_address(self, address: str) -> bool:
        """
        Validate address format for this blockchain
        
        Args:
            address: Address to validate
            
        Returns:
            True if valid format, False otherwise
        """
        return True  # Override in subclasses
    
    def get_explorer_url(self, address: str) -> str:
        """Get blockchain explorer URL for address"""
        return ""  # Override in subclasses
