import os
import pyotp
import json
import qrcode
from PIL import Image
from datetime import datetime

class TOTPManager:
    """TOTP管理器类，用于处理双因素认证相关的操作"""
    
    def __init__(self, config_file='totp_config.json'):
        """初始化TOTP管理器
        
        Args:
            config_file (str): 配置文件路径，用于存储TOTP密钥
        """
        self.config_file = config_file
        self.secret_key = None
        self.load_config()
    
    def load_config(self):
        """从配置文件加载TOTP密钥"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.secret_key = config.get('secret_key')
            except Exception as e:
                print(f"加载TOTP配置出错: {str(e)}")
    
    def save_config(self):
        """保存TOTP密钥到配置文件"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'secret_key': self.secret_key}, f)
        except Exception as e:
            print(f"保存TOTP配置出错: {str(e)}")
    
    def generate_new_secret(self):
        """生成新的TOTP密钥"""
        self.secret_key = pyotp.random_base32()
        self.save_config()
        return self.secret_key
    
    def verify_totp(self, code):
        """验证TOTP验证码
        
        Args:
            code (str): 6位数字验证码
            
        Returns:
            bool: 验证是否成功
        """
        if not self.secret_key:
            return False
            
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(code)
    
    def get_current_totp(self):
        """获取当前有效的TOTP验证码（仅用于测试）
        
        Returns:
            str: 当前有效的6位验证码
        """
        if not self.secret_key:
            return None
            
        totp = pyotp.TOTP(self.secret_key)
        return totp.now()
    
    def generate_qr_code(self, save_dir='qrcodes', issuer="快递管理系统"):
        """生成TOTP配置二维码
        
        Args:
            save_dir (str): 保存二维码图片的目录
            issuer (str): 发行方名称，显示在验证器应用中
            
        Returns:
            tuple: (str, Image), 生成的二维码图片的完整路径和图片对象
        """
        if not self.secret_key:
            self.generate_new_secret()
            
        # 确保保存目录存在
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 创建TOTP URI（用于生成二维码）
        totp = pyotp.TOTP(self.secret_key)
        provisioning_uri = totp.provisioning_uri(
            name="admin@express",
            issuer_name=issuer
        )
        
        # 创建QR码
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # 生成图像
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"totp_config_{timestamp}.png"
        file_path = os.path.join(save_dir, filename)
        
        # 保存图像
        img.save(file_path)
        print(f"TOTP配置二维码已保存为: {file_path}")
        
        return file_path, img
    
    def is_configured(self):
        """检查是否已配置TOTP密钥
        
        Returns:
            bool: 是否已配置
        """
        return self.secret_key is not None
