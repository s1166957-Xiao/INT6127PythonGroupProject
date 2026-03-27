import cv2
import json

# 尝试导入 pyzbar，如果失败则设置为 None
try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except (ImportError, FileNotFoundError, OSError) as e:
    decode = None
    PYZBAR_AVAILABLE = False
    print(f"警告: pyzbar 库不可用，二维码识别功能将被禁用。错误: {e}")

def read_express_qr_code(image_path):
    """
    读取包含快递信息的二维码并解析为字典
    
    参数:
        image_path: 二维码图片路径
        
    返回:
        dict: 包含快递信息的字典
    """
    try:
        if not image_path:
            raise ValueError("未选择图片文件")
            
        # 使用Unicode路径读取图片
        import numpy as np
        with open(image_path, 'rb') as f:
            image_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
        if image is None:
            raise ValueError("无法读取图片文件，请确保文件存在且格式正确")
        
        # 检查 pyzbar 是否可用
        if not PYZBAR_AVAILABLE or decode is None:
            raise ValueError("二维码识别功能不可用，请安装 pyzbar 所需的 DLL 文件")
        
        # 解码二维码
        decoded_objects = decode(image)
        
        if not decoded_objects:
            raise ValueError("未检测到二维码，请确保图片清晰且包含有效的二维码")
        
        # 获取第一个二维码的数据
        qr_data = decoded_objects[0].data.decode('utf-8')
        
        # 解析数据（假设是JSON格式）
        try:
            express_info = json.loads(qr_data)
        except json.JSONDecodeError:
            # 如果不是JSON，尝试其他格式解析
            express_info = parse_express_data(qr_data)
        
        return express_info
        
    except Exception as e:
        print(f"读取二维码时出错: {e}")
        return None

def parse_express_data(data_string):
    """
    解析快递数据字符串为字典
    
    参数:
        data_string: 包含快递信息的字符串
        
    返回:
        dict: 解析后的字典
    """
    express_info = {
        "express_id": "",
        "pick_code": "",
        "sender": "",
        "receiver": "",
        "location": "",
        "notes": "",
    }
    
    # 方法1: 如果是键值对格式
    if "=" in data_string or ":" in data_string:
        lines = data_string.split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
            elif ':' in line:
                key, value = line.split(':', 1)
            else:
                continue
            
            key = key.strip().lower()
            value = value.strip()
            
            if 'express' in key or 'id' in key:
                express_info["express_id"] = value
            elif 'pick' in key or 'code' in key:
                express_info["pick_code"] = value
            elif 'sender' in key:
                express_info["sender"] = value
            elif 'receiver' in key:
                express_info["receiver"] = value
            elif 'location' in key:
                express_info["location"] = value
            elif 'notes' in key or 'note' in key:
                express_info["notes"] = value
    
    # 方法2: 如果是CSV格式
    elif ',' in data_string:
        parts = [part.strip() for part in data_string.split(',')]
        if len(parts) >= 8:
            express_info = {
                "express_id": parts[0],
                "pick_code": parts[1],
                "sender": parts[2],
                "sender_name": parts[3],
                "receiver": parts[4],
                "receiver_name": parts[5],
                "location": parts[6],
                "notes": parts[7],
            }
    
    return express_info

# 使用示例
if __name__ == "__main__":
    # 读取二维码
    result = read_express_qr_code("qrcode.png")
    
    if result:
        print("成功读取快递信息:")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print("读取失败")
