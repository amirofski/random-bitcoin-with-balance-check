"""
BEP-20 Token balance checker for Binance Smart Chain
BEP-20 tokens are functionally equivalent to ERC-20 on BSC
"""

from typing import Dict, Optional, List
import logging
import requests


class BEP20TokenChecker:
    """Check BEP-20 token balances on Binance Smart Chain"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        # BEP-20 standard function selectors (same as ERC-20)
        self.balance_of_selector = "0x70a08231"  # balanceOf(address)
        self.total_supply_selector = "0x18160ddd"  # totalSupply()
        self.decimals_selector = "0x313ce567"  # decimals()
        self.symbol_selector = "0x95d89b41"  # symbol()
        self.name_selector = "0x06fdde03"  # name()
    
    def check_balance(self, address: str, token_contract: str, endpoint: str, timeout: int = 10) -> Optional[float]:
        """
        Check BEP-20 token balance on BSC
        
        Args:
            address: BSC wallet address
            token_contract: BEP-20 token contract address
            endpoint: BSC RPC endpoint URL
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
            self.logger.debug(f"BEP-20 balance check failed: {e}")
        
        return None
    
    def get_decimals(self, token_contract: str, endpoint: str, timeout: int = 10) -> int:
        """Get BEP-20 token decimals"""
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
            self.logger.debug(f"Failed to get BEP-20 token decimals: {e}")
        
        return 18  # Default to 18 decimals
    
    def get_total_supply(self, token_contract: str, endpoint: str, timeout: int = 10) -> Optional[float]:
        """Get total supply of BEP-20 token"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_call",
                "params": [
                    {
                        "to": token_contract,
                        "data": self.total_supply_selector
                    },
                    "latest"
                ],
                "id": 1,
            }
            
            response = requests.post(endpoint, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and data['result'] != '0x':
                    supply_raw = int(data['result'], 16)
                    decimals = self.get_decimals(token_contract, endpoint, timeout)
                    return supply_raw / (10 ** decimals)
        
        except Exception as e:
            self.logger.debug(f"Failed to get BEP-20 total supply: {e}")
        
        return None
    
    def get_token_info(self, token_contract: str, endpoint: str, timeout: int = 10) -> Dict[str, any]:
        """Get BEP-20 token metadata (name, symbol, decimals)"""
        info = {
            'address': token_contract,
            'decimals': 18
        }
        
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
                if 'result' in data and data['result'] != '0x':
                    info['name'] = data['result']
            
            # Get symbol
            payload['params'][0]['data'] = self.symbol_selector
            response = requests.post(endpoint, json=payload, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and data['result'] != '0x':
                    info['symbol'] = data['result']
            
            # Get decimals
            info['decimals'] = self.get_decimals(token_contract, endpoint, timeout)
        
        except Exception as e:
            self.logger.debug(f"Failed to get BEP-20 token info: {e}")
        
        return info
    
    def check_multiple_tokens(self, address: str, tokens: List[Dict[str, any]], endpoint: str,
                             timeout: int = 10) -> Dict[str, Optional[float]]:
        """
        Check balances for multiple BEP-20 tokens
        
        Args:
            address: BSC wallet address
            tokens: List of token configs with 'address' and optional 'decimals'
            endpoint: BSC RPC endpoint
            timeout: Request timeout
            
        Returns:
            Dictionary mapping token addresses to balances
        """
        results = {}
        
        for token in tokens:
            token_addr = token.get('address')
            decimals = token.get('decimals')
            
            # Get decimals if not provided
            if decimals is None:
                decimals = self.get_decimals(token_addr, endpoint, timeout)
            
            balance_raw = self.check_balance(address, token_addr, endpoint, timeout)
            
            if balance_raw is not None:
                balance = balance_raw / (10 ** decimals)
                results[token_addr] = balance
            else:
                results[token_addr] = None
        
        return results
    
    def check_bnb_and_tokens(self, address: str, token_configs: List[Dict[str, any]], 
                            endpoint: str, timeout: int = 10) -> Dict[str, Optional[float]]:
        """
        Check both BNB native balance and multiple BEP-20 tokens
        
        Args:
            address: BSC wallet address
            token_configs: List of BEP-20 token configurations
            endpoint: BSC RPC endpoint
            timeout: Request timeout
            
        Returns:
            Dictionary with 'bnb' and token addresses as keys
        """
        results = {}
        
        try:
            # Get BNB balance
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
                    bnb_wei = int(data['result'], 16)
                    results['bnb'] = bnb_wei / 1e18
        
        except Exception as e:
            self.logger.debug(f"Failed to check BNB balance: {e}")
            results['bnb'] = None
        
        # Get token balances
        token_balances = self.check_multiple_tokens(address, token_configs, endpoint, timeout)
        results.update(token_balances)
        
        return results
