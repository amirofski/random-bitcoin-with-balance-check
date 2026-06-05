"""
Blockchains package - Initialization and registry
"""

from .base_blockchain import BaseBlockchain
from .ripple_blockchain import RippleBlockchain
from .cardano_blockchain import CardanoBlockchain
from .polkadot_blockchain import PolkadotBlockchain
from .cosmos_blockchain import CosmosBlockchain
from .avalanche_blockchain import AvalancheBlockchain
from .polygon_blockchain import PolygonBlockchain
from .bsc_blockchain import BSCBlockchain

__all__ = [
    'BaseBlockchain',
    'RippleBlockchain',
    'CardanoBlockchain',
    'PolkadotBlockchain',
    'CosmosBlockchain',
    'AvalancheBlockchain',
    'PolygonBlockchain',
    'BSCBlockchain',
]

# Registry of blockchain handlers
BLOCKCHAIN_REGISTRY = {
    'ripple': RippleBlockchain,
    'xrp': RippleBlockchain,
    'cardano': CardanoBlockchain,
    'ada': CardanoBlockchain,
    'polkadot': PolkadotBlockchain,
    'dot': PolkadotBlockchain,
    'cosmos': CosmosBlockchain,
    'atom': CosmosBlockchain,
    'avalanche': AvalancheBlockchain,
    'avax': AvalancheBlockchain,
    'polygon': PolygonBlockchain,
    'matic': PolygonBlockchain,
    'bsc': BSCBlockchain,
    'binance': BSCBlockchain,
}


def get_blockchain_handler(blockchain_name: str, config: dict, logger):
    """
    Factory function to get blockchain handler
    
    Args:
        blockchain_name: Name of blockchain
        config: Blockchain configuration
        logger: Logger instance
        
    Returns:
        Blockchain handler instance
    """
    handler_class = BLOCKCHAIN_REGISTRY.get(blockchain_name.lower())
    if handler_class is None:
        raise ValueError(f"Unknown blockchain: {blockchain_name}")
    
    return handler_class(config, logger)
