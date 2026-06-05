"""
ERC-20 Token balance checker for Ethereum and EVM-compatible chains
Supports Polygon, Avalanche, BSC, and other EVM networks
"""

from typing import Dict, Optional, List
import logging
import requests


class ERC20TokenChecker:
    """Check ERC-20 token balances on EVM chains"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        # ERC-20 standard function selectors
        self.balance_of_selector = "0x70a08231"  # balanceOf(address)
        self.total_supply_selector = "0x18160ddd"  # totalSupply()
        self.decimals_selector = "0x313ce567"  # decimals()
        self.symbol_selector = "0x95d89b41"  # symbol()
        self.name_selector = "0x06fdde03"  # name()
    
    def check_balance(self, address: str, token_contract: str, endpoint: str, timeout: int = 10) -> Optional[float]:
        """
        Check ERC-20 token balance
        
        Args:
            address: Wallet address
            token_contract: Token contract address
            endpoint: RPC endpoint URL
            timeout: Request timeout in seconds
            
        Returns:
            Token balance or None if check fails
        """
        try:
            # Pad address to 64 hex characters for function parameter
            padded_address = address.lower().replace('0x', '').zfill(64)
            
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [
                    {
                        "to": token_contract,
                        "data": f"{self.balance_of_selector}{padded_address}"
                    },
                    "latest"
                ],
                "id": 1,
            }
            
            response = requests.post(endpoint, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and data['result'] != '0x':
                    balance_raw = int(data['result'], 16)
                    return balance_raw
            
        except Exception as e:
            self.logger.debug(f"ERC-20 balance check failed: {e}")
        
        return None
    
    def get_decimals(self, token_contract: str, endpoint: str, timeout: int = 10) -> int:
        """Get token decimals"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [
                    {
                        "to": token_contract,
                        "data": self.decimals_selector
                    },
                    "latest"
                ],
                "id": 1,
            }
            
            response = requests.post(endpoint, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    return int(data['result'], 16)
        
        except Exception as e:
            self.logger.debug(f"Failed to get token decimals: {e}")
        
        return 18  # Default to 18 decimals
    
    def get_token_info(self, token_contract: str, endpoint: str, timeout: int = 10) -> Dict[str, str]:
        """Get token name, symbol, and other metadata"""
        info = {}
        
        try:
            # Get name
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [
                    {
                        "to": token_contract,
                        "data": self.name_selector
                    },
                    "latest"
                ],
                "id": 1,
            }
            response = requests.post(endpoint, json=payload, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    # Decode string from hex
                    info['name'] = data['result']
            
            # Get symbol
            payload['params'][0]['data'] = self.symbol_selector
            response = requests.post(endpoint, json=payload, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    info['symbol'] = data['result']
        
        except Exception as e:
            self.logger.debug(f"Failed to get token info: {e}")
        
        return info
    
    def check_multiple_tokens(self, address: str, tokens: List[Dict[str, str]], endpoint: str, 
                             timeout: int = 10) -> Dict[str, Optional[float]]:
        """
        Check balances for multiple tokens
        
        Args:
            address: Wallet address
            tokens: List of token configs with 'address' and 'decimals'
            endpoint: RPC endpoint
            timeout: Request timeout
            
        Returns:
            Dictionary mapping token addresses to balances
        """
        results = {}
        
        for token in tokens:
            token_addr = token.get('address')
            decimals = token.get('decimals', 18)
            
            balance_raw = self.check_balance(address, token_addr, endpoint, timeout)
            
            if balance_raw is not None:
                balance = balance_raw / (10 ** decimals)
                results[token_addr] = balance
            else:
                results[token_addr] = None
        
        return results
