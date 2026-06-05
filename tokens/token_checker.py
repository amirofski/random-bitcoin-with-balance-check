"""
Unified Token Checker
Manages token balance checking across multiple blockchains and token types
"""

from typing import Dict, Optional, List, Any
import logging
from tokens.erc20_checker import ERC20TokenChecker
from tokens.spl_checker import SPLTokenChecker
from tokens.bep20_checker import BEP20TokenChecker


class UnifiedTokenChecker:
    """Unified interface for checking token balances across blockchains"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.erc20_checker = ERC20TokenChecker(logger)
        self.spl_checker = SPLTokenChecker(logger)
        self.bep20_checker = BEP20TokenChecker(logger)
    
    def check_token_balance(self, blockchain: str, address: str, token_contract: str, 
                           endpoint: str, decimals: int = 18, timeout: int = 10) -> Optional[float]:
        """
        Check token balance on specified blockchain
        
        Args:
            blockchain: 'ethereum', 'polygon', 'avalanche', 'bsc', 'solana'
            address: Wallet address
            token_contract: Token contract/mint address
            endpoint: RPC endpoint URL
            decimals: Token decimals
            timeout: Request timeout
            
        Returns:
            Token balance or None if check fails
        """
        blockchain = blockchain.lower()
        
        try:
            if blockchain in ['ethereum', 'polygon', 'avalanche']:
                # ERC-20 compatible
                balance_raw = self.erc20_checker.check_balance(address, token_contract, endpoint, timeout)
                if balance_raw is not None:
                    return balance_raw / (10 ** decimals)
            
            elif blockchain == 'bsc':
                # BEP-20 (compatible with ERC-20)
                balance_raw = self.bep20_checker.check_balance(address, token_contract, endpoint, timeout)
                if balance_raw is not None:
                    return balance_raw / (10 ** decimals)
            
            elif blockchain == 'solana':
                # SPL token
                return self.spl_checker.check_token_balance(address, token_contract, endpoint, timeout)
            
            else:
                self.logger.warning(f"Unknown blockchain: {blockchain}")
        
        except Exception as e:
            self.logger.debug(f"Failed to check {blockchain} token balance: {e}")
        
        return None
    
    def check_native_balance(self, blockchain: str, address: str, endpoint: str, 
                            timeout: int = 10) -> Optional[float]:
        """
        Check native token balance
        
        Args:
            blockchain: Blockchain name
            address: Wallet address
            endpoint: RPC endpoint
            timeout: Request timeout
            
        Returns:
            Balance in native token or None
        """
        blockchain = blockchain.lower()
        
        try:
            if blockchain == 'solana':
                return self.spl_checker.check_balance(address, endpoint, timeout)
            
            # For EVM chains, use standard eth_getBalance
            elif blockchain in ['ethereum', 'polygon', 'avalanche', 'bsc']:
                import requests
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_getBalance",
                    "params": [address, "latest"],
                    "id": 1,
                }
                response = requests.post(endpoint, json=payload, timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        balance_wei = int(data['result'], 16)
                        return balance_wei / 1e18
        
        except Exception as e:
            self.logger.debug(f"Failed to check {blockchain} native balance: {e}")
        
        return None
    
    def check_multiple_tokens(self, blockchain: str, address: str, tokens: List[Dict[str, Any]], 
                             endpoint: str, timeout: int = 10) -> Dict[str, Optional[float]]:
        """
        Check balances for multiple tokens on a blockchain
        
        Args:
            blockchain: Blockchain name
            address: Wallet address
            tokens: List of token configurations
            endpoint: RPC endpoint
            timeout: Request timeout
            
        Returns:
            Dictionary mapping token identifiers to balances
        """
        blockchain = blockchain.lower()
        
        try:
            if blockchain in ['ethereum', 'polygon', 'avalanche']:
                return self.erc20_checker.check_multiple_tokens(address, tokens, endpoint, timeout)
            
            elif blockchain == 'bsc':
                return self.bep20_checker.check_multiple_tokens(address, tokens, endpoint, timeout)
            
            elif blockchain == 'solana':
                mint_addresses = [t.get('address') for t in tokens]
                return self.spl_checker.check_multiple_token_balances(address, mint_addresses, 
                                                                      endpoint, timeout)
        
        except Exception as e:
            self.logger.debug(f"Failed to check multiple {blockchain} token balances: {e}")
        
        return {}
    
    def get_token_info(self, blockchain: str, token_contract: str, endpoint: str, 
                      timeout: int = 10) -> Dict[str, Any]:
        """
        Get token metadata
        
        Args:
            blockchain: Blockchain name
            token_contract: Token address/mint
            endpoint: RPC endpoint
            timeout: Request timeout
            
        Returns:
            Token metadata dictionary
        """
        blockchain = blockchain.lower()
        
        try:
            if blockchain in ['ethereum', 'polygon', 'avalanche']:
                return self.erc20_checker.get_token_info(token_contract, endpoint, timeout)
            
            elif blockchain == 'bsc':
                return self.bep20_checker.get_token_info(token_contract, endpoint, timeout)
            
            elif blockchain == 'solana':
                return self.spl_checker.get_token_info(token_contract, endpoint, timeout)
        
        except Exception as e:
            self.logger.debug(f"Failed to get {blockchain} token info: {e}")
        
        return {}
    
    def validate_address(self, blockchain: str, address: str) -> bool:
        """Validate address format for blockchain"""
        blockchain = blockchain.lower()
        
        try:
            if blockchain in ['ethereum', 'polygon', 'avalanche', 'bsc']:
                return isinstance(address, str) and address.startswith('0x') and len(address) == 42
            
            elif blockchain == 'solana':
                return isinstance(address, str) and len(address) == 44
        
        except Exception as e:
            self.logger.debug(f"Address validation failed: {e}")
        
        return False
