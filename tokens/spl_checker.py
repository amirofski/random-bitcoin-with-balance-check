"""
SPL Token balance checker for Solana blockchain
Supports checking balances of SPL (Solana Program Library) tokens
"""

from typing import Dict, Optional, List
import logging
import requests


class SPLTokenChecker:
    """Check SPL token balances on Solana"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def check_balance(self, wallet_address: str, endpoint: str, timeout: int = 10) -> Optional[float]:
        """
        Check SOL balance for Solana wallet
        
        Args:
            wallet_address: Solana wallet address
            endpoint: Solana RPC endpoint
            timeout: Request timeout in seconds
            
        Returns:
            SOL balance or None if check fails
        """
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "getBalance",
                "params": [wallet_address],
                "id": 1
            }
            
            response = requests.post(endpoint, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    balance_lamports = data['result'].get('value', 0)
                    return balance_lamports / 1e9  # Convert lamports to SOL
        
        except Exception as e:
            self.logger.debug(f"Solana balance check failed: {e}")
        
        return None
    
    def check_token_balance(self, wallet_address: str, mint_address: str, endpoint: str, 
                           timeout: int = 10) -> Optional[float]:
        """
        Check SPL token balance
        
        Args:
            wallet_address: Solana wallet address
            mint_address: SPL token mint address
            endpoint: Solana RPC endpoint
            timeout: Request timeout
            
        Returns:
            Token balance or None if check fails
        """
        try:
            # First, get token accounts for this wallet and mint
            payload = {
                "jsonrpc": "2.0",
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet_address,
                    {"mint": mint_address},
                    {"encoding": "jsonParsed"}
                ],
                "id": 1
            }
            
            response = requests.post(endpoint, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'value' in data['result']:
                    accounts = data['result']['value']
                    
                    if accounts and len(accounts) > 0:
                        # Get the balance from the token account
                        account = accounts[0]
                        if 'account' in account and 'data' in account['account']:
                            parsed = account['account']['data'].get('parsed', {})
                            info = parsed.get('info', {})
                            
                            # Get token amount and decimals
                            token_amount = info.get('tokenAmount', {})
                            balance = float(token_amount.get('uiAmount', 0))
                            return balance
        
        except Exception as e:
            self.logger.debug(f"SPL token balance check failed: {e}")
        
        return None
    
    def get_token_info(self, mint_address: str, endpoint: str, timeout: int = 10) -> Dict[str, any]:
        """Get SPL token metadata"""
        info = {}
        
        try:
            # Get mint account info
            payload = {
                "jsonrpc": "2.0",
                "method": "getMint",
                "params": [mint_address],
                "id": 1
            }
            
            response = requests.post(endpoint, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data:
                    mint_info = data['result']
                    info['supply'] = mint_info.get('supply', 0)
                    info['decimals'] = mint_info.get('decimals', 0)
                    info['owner'] = mint_info.get('owner', '')
        
        except Exception as e:
            self.logger.debug(f"Failed to get SPL token info: {e}")
        
        return info
    
    def check_multiple_token_balances(self, wallet_address: str, mint_addresses: List[str], 
                                     endpoint: str, timeout: int = 10) -> Dict[str, Optional[float]]:
        """
        Check balances for multiple SPL tokens
        
        Args:
            wallet_address: Solana wallet address
            mint_addresses: List of token mint addresses
            endpoint: Solana RPC endpoint
            timeout: Request timeout
            
        Returns:
            Dictionary mapping mint addresses to balances
        """
        results = {}
        
        try:
            # Get all token accounts for the wallet
            payload = {
                "jsonrpc": "2.0",
                "method": "getTokenAccountsByOwner",
                "params": [
                    wallet_address,
                    {"programId": "TokenkegQfeZyiNwAJsyFbPVwwQQftsLmDaY5TB2ND6"},
                    {"encoding": "jsonParsed"}
                ],
                "id": 1
            }
            
            response = requests.post(endpoint, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and 'value' in data['result']:
                    accounts = data['result']['value']
                    
                    # Build lookup of mint -> balance
                    for account in accounts:
                        if 'account' in account and 'data' in account['account']:
                            parsed = account['account']['data'].get('parsed', {})
                            info = parsed.get('info', {})
                            mint = info.get('mint', '')
                            
                            if mint in mint_addresses:
                                token_amount = info.get('tokenAmount', {})
                                balance = float(token_amount.get('uiAmount', 0))
                                results[mint] = balance
                
                # Add None for any missing mints
                for mint in mint_addresses:
                    if mint not in results:
                        results[mint] = None
        
        except Exception as e:
            self.logger.debug(f"Failed to check multiple SPL token balances: {e}")
            # Return None for all if request fails
            for mint in mint_addresses:
                results[mint] = None
        
        return results
