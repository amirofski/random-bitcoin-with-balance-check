"""
Ripple (XRP) blockchain implementation
Supports XRP address generation and balance checking
"""

import secrets
from typing import Dict, Optional
import logging
import requests
from .base_blockchain import BaseBlockchain


class RippleBlockchain(BaseBlockchain):
    """Ripple (XRP) blockchain handler"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        super().__init__(config, logger)
        self.blockchain_name = 'ripple'
        try:
            from ripple_lib import wallet as xrpl_wallet
            self.xrpl_wallet = xrpl_wallet
        except ImportError:
            self.logger.warning("ripple-lib not installed. XRP key generation will use fallback method.")
            self.xrpl_wallet = None
    
    def generate_key(self) -> Dict[str, str]:
        """Generate Ripple account with public and private keys"""
        try:
            if self.xrpl_wallet:
                wallet = self.xrpl_wallet.generate_classic_address()
                return {
                    'address': wallet.classic_address,
                    'private_key_hex': wallet.private_key,
                    'public_key': wallet.public_key,
                    'seed': wallet.seed
                }
        except Exception as e:
            self.logger.debug(f"XRP key generation failed: {e}")
        
        # Fallback: Generate using random entropy (simplified)
        entropy = secrets.token_hex(32)
        # In production, use proper XRP key derivation
        return {
            'address': f"r{secrets.token_hex(20)}",  # Placeholder
            'private_key_hex': entropy,
            'public_key': secrets.token_hex(33),
            'seed': f"s{secrets.token_hex(16)}"
        }
    
    def check_balance(self, address: str) -> Optional[float]:
        """Check XRP balance using Ripple API"""
        endpoints = self.config.get('endpoints', [])
        timeout = self.config.get('timeout', 10)
        
        for endpoint in endpoints:
            try:
                if 'xrpscan.com' in endpoint or 'rippled' in endpoint:
                    response = requests.get(
                        f"{endpoint}{address}",
                        timeout=timeout
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if 'account_data' in data:
                            balance_drops = int(data['account_data'].get('Balance', 0))
                            return balance_drops / 1e6  # Convert drops to XRP
                
                # Alternative: XRPL WebSocket or HTTP-RPC
                payload = {
                    "method": "account_info",
                    "params": [{"account": address}]
                }
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=timeout
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data and 'account_data' in data['result']:
                        balance_drops = int(data['result']['account_data'].get('Balance', 0))
                        return balance_drops / 1e6
            
            except Exception as e:
                self.logger.debug(f"XRP balance check failed on {endpoint}: {e}")
        
        return None
    
    def check_token_balance(self, address: str, token_address: str, decimals: int = 6) -> Optional[float]:
        """
        Check balance of issued currency (IOU) on Ripple
        
        Args:
            address: XRP address
            token_address: Token issuer address
            decimals: Token decimals (typically 6 for most XRP tokens)
        """
        endpoints = self.config.get('endpoints', [])
        timeout = self.config.get('timeout', 10)
        
        for endpoint in endpoints:
            try:
                payload = {
                    "method": "account_lines",
                    "params": [{"account": address, "peer": token_address}]
                }
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'result' in data and 'lines' in data['result']:
                        for line in data['result']['lines']:
                            if line.get('account') == token_address:
                                balance = float(line.get('balance', 0))
                                return balance / (10 ** decimals)
            
            except Exception as e:
                self.logger.debug(f"XRP token balance check failed: {e}")
        
        return None
    
    def validate_address(self, address: str) -> bool:
        """Validate Ripple address format"""
        # Ripple addresses start with 'r' and are base58 encoded
        return isinstance(address, str) and address.startswith('r') and len(address) >= 25
    
    def get_explorer_url(self, address: str) -> str:
        """Get Ripple explorer URL"""
        return f"https://xrpscan.com/account/{address}"
