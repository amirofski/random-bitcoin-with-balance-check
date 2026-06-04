#!/usr/bin/env python3
"""
Multi-Chain Random Key Generator with Balance Checker
Generates random private keys for multiple blockchains and checks for balances/transactions
"""

import time
import sys
import logging
from typing import Dict
from datetime import datetime

from config import ConfigLoader
from key_generator import KeyGenerator
from blockchain_scanner import BlockchainScanner
from logger import SuccessLogger
from dashboard import Dashboard


class MultiChainScanner:
    """Main scanner orchestrator"""
    
    def __init__(self, config_file: str = 'config.json'):
        # Load configuration
        config_loader = ConfigLoader(config_file)
        self.config = config_loader.load()
        
        # Setup logging
        success_logger = SuccessLogger(self.config)
        self.logger = success_logger.setup_logging()
        
        # Initialize components
        self.key_generator = KeyGenerator()
        self.scanner = BlockchainScanner(self.config, self.logger)
        self.dashboard = Dashboard(self.logger)
        self.success_logger = success_logger
        
        self.logger.info("MultiChainScanner initialized successfully")
    
    def run(self, max_iterations: int = None):
        """Main scanning loop"""
        try:
            self.dashboard.display_header()
            self.logger.info("Starting multi-chain key scanning...")
            
            iteration = 0
            
            while max_iterations is None or iteration < max_iterations:
                try:
                    # Generate random keys for all enabled blockchains
                    keys = self.key_generator.generate_all_keys()
                    
                    # Scan addresses across blockchains
                    scan_result = self.scanner.scan_address(keys)
                    
                    # Update dashboard
                    self.dashboard.update_metrics(scan_result)
                    
                    # If found key with activity
                    if scan_result.get('found'):
                        self.logger.warning("KEY WITH ACTIVITY FOUND!")
                        self.dashboard.display_found_key(keys, scan_result)
                        self.success_logger.log_found_key(keys, scan_result)
                    
                    # Display periodic status updates (every 100 scans)
                    if self.scanner.metrics['total_checks'] % 100 == 0:
                        self.dashboard.display_status()
                    
                    iteration += 1
                
                except KeyboardInterrupt:
                    self.logger.info("Scanning paused by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error during scan: {str(e)}", exc_info=True)
                    self.dashboard.display_error(str(e))
                    continue
            
            # Final status
            self.logger.info(f"Scanning completed. Total iterations: {iteration}")
            self.dashboard.display_status()
        
        except Exception as e:
            self.logger.critical(f"Critical error: {str(e)}", exc_info=True)
            sys.exit(1)


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Multi-Chain Random Key Generator with Balance Checker'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=None,
        help='Maximum number of iterations (default: infinite)'
    )
    
    args = parser.parse_args()
    
    scanner = MultiChainScanner(args.config)
    scanner.run(max_iterations=args.max_iterations)


if __name__ == '__main__':
    main()
