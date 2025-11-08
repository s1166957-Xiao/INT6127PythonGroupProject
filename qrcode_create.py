import qrcode
import json
import os
from datetime import datetime

def generate_qr_code(express_info, save_dir='qrcodes'):
    """
    为快递信息生成二维码
    
    参数:
        express_info: dict, 包含快递信息的字典
        save_dir: str, 保存二维码图片的目录路径
        
    返回:
        tuple: (str, Image), 生成的二维码图片的完整路径和图片对象
    """
    try:
        # 确保保存目录存在
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 将快递信息转换为JSON字符串
        qr_data = json.dumps(express_info, ensure_ascii=False)
        
        # 创建QRCode实例
        qr = qrcode.QRCode(
            version=None,  # 自动选择合适的版本
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # 提高容错率
            box_size=10,  # 每个"盒子"的像素大小
            border=4,  # 边框大小
        )
        
        # 添加数据
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # 生成二维码图像
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 生成文件名（使用快递单号和时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{express_info['express_id']}_{timestamp}.png"
        file_path = os.path.join(save_dir, filename)
        
        # 保存图像
        img.save(file_path)
        print(f"二维码已生成并保存为: {file_path}")
        
        return file_path, img
        
    except Exception as e:
        print(f"生成二维码时出错: {str(e)}")
        return None, None

# 使用示例
if __name__ == "__main__":
    text = "E008,753951,P001,张三,P002,李四,A区2架,香蕉"
    filename = "qrcode.png"
    
    generate_qr_code(text, filename)
