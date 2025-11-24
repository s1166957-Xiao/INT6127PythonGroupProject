
### Development Environment Setup

1. **Clone Repository**
   ```sh
   git clone <repository-url>
   cd INT6127PythonGroupProject-unstable
   ```
2. **Set up Development Environment**
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Run Tests**
   ```sh
   python test_imports.py        # Test dependencies
   python test_blockchain.py     # Test blockchain functionality
   ```


### Technology Stack

- **Core Language**: Python 3.x
- **GUI Framework**: Tkinter
- **Data Storage**: SQLite
- **Blockchain**: Web3.py (Ethereum compatible)
- **QR Code**: qrcode, pyzbar
- **Data Processing**: pandas, openpyxl
- **Chart Visualization**: matplotlib
- **Security Authentication**: pyotp


## Installation

### System Requirements

None

### Installation Steps

1. **Get Source Code**
   ```sh
   git clone <project repository URL>
   cd INT6127PythonGroupProject-unstable
   ```
2. **Create and Activate Virtual Environment (Recommended)**
   - Windows System:
     ```sh
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - Linux/macOS System:
     ```sh
     python3 -m venv venv
     source venv/bin/activate
     ```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Initialize Database**
   - The system will automatically create SQLite database on first run
   - Ensure the project directory has write permissions
5. **Start Application**
   ```sh
   python main.py
   ```


## Blockchain Function Configuration (Optional)
Note: Blockchain function is optional, the system can run all core business functions normally without blockchain configuration.
To use blockchain functions, blockchain connection configuration is required:
### Method 1: Using Local Test Network (Ganache) - Recommended

### 1. Install Ganache

Ganache is a local Ethereum blockchain for development and testing.

**Download Links:**
- Windows: https://trufflesuite.com/ganache/
- Or use npm: `npm install -g ganache`

### 2. Start Ganache

1. Open Ganache application
2. Click "New Workspace" or "Quick Start"
3. Record the following information:
   - **RPC URL**: Usually `http://127.0.0.1:7545` or `http://127.0.0.1:8545`
   - **Account Private Keys**: You can see each account's private key in Ganache interface
   - **Account Addresses**: Used to receive test coins

### 3. Deploy Smart Contract

You need to deploy smart contracts to Ganache network first. The contract address will be used for configuration.

**If you don't have smart contracts, you can use the following simplified solution:**

Create a simple test contract address (you can use the address of a newly created account in Ganache as a temporary contract address for connection testing).

### 4. Configure Blockchain

In the express management system:
1. Login as administrator
2. Click menu: **Blockchain → Configure Blockchain**
3. Fill in information:
   - **RPC URL**: `http://127.0.0.1:7545` (or the port shown by Ganache)
   - **Private Key**: Account private key shown in Ganache (with or without 0x prefix)
   - **Contract Address**: Deployed smart contract address

### 5. Test Upload

After configuration is complete, you can:
- Click **Blockchain → Upload All Data to Blockchain**
- Or automatically upload after adding express (if configured)

---

## Method 2: Using Public Testnet (Sepolia)

### 1. Get Test Coins

1. Visit Sepolia faucet to get test ETH:
   - https://sepoliafaucet.com/
   - https://faucet.quicknode.com/ethereum/sepolia

2. Create account and get private key using MetaMask or other wallets

### 2. Get RPC URL

Use public RPC nodes:
- Infura: https://sepolia.infura.io/v3/YOUR_PROJECT_ID
- Alchemy: https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY
- Public node: https://rpc.sepolia.org

### 3. Deploy Contract

Deploy smart contract to Sepolia testnet and get contract address.

### 4. Configure and Use

Same as steps 4-5 in Method 1.

---

## Method 3: Test Data Export Only (No Blockchain Connection)

If you only want to test data export functionality without real blockchain connection:

1. Run test script:
   ```bash
   python test_blockchain.py
   ```
   Select option 3, it will create test data files.

2. In express management system:
   - Add some express and user data
   - Use menu: **Blockchain → Upload All Data to Blockchain**
   - The system will first export data to Excel, then try to upload (will prompt if blockchain is not configured)

---

## Test Script Usage

Running test scripts can quickly verify blockchain functionality:

```bash
python test_blockchain.py
```

The script will:
1. Create test data (express and users)
2. Test blockchain connection
3. Test data upload
4. Display on-chain statistics

---

## Common Issues

### 1. Connection Failed: Cannot connect to blockchain node

**Solutions:**
- Check if RPC URL is correct
- Confirm Ganache or testnet node is running
- Check network connection

### 2. Transaction Failed: insufficient funds

