import secrets
from typing import Dict, Tuple
import hashlib
from eth_keys import keys as eth_keys
import bit


class KeyGenerator:
    """Generate private keys for multiple blockchains"""
    
    def __init__(self):
        self.btc_min = 1
        self.btc_max = 115792089237316195423570985008687907852837564279074904382605163141518161494337
    
    def generate_random_entropy(self, bits: int = 256) -> bytes:
        """Generate high-entropy random bytes"""
        return secrets.token_bytes(bits // 8)
    
    def generate_bitcoin_key(self) -> Tuple[str, str, str]:
        """Generate Bitcoin private key and address"""
        private_key_int = secrets.randbelow(self.btc_max) + 1
        key = bit.Key.from_int(private_key_int)
        
        return {
            'address': key.address,
            'private_key_hex': key.to_hex(),
            'private_key_wif': key.to_wif(),
            'public_key': key.public_key.hex()
        }
    
    def generate_ethereum_key(self) -> Dict[str, str]:
        """Generate Ethereum private key and address"""
        private_key = secrets.randbelow(2**256 - 1) + 1
        eth_key = eth_keys.PrivateKey(private_key.to_bytes(32, 'big'))
        
        return {
            'address': '0x' + eth_key.public_key.to_checksum_address().lower(),
            'private_key_hex': '0x' + private_key.to_bytes(32, 'big').hex(),
            'public_key': '0x' + eth_key.public_key.to_hex()
        }
    
    def generate_solana_key(self) -> Dict[str, str]:
        """Generate Solana private key and address"""
        from solders.keypair import Keypair
        
        keypair = Keypair()
        return {
            'address': str(keypair.pubkey()),
            'private_key_hex': keypair.secret().hex(),
            'public_key': str(keypair.pubkey())
        }
    
    def generate_all_keys(self) -> Dict[str, Dict[str, str]]:
        """Generate keys for all enabled blockchains"""
        entropy = self.generate_random_entropy()
        
        keys = {
            'bitcoin': self.generate_bitcoin_key(),
            'ethereum': self.generate_ethereum_key(),
            'solana': self.generate_solana_key(),
            'entropy': entropy.hex()
        }
        
        return keys
