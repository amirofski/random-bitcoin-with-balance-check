"""
Binance Smart Chain (BSC) blockchain implementation
Supports BNB address generation and balance checking (EVM compatible)
"""

import secrets
from typing import Dict, Optional
import logging
import requests
from eth_keys import keys as eth_keys
from .base_blockchain import BaseBlockchain


class BSCBlockchain(BaseBlockchain):
    """Binance Smart Chain (BSC) blockchain handler - EVM compatible"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        super().__init__(config, logger)
        self.blockchain_name = 'bsc'
        self.chain_id = config.get('chain_id', 56)  # BSC mainnet
    
    def generate_key(self) -> Dict[str, str]:
        """Generate BSC address (same as Ethereum, different chain)"""
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
        """Check BNB balance using BSC RPC"""
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
                        return balance_wei / 1e18  # Convert wei to BNB
            
            except Exception as e:
                self.logger.debug(f"BSC balance check failed on {endpoint}: {e}")
        
        return None
    
    def check_token_balance(self, address: str, token_address: str, decimals: int = 18) -> Optional[float]:
        """
        Check BEP-20 token balance on BSC
        
        Args:
            address: BSC address
            token_address: BEP-20 token contract address
            decimals: Token decimals
        """
        endpoints = self.config.get('endpoints', [])
        timeout = self.config.get('timeout', 10)
        
        # BEP-20 balanceOf function selector (0x70a08231 - same as ERC-20)
        function_selector = "0x70a08231"
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
                self.logger.debug(f"BSC token balance check failed: {e}")
        
        return None
    
    def validate_address(self, address: str) -> bool:
        """Validate BSC address format"""
        return isinstance(address, str) and address.startswith('0x') and len(address) == 42
    
    def get_explorer_url(self, address: str) -> str:
        """Get BSC explorer URL"""
        return f"https://bscscan.com/address/{address}"
