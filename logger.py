import logging
import json
from datetime import datetime
from typing import Dict


class FileHandler(logging.FileHandler):
    """Custom file handler for structured logging"""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + '\n')
            self.flush()
        except Exception:
            self.handleError(record)


class SuccessLogger:
    """Logger for successful key finds"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.output_file = config['general']['output_file']
        self.encryption_enabled = config['general']['encryption_enabled']
        
        if self.encryption_enabled:
            from encryption import KeyEncryption
            self.encryptor = KeyEncryption()
        else:
            self.encryptor = None
    
    def log_found_key(self, keys: Dict, scan_result: Dict):
        """Log found key with balance or transaction history"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'found_at': scan_result.get('timestamp'),
            'scan_time': scan_result.get('scan_time'),
            'keys': keys,
            'activity': scan_result.get('details', {})
        }
        
        try:
            if self.encryption_enabled:
                encrypted = self.encryptor.encrypt_data(log_entry)
                with open(self.output_file, 'a') as f:
                    f.write(encrypted + '\n')
            else:
                with open(self.output_file, 'a') as f:
                    f.write(json.dumps(log_entry, indent=2) + '\n')
                    f.write('=' * 80 + '\n\n')
        
        except Exception as e:
            print(f"Failed to log found key: {str(e)}")
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('KeyScanner')
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        # File handler
        file_handler = FileHandler('scanner.log')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
