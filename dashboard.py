import time
from datetime import datetime
from typing import Dict
import logging


class Dashboard:
    """Command-line dashboard for real-time metrics"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_time = time.time()
        self.metrics = {
            'total_scans': 0,
            'found_keys': 0,
            'avg_scan_time': 0,
            'scan_speed': 0,
            'endpoint_latencies': {}
        }
    
    def update_metrics(self, scan_result: Dict):
        """Update dashboard metrics from scan result"""
        self.metrics['total_scans'] += 1
        
        if scan_result.get('found'):
            self.metrics['found_keys'] += 1
        
        # Calculate average scan time
        total_time = time.time() - self.start_time
        self.metrics['avg_scan_time'] = total_time / self.metrics['total_scans']
        self.metrics['scan_speed'] = self.metrics['total_scans'] / total_time
    
    def display_header(self):
        """Display dashboard header"""
        header = """
╔════════════════════════════════════════════════════════════╗
║         🔑 MULTI-CHAIN KEY SCANNER & CHECKER 🔑           ║
║          Random Bitcoin/Ethereum/Solana Finder            ║
╚════════════════════════════════════════════════════════════╝
        """
        print(header)
    
    def display_status(self):
        """Display current status"""
        uptime = time.time() - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        
        status = f"""
╔════════════════════════════════════════════════════════════╗
║ SCANNER STATUS
├────────────────────────────────────────────────────────────┤
│ ⏱️  Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}
│ 📊 Total Scans: {self.metrics['total_scans']:,}
│ 🎯 Found Keys: {self.metrics['found_keys']:,}
│ ⚡ Scan Speed: {self.metrics['scan_speed']:.2f} scans/sec
│ ⏰ Avg Scan Time: {self.metrics['avg_scan_time']:.4f}s
│ ⏳ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
╚════════════════════════════════════════════════════════════╝
        """
        print(status)
    
    def display_found_key(self, keys: Dict, scan_result: Dict):
        """Display when a key with balance is found"""
        alert = f"""
╔════════════════════════════════════════════════════════════╗
║ ✨ FOUND KEY WITH ACTIVITY! ✨
├────────────────────────────────────────────────────────────┤
"""
        
        for blockchain, details in scan_result.get('details', {}).items():
            if details.get('has_activity'):
                if blockchain == 'bitcoin':
                    alert += f"│ Bitcoin Address: {details['address']}\n"
                    alert += f"│ Private Key (WIF): {keys['bitcoin'].get('private_key_wif', 'N/A')}\n"
                    alert += f"│ Private Key (HEX): {keys['bitcoin'].get('private_key_hex', 'N/A')}\n"
                
                elif blockchain == 'ethereum':
                    alert += f"│ Ethereum Address: {details['address']}\n"
                    alert += f"│ Private Key: {keys['ethereum'].get('private_key_hex', 'N/A')}\n"
                
                elif blockchain == 'solana':
                    alert += f"│ Solana Address: {details['address']}\n"
                    alert += f"│ Private Key: {keys['solana'].get('private_key_hex', 'N/A')}\n"
        
        alert += f"│ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        alert += """╚════════════════════════════════════════════════════════════╝
        """
        print(alert)
    
    def display_error(self, error_message: str):
        """Display error message"""
        error = f"""
╔════════════════════════════════════════════════════════════╗
║ ❌ ERROR
├────────────────────────────────────────────────────────────┤
│ {error_message}
╚════════════════════════════════════════════════════════════╝
        """
        print(error)
