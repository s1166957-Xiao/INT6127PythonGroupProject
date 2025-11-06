import qrcode

def generate_qr_code(data, filename="qrcode.png"):
    """
    将字符串数据生成二维码并保存为图片
    
    参数:
        data: 要编码的字符串
        filename: 保存的文件名
    """
    # 创建QRCode实例
    qr = qrcode.QRCode(
        version=1,  # 控制二维码大小，1-40，1是最小版本
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错率
        box_size=10,  # 每个"盒子"的像素大小
        border=4,  # 边框大小
    )
    
    # 添加数据
    qr.add_data(data)
    qr.make(fit=True)
    
    # 生成二维码图像
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 保存图像
    img.save(filename)
    print(f"二维码已生成并保存为: {filename}")
    
    return img

# 使用示例
if __name__ == "__main__":
    text = "E008,753951,P001,张三,P002,李四,A区2架,香蕉"
    filename = "qrcode.png"
    
    generate_qr_code(text, filename)