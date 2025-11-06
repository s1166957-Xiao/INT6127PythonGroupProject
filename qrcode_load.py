import cv2
from pyzbar.pyzbar import decode
import json

def read_express_qr_code(image_path):
    """
    读取包含快递信息的二维码并解析为字典
    
    参数:
        image_path: 二维码图片路径
        
    返回:
        dict: 包含快递信息的字典
    """
    try:
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("无法读取图片文件")
        
        # 解码二维码
        decoded_objects = decode(image)
        
        if not decoded_objects:
            raise ValueError("未检测到二维码")
        
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

