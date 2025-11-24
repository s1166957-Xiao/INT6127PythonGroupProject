"""
检查区块链运行状态的脚本
用于快速判断区块链模块是否在运行
"""

import sys
import time

def check_blockchain_status():
    """检查区块链状态"""
    print("=" * 60)
    print("区块链运行状态检查")
    print("=" * 60)
    
    try:
        from blockchain_manager import BlockchainManager
        
        # 创建管理器实例（模拟）
        manager = BlockchainManager(is_enabled=False)
        
        print("\n[1] 基本状态检查")
        print("-" * 60)
        status = manager.get_status_info()
        
        print(f"启用状态: {'✓ 已启用' if status['is_enabled'] else '✗ 未启用'}")
        print(f"上传器状态: {'✓ 已配置' if status['has_uploader'] else '✗ 未配置'}")
        print(f"运行状态: {'✓ 正在运行' if status['is_uploading'] else '○ 空闲'}")
        print(f"运行任务数: {status['running_count']}")
        
        if status['last_error']:
            print(f"最后错误: {status['last_error']}")
        else:
            print("最后错误: 无")
        
        print("\n[2] 运行状态检查")
        print("-" * 60)
        is_running = manager.is_running()
        running_count = manager.get_running_count()
        
        if is_running:
            print(f"⚠️  区块链模块正在运行")
            print(f"   当前有 {running_count} 个上传任务")
        else:
            print("✓ 区块链模块当前空闲（没有运行中的任务）")
        
        print("\n[3] 判断方法")
        print("-" * 60)
        print("方法1: 查看界面状态")
        print("  - 菜单：区块链 → 查看运行状态")
        print()
        print("方法2: 查看控制台日志")
        print("  - 查找以 '[区块链]' 开头的日志")
        print("  - 正常运行时会有日志输出")
        print()
        print("方法3: 使用代码检查")
        print("  - manager.is_running()  # 返回 True/False")
        print("  - manager.get_running_count()  # 返回任务数")
        print("  - manager.get_status_info()  # 返回完整状态")
        
        print("\n" + "=" * 60)
        print("检查完成！")
        print("=" * 60)
        
    except ImportError as e:
        print(f"✗ 无法导入区块链模块: {e}")
        print("提示: 请确保 blockchain_manager.py 文件存在")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 检查过程中出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_blockchain_status()

