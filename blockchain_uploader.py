"""
区块链数据上链模块 - Web3 集成
用于将快递和用户数据上链到以太坊区块链
"""

import json
import hashlib
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional
from web3 import Web3
from eth_account import Account
import sys
import io
import os
import random
from PIL import Image

# 设置控制台编码为UTF-8（Windows兼容）
if sys.platform == 'win32':
    try:
        # 尝试设置控制台编码
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        # 如果失败，使用io包装
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class BlockchainUploader:
    """区块链数据上链管理器"""
    
    # 合约 ABI（应用二进制接口）
    CONTRACT_ABI = [
        {
            "inputs": [{"internalType": "string", "name": "dataHash", "type": "string"},
                      {"internalType": "uint256", "name": "recordCount", "type": "uint256"}],
            "name": "uploadExpressData",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "string", "name": "dataHash", "type": "string"},
                      {"internalType": "uint256", "name": "recordCount", "type": "uint256"}],
            "name": "uploadUserData",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "uint256", "name": "uploadId", "type": "uint256"}],
            "name": "getDataRecord",
            "outputs": [
                {"internalType": "uint256", "name": "uploadId", "type": "uint256"},
                {"internalType": "address", "name": "uploader", "type": "address"},
                {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"internalType": "string", "name": "dataHash", "type": "string"},
                {"internalType": "string", "name": "dataType", "type": "string"},
                {"internalType": "uint256", "name": "recordCount", "type": "uint256"},
                {"internalType": "bool", "name": "isVerified", "type": "bool"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "getStatistics",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        """
        初始化区块链上传器
        
        Args:
            rpc_url: RPC 节点 URL（如 http://localhost:8545 或以太坊 Sepolia 测试网）
            private_key: 私钥（用于签名交易）
            contract_address: 智能合约地址
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"无法连接到区块链节点: {rpc_url}")
        
        self.account = Account.from_key(private_key)
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.CONTRACT_ABI
        )
        
        print(f"[OK] 区块链连接成功")
        print(f"[OK] 钱包地址: {self.account.address}")
    
    @staticmethod
    def _calculate_file_hash(file_path: str) -> str:
        """计算文件 SHA256 哈希"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return "0x" + sha256_hash.hexdigest()
    
    @staticmethod
    def _get_dataframe_hash(df: pd.DataFrame) -> str:
        """计算 DataFrame 哈希（用于从已加载的数据计算）"""
        data_str = df.to_json()
        return "0x" + hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def _get_dataframe_record_count(df: pd.DataFrame) -> int:
        """获取 DataFrame 的行数"""
        return len(df)
    
    def _send_transaction(self, func) -> Tuple[bool, str]:
        """
        发送交易到区块链
        
        Args:
            func: 合约函数对象
            
        Returns:
            (success: bool, tx_hash_or_error: str)
        """
        try:
            # 获取 gas 估计
            gas_estimate = func.estimate_gas({"from": self.account.address})
            
            # 构建交易
            tx = func.build_transaction({
                "from": self.account.address,
                "gas": int(gas_estimate * 1.2),  # 增加 20% 的 gas 限制以确保成功
                "gasPrice": self.w3.eth.gas_price,
                "nonce": self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # 签名交易
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            
            # 发送交易（兼容web3.py不同版本的属性名）
            # web3.py 6.x及以下使用 rawTransaction，7.x及以上使用 raw_transaction
            if hasattr(signed_tx, 'raw_transaction'):
                raw_tx = signed_tx.raw_transaction
            elif hasattr(signed_tx, 'rawTransaction'):
                raw_tx = signed_tx.rawTransaction
            else:
                # 如果都不存在，尝试直接访问
                raw_tx = getattr(signed_tx, 'raw_transaction', getattr(signed_tx, 'rawTransaction', None))
                if raw_tx is None:
                    raise AttributeError("无法找到签名交易的原始交易数据属性")
            
            tx_hash = self.w3.eth.send_raw_transaction(raw_tx)
            print(f"[OK] 交易已发送: {tx_hash.hex()}")
            
            # 等待交易确认
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt['status'] == 1:
                print(f"[OK] 交易确认成功")
                return True, tx_hash.hex()
            else:
                print(f"[ERROR] 交易失败")
                return False, "Transaction failed"
        
        except Exception as e:
            error_msg = f"交易失败: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    
    def upload_express_data(self, express_df: pd.DataFrame) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        上传快递数据到区块链
        
        Args:
            express_df: 快递数据 DataFrame
            
        Returns:
            (success: bool, upload_id: Optional[int], image_path: Optional[str])
        """
        if express_df.empty:
            print("[ERROR] 快递数据为空，无法上链")
            return False, None, None
        
        try:
            # 计算数据哈希和记录数
            data_hash = self._get_dataframe_hash(express_df)
            record_count = self._get_dataframe_record_count(express_df)
            
            print(f"\n📤 准备上传快递数据...")
            print(f"  - 记录数: {record_count}")
            print(f"  - 数据哈希: {data_hash}")
            
            # 调用智能合约函数
            func = self.contract.functions.uploadExpressData(data_hash, record_count)
            success, tx_hash = self._send_transaction(func)
            
            if success:
                # 获取 upload ID
                try:
                    upload_id = self.contract.functions.getStatistics().call()
                except Exception as e:
                    print(f"[WARNING] 获取上链记录ID失败: {str(e)}")
                    upload_id = None
                
                print(f"[OK] 快递数据上链成功")
                
                # 获取jpguse文件夹中的任意一张jpg图片路径
                image_path = None
                try:
                    jpguse_dir = Path("jpguse")
                    if jpguse_dir.exists():
                        jpg_files = list(jpguse_dir.glob("*.jpg"))
                        if jpg_files:
                            # 随机选择一张图片
                            selected_image = random.choice(jpg_files)
                            image_path = str(selected_image.absolute())
                except Exception as e:
                    print(f"[WARNING] 无法获取图片: {str(e)}")
                
                return True, upload_id, image_path
            else:
                return False, None, None
        
        except Exception as e:
            print(f"[ERROR] 快递数据上链失败: {str(e)}")
            return False, None, None
    
    def upload_user_data(self, user_df: pd.DataFrame) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        上传用户数据到区块链
        
        Args:
            user_df: 用户数据 DataFrame
            
        Returns:
            (success: bool, upload_id: Optional[int], image_path: Optional[str])
        """
        if user_df.empty:
            print("[ERROR] 用户数据为空，无法上链")
            return False, None, None
        
        try:
            # 计算数据哈希和记录数
            data_hash = self._get_dataframe_hash(user_df)
            record_count = self._get_dataframe_record_count(user_df)
            
            print(f"\n📤 准备上传用户数据...")
            print(f"  - 记录数: {record_count}")
            print(f"  - 数据哈希: {data_hash}")
            
            # 调用智能合约函数
            func = self.contract.functions.uploadUserData(data_hash, record_count)
            success, tx_hash = self._send_transaction(func)
            
            if success:
                # 获取 upload ID
                try:
                    upload_id = self.contract.functions.getStatistics().call()
                except Exception as e:
                    print(f"[WARNING] 获取上链记录ID失败: {str(e)}")
                    upload_id = None
                
                print(f"[OK] 用户数据上链成功")
                
                # 获取jpguse文件夹中的任意一张jpg图片路径
                image_path = None
                try:
                    jpguse_dir = Path("jpguse")
                    if jpguse_dir.exists():
                        jpg_files = list(jpguse_dir.glob("*.jpg"))
                        if jpg_files:
                            # 随机选择一张图片
                            selected_image = random.choice(jpg_files)
                            image_path = str(selected_image.absolute())
                except Exception as e:
                    print(f"[WARNING] 无法获取图片: {str(e)}")
                
                return True, upload_id, image_path
            else:
                return False, None, None
        
        except Exception as e:
            print(f"[ERROR] 用户数据上链失败: {str(e)}")
            return False, None, None
    
    def upload_all_data(self, express_file: str, user_file: str) -> Dict[str, any]:
        """
        一次性上传所有数据
        
        Args:
            express_file: 快递数据文件路径（xlsx）
            user_file: 用户数据文件路径（xlsx）
            
        Returns:
            包含上链结果的字典
        """
        results = {
            "express": {"success": False, "upload_id": None, "record_count": 0, "image_path": None},
            "user": {"success": False, "upload_id": None, "record_count": 0, "image_path": None}
        }
        
        try:
            # 读取快递数据
            if Path(express_file).exists():
                express_df = pd.read_excel(express_file)
                success, upload_id, image_path = self.upload_express_data(express_df)
                results["express"]["success"] = success
                results["express"]["upload_id"] = upload_id
                results["express"]["record_count"] = len(express_df)
                results["express"]["image_path"] = image_path
            else:
                print(f"[WARNING] 快递文件不存在: {express_file}")
            
            # 读取用户数据
            if Path(user_file).exists():
                user_df = pd.read_excel(user_file)
                success, upload_id, image_path = self.upload_user_data(user_df)
                results["user"]["success"] = success
                results["user"]["upload_id"] = upload_id
                results["user"]["record_count"] = len(user_df)
                results["user"]["image_path"] = image_path
            else:
                print(f"[WARNING] 用户文件不存在: {user_file}")
            
            return results
            
        except Exception as e:
            print(f"[ERROR] 数据上链过程中出错: {str(e)}")
            return results
    
    def get_upload_record(self, upload_id: int) -> Optional[Dict]:
        """
        获取上链记录详情
        
        Args:
            upload_id: 上链记录ID
            
        Returns:
            包含记录详情的字典，或 None（如果查询失败）
        """
        try:
            record = self.contract.functions.getDataRecord(upload_id).call()
            return {
                "uploadId": record[0],
                "uploader": record[1],
                "timestamp": record[2],
                "dataHash": record[3],
                "dataType": record[4],
                "recordCount": record[5],
                "isVerified": record[6]
            }
        except Exception as e:
            print(f"[ERROR] 获取上链记录失败: {str(e)}")
            return None
    
    def get_statistics(self) -> int:
        """获取总上链次数"""
        return self.contract.functions.getStatistics().call()


# 使用示例配置
class BlockchainConfig:
    """区块链配置类"""
    
    # 公共测试网配置（Sepolia）
    RPC_URL = "https://sepolia.infura.io/v3/YOUR_INFURA_KEY"  # 需要替换为实际的 Infura Key
    
    # 本地开发网配置
    LOCAL_RPC_URL = "http://127.0.0.1:8545"  # Ganache 或本地节点
    
    # 示例合约地址（部署后需要替换）
    CONTRACT_ADDRESS = "0x..."  # 需要替换为实际部署的合约地址


def create_uploader(rpc_url: str, private_key: str, contract_address: str) -> BlockchainUploader:
    """
    工厂函数：创建区块链上传器实例
    
    Args:
        rpc_url: RPC 节点 URL
        private_key: 私钥（带 0x 前缀或不带）
        contract_address: 智能合约地址
        
    Returns:
        BlockchainUploader 实例
    """
    # 确保私钥格式正确
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    
    return BlockchainUploader(rpc_url, private_key, contract_address)
