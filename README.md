# Multi-Chain Random Key Scanner

A high-performance Python-based random private key generator and balance checker for multiple blockchains.

## 🎯 Features

- **Multi-Chain Support**: Bitcoin, Ethereum, Solana, Litecoin
- **Configure RPC Endpoints**: Customize blockchain node endpoints in `config.json`
- **High-Entropy Generation**: Cryptographically secure random key generation
- **Fast Balance Checking**: Parallel checks across multiple blockchains
- **Encrypted Storage**: Found keys are encrypted with AES-256-GCM
- **Real-time Dashboard**: Live scanning metrics and status display
- **Structured Logging**: Detailed logs for auditing and debugging

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/amirofski/random-bitcoin-with-balance-check.git
cd random-bitcoin-with-balance-check

# Install dependencies
pip install -r requirements.txt

# Set encryption password (optional)
export KEY_ENCRYPTION_PASSWORD="your-secure-password"
```

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
  "general": {
    "threads": 4,
    "log_level": "INFO",
    "encryption_enabled": true,
    "output_file": "found_keys.txt"
  },
  "blockchains": {
    "bitcoin": {
      "enabled": true,
      "endpoints": ["https://blockchain.info/q/addressbalance/"],
      "timeout": 10
    },
    "ethereum": {
      "enabled": true,
      "endpoints": ["https://mainnet.infura.io/v3/YOUR_INFURA_KEY"],
      "timeout": 10
    }
  }
}
```

### Supported Blockchains

- **Bitcoin**: P2PKH addresses (use `blockchain.info` or `blockstream.info` APIs)
- **Ethereum**: EVM-compatible networks (use Infura, Alchemy, or custom RPC)
- **Solana**: Use public RPC endpoints
- **Litecoin**: Litecoin mainnet

## 🏃 Usage

### Basic Scanning

```bash
python main.py
```

### With Configuration File

```bash
python main.py --config custom_config.json
```

### Limited Iterations

```bash
python main.py --max-iterations 1000
```

## 📊 Output

### Console Dashboard

The scanner displays:
- 📊 Total scans performed
- 🎯 Found keys with balances
- ⚡ Scanning speed (scans/sec)
- ⏰ Average scan time
- ⏳ Current timestamp

### Found Keys

Found keys are automatically saved to the configured output file (`found_keys.txt`):

**Without Encryption:**
```json
{
  "timestamp": "2026-06-04T12:34:56.789123",
  "found_at": "2026-06-04T12:34:55.123456",
  "scan_time": 0.8234,
  "keys": {
    "bitcoin": {
      "address": "1A1z7agoat...",
      "private_key_hex": "...",
      "private_key_wif": "..."
    }
  },
  "activity": {
    "bitcoin": {
      "address": "1A1z7agoat...",
      "has_activity": true
    }
  }
}
```

**With Encryption (set password via env var):**
```
Base64 encoded encrypted data...
```

### Logs

- **Console**: Real-time progress and important events
- **File** (`scanner.log`): Detailed debug information

## 🔐 Security Notes

1. **Encryption**: Set `KEY_ENCRYPTION_PASSWORD` environment variable for encrypted storage
2. **API Keys**: Don't commit API keys to git; use environment variables
3. **Private Keys**: Found keys are encrypted before storage
4. **Rate Limiting**: Configure timeouts appropriately for your endpoints

## 🛠️ Architecture

- **`main.py`**: Main scanner orchestrator
- **`config.py`**: Configuration management
- **`key_generator.py`**: Multi-chain key generation
- **`blockchain_scanner.py`**: Balance and transaction checking
- **`encryption.py`**: AES-256-GCM encryption
- **`dashboard.py`**: Real-time metrics display
- **`logger.py`**: Logging and success tracking

## 📝 Example Configuration

### Bitcoin Only
```json
{
  "blockchains": {
    "bitcoin": {
      "enabled": true,
      "endpoints": ["https://blockchain.info/q/addressbalance/"],
      "timeout": 10
    },
    "ethereum": { "enabled": false },
    "solana": { "enabled": false }
  }
}
```

### Multiple Endpoints per Chain
```json
{
  "ethereum": {
    "enabled": true,
    "endpoints": [
      "https://mainnet.infura.io/v3/KEY1",
      "https://eth-mainnet.alchemyapi.io/v2/KEY2",
      "https://1rpc.com/eth"
    ],
    "timeout": 10
  }
}
```

## ⚠️ Disclaimer

This tool is for educational and testing purposes only. Generating and checking random addresses is extremely unlikely to find existing addresses with balances due to the astronomical key space size.

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📞 Support

For issues and questions, please open a GitHub issue on the repository.
