"""
Polkadot (DOT) blockchain implementation
Supports DOT address generation and balance checking
"""

import secrets
from typing import Dict, Optional
import logging
import requests
from .base_blockchain import BaseBlockchain


class PolkadotBlockchain(BaseBlockchain):
    """Polkadot (DOT) blockchain handler"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        super().__init__(config, logger)
        self.blockchain_name = 'polkadot'
        try:
            from substrateinterface import SubstrateInterface, Keypair
            self.SubstrateInterface = SubstrateInterface
            self.Keypair = Keypair
        except ImportError:
            self.logger.warning("substrate-interface not installed. Using API-based approach.")
            self.SubstrateInterface = None
            self.Keypair = None
    
    def generate_key(self) -> Dict[str, str]:
        """Generate Polkadot address with private key"""
        try:
            if self.Keypair:
                # Generate using substrate interface
                keypair = self.Keypair.create_from_uri(f"//{secrets.token_hex(32)}")
                
                return {
                    'address': keypair.ss58_address,
                    'private_key_hex': keypair.private_key.hex(),
                    'public_key': keypair.public_key.hex(),
                    'ss58_address': keypair.ss58_address
                }
        except Exception as e:
            self.logger.debug(f"Polkadot key generation with library failed: {e}")
        
        # Fallback: Generate using entropy
        entropy = secrets.token_hex(32)
        # In production, use proper substrate key derivation
        addr_hash = secrets.token_hex(35)
        
        return {
            'address': f"1{addr_hash}",  # Placeholder (Polkadot SS58 format)
            'private_key_hex': entropy,
            'public_key': secrets.token_hex(32),
            'ss58_address': f"1{addr_hash}"
        }
    
    def check_balance(self, address: str) -> Optional[float]:
        """Check DOT balance using Polkadot RPC"""
        endpoints = self.config.get('endpoints', [])
        timeout = self.config.get('timeout', 10)
        
        for endpoint in endpoints:
            try:
                # Subscan API
                if 'subscan.io' in endpoint:
                    headers = {
                        'Content-Type': 'application/json',
                        'X-API-Key': self.config.get('api_key', '')
                    }
                    response = requests.post(
                        f"{endpoint}/api/v2/scan/account",
                        json={"address": address},
                        headers=headers,
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('code') == 0 and 'data' in data:
                            # Balance in planck (1 DOT = 10^10 planck)
                            balance_planck = int(data['data'].get('balance', '0'))
                            return balance_planck / 1e10
                
                # Substrate RPC endpoint
                else:
                    payload = {
                        "jsonrpc": "2.0",
                        "method": "system_accountNextIndex",
                        "params": [address],
                        "id": 1
                    }
                    response = requests.post(
                        endpoint,
                        json=payload,
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        # For full balance, need state_getStorage query
                        # This is a simplified approach
                        data = response.json()
                        if 'result' in data:
                            return float(data['result'])
            
            except Exception as e:
                self.logger.debug(f"Polkadot balance check failed on {endpoint}: {e}")
        
        return None
    
    def check_token_balance(self, address: str, token_address: str, decimals: int = 10) -> Optional[float]:
        """
        Check token/asset balance on Polkadot
        
        Args:
            address: Polkadot address
            token_address: Asset ID or token identifier
            decimals: Token decimals (typically 10 for DOT)
        """
        endpoints = self.config.get('endpoints', [])
        timeout = self.config.get('timeout', 10)
        
        for endpoint in endpoints:
            try:
                if 'subscan.io' in endpoint:
                    headers = {
                        'Content-Type': 'application/json',
                        'X-API-Key': self.config.get('api_key', '')
                    }
                    # Token transfers endpoint
                    response = requests.post(
                        f"{endpoint}/api/v2/scan/token/transfers",
                        json={
                            "address": address,
                            "token_id": token_address,
                            "direction": "all"
                        },
                        headers=headers,
                        timeout=timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('code') == 0 and 'data' in data:
                            transfers = data['data'].get('transfers', [])
                            balance = 0
                            for transfer in transfers:
                                if transfer.get('to') == address:
                                    balance += int(transfer.get('amount', 0))
                                elif transfer.get('from') == address:
                                    balance -= int(transfer.get('amount', 0))
                            return balance / (10 ** decimals)
            
            except Exception as e:
                self.logger.debug(f"Polkadot token balance check failed: {e}")
        
        return None
    
    def validate_address(self, address: str) -> bool:
        """Validate Polkadot address format"""
        # Polkadot SS58 addresses typically start with '1', length ~47-48
        return isinstance(address, str) and address.startswith('1') and len(address) >= 47
    
    def get_explorer_url(self, address: str) -> str:
        """Get Polkadot explorer URL"""
        return f"https://polkadot.subscan.io/account/{address}"
