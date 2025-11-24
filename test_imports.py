"""测试所有导入是否正常"""
import sys

print("=" * 60)
print("测试项目依赖导入...")
print("=" * 60)

errors = []

# 测试基础库
try:
    import tkinter as tk
    print("[OK] tkinter")
except Exception as e:
    print(f"[ERROR] tkinter: {e}")
    errors.append("tkinter")

try:
    from ttkthemes import ThemedTk
    print("[OK] ttkthemes")
except Exception as e:
    print(f"[ERROR] ttkthemes: {e}")
    errors.append("ttkthemes")

try:
    from PIL import Image, ImageTk
    print("[OK] Pillow (PIL)")
except Exception as e:
    print(f"[ERROR] Pillow: {e}")
    errors.append("Pillow")

try:
    import pandas as pd
    print("[OK] pandas")
except Exception as e:
    print(f"[ERROR] pandas: {e}")
    errors.append("pandas")

try:
    import qrcode
    print("[OK] qrcode")
except Exception as e:
    print(f"[ERROR] qrcode: {e}")
    errors.append("qrcode")

try:
    import cv2
    print("[OK] opencv-python (cv2)")
except Exception as e:
    print(f"[ERROR] opencv-python: {e}")
    errors.append("opencv-python")

try:
    from pyzbar import pyzbar
    print("[OK] pyzbar")
except Exception as e:
    print(f"[ERROR] pyzbar: {e}")
    errors.append("pyzbar")

try:
    import matplotlib.pyplot as plt
    print("[OK] matplotlib")
except Exception as e:
    print(f"[ERROR] matplotlib: {e}")
    errors.append("matplotlib")

try:
    import pyotp
    print("[OK] pyotp")
except Exception as e:
    print(f"[ERROR] pyotp: {e}")
    errors.append("pyotp")

try:
    from web3 import Web3
    print("[OK] web3")
except Exception as e:
    print(f"[ERROR] web3: {e}")
    errors.append("web3")

try:
    from eth_account import Account
    print("[OK] eth-account")
except Exception as e:
    print(f"[ERROR] eth-account: {e}")
    errors.append("eth-account")

# 测试项目模块
print("\n" + "=" * 60)
print("测试项目模块...")
print("=" * 60)

try:
    import qrcode_create
    print("[OK] qrcode_create")
except Exception as e:
    print(f"[WARNING] qrcode_create: {e}")

try:
    import qrcode_load
    print("[OK] qrcode_load")
except Exception as e:
    print(f"[WARNING] qrcode_load: {e} (可选模块)")

try:
    from database import DatabaseManager
    print("[OK] database")
except Exception as e:
    print(f"[ERROR] database: {e}")
    errors.append("database")

try:
    from totp_manager import TOTPManager
    print("[OK] totp_manager")
except Exception as e:
    print(f"[ERROR] totp_manager: {e}")
    errors.append("totp_manager")

try:
    from style_manager import tr, CURRENT_LANG
    print("[OK] style_manager")
except Exception as e:
    print(f"[ERROR] style_manager: {e}")
    errors.append("style_manager")

try:
    from blockchain_manager import BlockchainManager
    print("[OK] blockchain_manager")
except Exception as e:
    print(f"[WARNING] blockchain_manager: {e} (可选模块)")

# 总结
print("\n" + "=" * 60)
if errors:
    print(f"[ERROR] 发现 {len(errors)} 个错误:")
    for err in errors:
        print(f"  - {err}")
    print("\n请运行: pip install -r requirements.txt")
    sys.exit(1)
else:
    print("[SUCCESS] 所有必需模块导入成功！")
    print("项目可以正常运行。")
    sys.exit(0)

