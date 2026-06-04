import requests
import time
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class BlockchainScanner:
    """Check balances and transaction history across multiple blockchains"""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.metrics = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'total_time': 0
        }
    
    def check_bitcoin_balance(self, address: str, endpoint: str) -> Optional[float]:
        """Check Bitcoin address balance"""
        try:
            timeout = self.config['blockchains']['bitcoin']['timeout']
            
            if 'blockchain.info' in endpoint:
                url = f"{endpoint}{address}"
                response = self.session.get(url, timeout=timeout)
                balance_satoshi = int(response.text)
                return balance_satoshi / 1e8  # Convert to BTC
            
            elif 'blockstream.info' in endpoint:
                url = f"{endpoint}{address}"
                response = self.session.get(url, timeout=timeout)
                data = response.json()
                return data['chain_stats']['funded_txo_sum'] / 1e8
            
        except Exception as e:
            self.logger.debug(f"Bitcoin check failed: {str(e)}")
            return None
        
        return None
    
    def check_ethereum_balance(self, address: str, endpoint: str) -> Optional[float]:
        """Check Ethereum address balance"""
        try:
            timeout = self.config['blockchains']['ethereum']['timeout']
            
            # Using web3.py would be better, but requests for simplicity
            if 'infura.io' in endpoint:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "eth_getBalance",
                    "params": [address, "latest"],
                    "id": 1,
                }
                response = self.session.post(endpoint, json=payload, timeout=timeout)
                data = response.json()
                
                if 'result' in data:
                    balance_wei = int(data['result'], 16)
                    return balance_wei / 1e18  # Convert to ETH
            
        except Exception as e:
            self.logger.debug(f"Ethereum check failed: {str(e)}")
            return None
        
        return None
    
    def check_solana_balance(self, address: str, endpoint: str) -> Optional[float]:
        """Check Solana address balance"""
        try:
            timeout = self.config['blockchains']['solana']['timeout']
            
            payload = {
                "jsonrpc": "2.0",
                "method": "getBalance",
                "params": [address],
                "id": 1,
            }
            response = self.session.post(endpoint, json=payload, timeout=timeout)
            data = response.json()
            
            if 'result' in data:
                balance_lamports = data['result']['value']
                return balance_lamports / 1e9  # Convert to SOL
        
        except Exception as e:
            self.logger.debug(f"Solana check failed: {str(e)}")
            return None
        
        return None
    
    def check_address_transactions(self, blockchain: str, address: str) -> bool:
        """Check if address has any transaction history"""
        endpoints = self.config['blockchains'][blockchain].get('endpoints', [])
        
        for endpoint in endpoints:
            try:
                if blockchain == 'bitcoin':
                    balance = self.check_bitcoin_balance(address, endpoint)
                elif blockchain == 'ethereum':
                    balance = self.check_ethereum_balance(address, endpoint)
                elif blockchain == 'solana':
                    balance = self.check_solana_balance(address, endpoint)
                
                if balance is not None and balance > 0:
                    return True
            
            except Exception as e:
                self.logger.debug(f"Transaction check failed for {blockchain}: {str(e)}")
        
        return False
    
    def scan_address(self, keys: Dict) -> Dict[str, any]:
        """Scan address across all enabled blockchains"""
        start_time = time.time()
        results = {
            'timestamp': datetime.now().isoformat(),
            'found': False,
            'details': {}
        }
        
        for blockchain, config in self.config['blockchains'].items():
            if not config['enabled']:
                continue
            
            try:
                if blockchain == 'bitcoin' and 'address' in keys.get('bitcoin', {}):
                    address = keys['bitcoin']['address']
                    has_activity = self.check_address_transactions(blockchain, address)
                    results['details'][blockchain] = {
                        'address': address,
                        'has_activity': has_activity
                    }
                    if has_activity:
                        results['found'] = True
                
                elif blockchain == 'ethereum' and 'address' in keys.get('ethereum', {}):
                    address = keys['ethereum']['address']
                    has_activity = self.check_address_transactions(blockchain, address)
                    results['details'][blockchain] = {
                        'address': address,
                        'has_activity': has_activity
                    }
                    if has_activity:
                        results['found'] = True
                
                elif blockchain == 'solana' and 'address' in keys.get('solana', {}):
                    address = keys['solana']['address']
                    has_activity = self.check_address_transactions(blockchain, address)
                    results['details'][blockchain] = {
                        'address': address,
                        'has_activity': has_activity
                    }
                    if has_activity:
                        results['found'] = True
            
            except Exception as e:
                self.logger.error(f"Error scanning {blockchain}: {str(e)}")
        
        results['scan_time'] = time.time() - start_time
        self.metrics['total_time'] += results['scan_time']
        self.metrics['total_checks'] += 1
        
        return results