**Solutions:**
- Ensure account has enough ETH (test coins)
- In Ganache, accounts have 100 ETH by default
- In testnet, need to get test coins from faucet

### 3. Contract Call Failed

**Solutions:**
- Confirm contract address is correct
- Confirm contract is properly deployed
- Check if contract ABI matches

### 4. Private Key Format Error

**Solutions:**
- Private key can be with or without `0x` prefix
- Ensure private key is 64 hexadecimal characters (32 bytes)

---

## Quick Start (Minimum Configuration)

If you just want to quickly see blockchain functionality running, you can use the following minimum configuration:

1. **Install Ganache** (simplest way)
2. **Start Ganache** with default settings
3. **Configure in express management system**:
   - RPC URL: `http://127.0.0.1:7545`
   - Private Key: Any account private key shown in Ganache interface
   - Contract Address: You can use any account address shown in Ganache as temporary test (real deployment requires real contract)

**Note:** If real smart contract is not deployed, upload operations will fail, but you can see:
- Whether blockchain connection is successful
- Whether data export functionality is normal
- Error message information

---

## View Results

### View in Console

When running express management system, blockchain operation logs will be output to console, including:
- ✓ Connection success information
- ✓ Transaction hash
- ✓ On-chain record ID
- ✗ Error information

### View in Interface

1. **On-chain Statistics**: Menu → Blockchain → View On-chain Statistics
2. **Upload Results**: Prompt box will show results after upload operation completes

### View in Blockchain Explorer

- **Ganache**: View transactions in Ganache interface
- **Sepolia**: Enter transaction hash at https://sepolia.etherscan.io/ to view

---

## Next Steps

After configuration is complete, you can:
1. Add express data in the system
2. The system will automatically upload data to blockchain in background (if configured)
3. Or manually upload data through menu
4. View on-chain statistics and records

## Usage

### Basic Usage Process

1. **Start System**
   ```sh
   python main.py
   ```
2. **Login System**
   - **Administrator**: Requires TOTP verification, can use all functions
   - **Regular User**: Can use query and pickup functions
3. **Express Storage**
   - Click "Storage" tab
   - Fill in express information (sender, recipient, location, etc.)
   - Click "Storage" button, system automatically generates express tracking number and pickup code
4. **Express Pickup**
   - Click "Pickup" tab
   - Enter pickup code or scan QR code
   - Confirm pickup operation

### Blockchain Function Usage

After configuring blockchain, you can use it through:

1. **Manual Data Upload**
   - **Blockchain → Upload All Data to Blockchain**: Upload express and user data
   - **Blockchain → Upload Express Data to Blockchain**: Upload only express data
   - **Blockchain → Upload User Data to Blockchain**: Upload only user data
2. **Automatic Upload**
   - System automatically uploads data in background after adding express
   - Automatically uploads updated data after pickup operation
3. **View On-chain Statistics**
   - **Blockchain → View On-chain Statistics**: Display total on-chain count

### Test Scripts

The project provides multiple test scripts:

```sh
# Test if all dependencies are normal
python test_imports.py

# Quick demo blockchain functionality
python quick_test_blockchain.py

# Complete blockchain test
python test_blockchain.py
```


### License

This project does not adopt MIT license, no LICENSE file 🙃.

### Contributing Guidelines

你怎么能直接 commit 到我的 main 分支啊？！GitHub 上不是这样！你应该先 fork 我的仓库，然后从 develop 分支 checkout 一个新的 feature 分支，比如叫 feature/confession。然后你把你的心意写成代码，并为它写好单元测试和集成测试，确保代码覆盖率达到95%以上。接着你要跑一下 Linter，通过所有的代码风格检查。然后你再 commit，commit message 要遵循 Conventional Commits 规范。之后你把这个分支 push 到你自己的远程仓库，然后给我提一个 Pull Request。在 PR 描述里，你要详细说明你的功能改动和实现思路，并且 @ 我和至少两个其他的评审。我们会 review 你的代码，可能会留下一些评论，你需要解决所有的 thread。等 CI/CD 流水线全部通过，并且拿到至少两个 LGTM 之后，我才会考虑把你的分支 squash and merge 到 develop 里，等待下一个版本发布。你怎么直接上来就想 force push 到 main？！GitHub 上根本不是这样！我拒绝合并！
(Reference: [Why did you directly commit to my master branch] https://www.bilibili.com/video/BV1pwC6BxEeb)


### Contact Information

For questions or suggestions, please contact through:

- Project Repository: [INT6127PythonGroupProject](https://github.com/s1166957-Xiao/INT6127PythonGroupProject)
- Email: <contact-email>[Zhang Fangzhe](s1165489@s.eduhk.hk)

---
