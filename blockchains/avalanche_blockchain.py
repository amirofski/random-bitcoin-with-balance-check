"""
Avalanche (AVAX) blockchain implementation
Supports AVAX address generation and balance checking
"""

import secrets
from typing import Dict, Optional
import logging
import requests
from eth_keys import keys as eth_keys
from .base_blockchain import BaseBlockchain


class AvalancheBlockchain(BaseBlockchain):
    """Avalanche (AVAX) blockchain handler - EVM compatible"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        super().__init__(config, logger)
        self.blockchain_name = 'avalanche'
        self.chain_id = config.get('chain_id', 43114)  # Avalanche C-Chain mainnet
    
    def generate_key(self) -> Dict[str, str]:
        """Generate Avalanche address (same as Ethereum, different chain)"""
        private_key = secrets.randbelow(2**256 - 1) + 1
        eth_key = eth_keys.PrivateKey(private_key.to_bytes(32, 'big'))
        
        address = eth_key.public_key.to_checksum_address()
        
        return {
            'address': address,
            'private_key_hex': '0x' + private_key.to_bytes(32, 'big').hex(),
            'public_key': '0x' + eth_key.public_key.to_hex(),
            'chain_id': self.chain_id
        }
    
    def check_balance(self, address: str) -> Optional[float]:
        """Check AVAX balance using Avalanche RPC"""
        endpoints = self.config.get('endpoints', [])
        timeout = self.config.get('timeout', 10)
        
        for endpoint in endpoints:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_getBalance",
                    "params": [address, "latest"],
                    "id": 1,
                }
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        balance_wei = int(data['result'], 16)
                        return balance_wei / 1e18  # Convert wei to AVAX
            
            except Exception as e:
                self.logger.debug(f"Avalanche balance check failed on {endpoint}: {e}")
        
        return None
    
    def check_token_balance(self, address: str, token_address: str, decimals: int = 18) -> Optional[float]:
        """
        Check ERC-20 token balance on Avalanche
        
        Args:
            address: Avalanche address
            token_address: ERC-20 token contract address
            decimals: Token decimals
        """
        endpoints = self.config.get('endpoints', [])
        timeout = self.config.get('timeout', 10)
        
        # ERC-20 balanceOf function selector (0x70a08231)
        function_selector = "0x70a08231"
        # Pad address to 64 hex characters
        padded_address = address.lower().replace('0x', '').zfill(64)
        
        for endpoint in endpoints:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_call",
                    "params": [
                        {
                            "to": token_address,
                            "data": f"{function_selector}{padded_address}"
                        },
                        "latest"
                    ],
                    "id": 1,
                }
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data:
                        balance_raw = int(data['result'], 16)
                        return balance_raw / (10 ** decimals)
            
            except Exception as e:
                self.logger.debug(f"Avalanche token balance check failed: {e}")
        
        return None
    
    def validate_address(self, address: str) -> bool:
        """Validate Avalanche address format"""
        return isinstance(address, str) and address.startswith('0x') and len(address) == 42
    
    def get_explorer_url(self, address: str) -> str:
        """Get Avalanche explorer URL"""
        return f"https://snowtrace.io/address/{address}"
