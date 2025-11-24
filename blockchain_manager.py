"""
快递管理系统 - 区块链上链集成模块
提供简化的 UI 接口和事件处理，用于将数据上链
"""

import threading
from typing import Optional, Callable
from blockchain_uploader import BlockchainUploader, create_uploader


class BlockchainManager:
    """区块链操作管理器 - 为主程序提供简化接口"""
    
    def __init__(self, is_enabled: bool = False):
        """
        初始化区块链管理器
        
        Args:
            is_enabled: 是否启用区块链功能
        """
        self.is_enabled = is_enabled
        self.uploader: Optional[BlockchainUploader] = None
        self.last_error: Optional[str] = None
        self.upload_callback: Optional[Callable] = None  # 用于 UI 回调
        self.is_uploading: bool = False  # 是否正在上传
        self.upload_threads: list = []  # 正在运行的上传线程列表
    
    def configure(self, rpc_url: str, private_key: str, contract_address: str) -> bool:
        """
        配置区块链连接
        
        Args:
            rpc_url: RPC 节点 URL
            private_key: 钱包私钥
            contract_address: 智能合约地址
            
        Returns:
            配置是否成功
        """
        try:
            self.uploader = create_uploader(rpc_url, private_key, contract_address)
            self.is_enabled = True
            return True
        except Exception as e:
            self.last_error = str(e)
            self.is_enabled = False
            return False
    
    def upload_all_data_async(self, express_file: str, user_file: str, 
                              callback: Optional[Callable] = None) -> threading.Thread:
        """
        异步上传所有数据（避免阻塞 UI）
        
        Args:
            express_file: 快递数据文件路径
            user_file: 用户数据文件路径
            callback: 完成后的回调函数 (success: bool, results: dict) -> None
            
        Returns:
            后台线程对象
        """
        def _upload_thread():
            self.is_uploading = True
            self.upload_threads.append(threading.current_thread())
            print(f"[区块链] 开始上传所有数据...")
            try:
                if not self.is_enabled or self.uploader is None:
                    error_msg = "区块链未配置"
                    print(f"[区块链] 错误: {error_msg}")
                    if callback:
                        callback(False, {"error": error_msg})
                    return
                
                results = self.uploader.upload_all_data(express_file, user_file)
                print(f"[区块链] 上传完成: {results}")
                if callback:
                    callback(True, results)
            except Exception as e:
                self.last_error = str(e)
                print(f"[区块链] 上传失败: {str(e)}")
                if callback:
                    callback(False, {"error": str(e)})
            finally:
                self.is_uploading = False
                if threading.current_thread() in self.upload_threads:
                    self.upload_threads.remove(threading.current_thread())
        
        thread = threading.Thread(target=_upload_thread, daemon=True)
        thread.start()
        return thread
    
    def upload_express_data_async(self, express_file: str, 
                                  callback: Optional[Callable] = None) -> threading.Thread:
        """
        异步上传快递数据
        
        Args:
            express_file: 快递数据文件路径
            callback: 完成后的回调函数 (success: bool, image_path: str or None) -> None
            
        Returns:
            后台线程对象
        """
        def _upload_thread():
            self.is_uploading = True
            self.upload_threads.append(threading.current_thread())
            print(f"[区块链] 开始上传快递数据...")
            try:
                if not self.is_enabled or self.uploader is None:
                    print(f"[区块链] 错误: 区块链未配置")
                    if callback:
                        callback(False, None)
                    return
                
                import pandas as pd
                express_df = pd.read_excel(express_file)
                success, upload_id, image_path = self.uploader.upload_express_data(express_df)
                if success:
                    print(f"[区块链] 快递数据上传成功")
                else:
                    print(f"[区块链] 快递数据上传失败")
                if callback:
                    callback(success, image_path)
            except Exception as e:
                self.last_error = str(e)
                print(f"[区块链] 上传异常: {str(e)}")
                if callback:
                    callback(False, None)
            finally:
                self.is_uploading = False
                if threading.current_thread() in self.upload_threads:
                    self.upload_threads.remove(threading.current_thread())
        
        thread = threading.Thread(target=_upload_thread, daemon=True)
        thread.start()
        return thread
    
    def upload_user_data_async(self, user_file: str, 
                               callback: Optional[Callable] = None) -> threading.Thread:
        """
        异步上传用户数据
        
        Args:
            user_file: 用户数据文件路径
            callback: 完成后的回调函数 (success: bool, upload_id: int or None) -> None
            
        Returns:
            后台线程对象
        """
        def _upload_thread():
            self.is_uploading = True
            self.upload_threads.append(threading.current_thread())
            print(f"[区块链] 开始上传用户数据...")
            try:
                if not self.is_enabled or self.uploader is None:
                    print(f"[区块链] 错误: 区块链未配置")
                    if callback:
                        callback(False, None)
                    return
                
                import pandas as pd
                user_df = pd.read_excel(user_file)
                success, upload_id, image_path = self.uploader.upload_user_data(user_df)
                if success:
                    print(f"[区块链] 用户数据上传成功")
                else:
                    print(f"[区块链] 用户数据上传失败")
                if callback:
                    callback(success, image_path)
            except Exception as e:
                self.last_error = str(e)
                print(f"[区块链] 上传异常: {str(e)}")
                if callback:
                    callback(False, None)
            finally:
                self.is_uploading = False
                if threading.current_thread() in self.upload_threads:
                    self.upload_threads.remove(threading.current_thread())
        
        thread = threading.Thread(target=_upload_thread, daemon=True)
        thread.start()
        return thread
    
    def get_upload_record(self, upload_id: int) -> Optional[dict]:
        """
        查询上链记录详情
        
        Args:
            upload_id: 上链记录ID
            
        Returns:
            记录详情字典或 None
        """
        if not self.is_enabled or self.uploader is None:
            return None
        
        try:
            return self.uploader.get_upload_record(upload_id)
        except Exception as e:
            self.last_error = str(e)
            return None
    
    def get_statistics(self) -> int:
        """获取总上链次数"""
        if not self.is_enabled or self.uploader is None:
            return 0
        
        try:
            return self.uploader.get_statistics()
        except Exception as e:
            self.last_error = str(e)
            return 0
    
    def is_running(self) -> bool:
        """检查是否有上传任务正在运行"""
        return self.is_uploading or len(self.upload_threads) > 0
    
    def get_running_count(self) -> int:
        """获取正在运行的上传任务数量"""
        # 清理已完成的线程
        self.upload_threads = [t for t in self.upload_threads if t.is_alive()]
        return len(self.upload_threads)
    
    def get_status_info(self) -> dict:
        """获取区块链状态信息"""
        return {
            "is_enabled": self.is_enabled,
            "is_uploading": self.is_uploading,
            "running_count": self.get_running_count(),
            "last_error": self.last_error,
            "has_uploader": self.uploader is not None
        }


# 快捷函数
def initialize_blockchain(rpc_url: str = None, private_key: str = None, 
                         contract_address: str = None) -> Optional[BlockchainManager]:
    """
    快速初始化区块链管理器
    
    Args:
        rpc_url: RPC URL（如果为 None 则禁用）
        private_key: 私钥
        contract_address: 合约地址
        
    Returns:
        配置好的 BlockchainManager 或 None
    """
    if rpc_url is None or private_key is None or contract_address is None:
        # 未提供配置，返回禁用状态的管理器
        return BlockchainManager(is_enabled=False)
    
    manager = BlockchainManager(is_enabled=False)
    if manager.configure(rpc_url, private_key, contract_address):
        return manager
    else:
        return BlockchainManager(is_enabled=False)
