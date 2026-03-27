"""
区块链功能测试脚本
用于测试和演示区块链上传功能
"""

import pandas as pd
from datetime import datetime
from blockchain_manager import BlockchainManager
from blockchain_uploader import BlockchainUploader, create_uploader

def create_test_data():
    """创建测试数据"""
    print("=" * 60)
    print("创建测试数据...")
    print("=" * 60)
    
    # 创建测试快递数据
    express_data = {
        "快递单号": ["E20250101001", "E20250101002", "E20250101003"],
        "取件码": ["123456", "234567", "345678"],
        "发件人ID": ["P001", "P002", "P003"],
        "发件人姓名": ["张三", "李四", "王五"],
        "收件人ID": ["P004", "P005", "P006"],
        "收件人姓名": ["赵六", "钱七", "孙八"],
        "区域ID": ["A001", "A002", "A001"],
        "区域名称": ["A区", "B区", "A区"],
        "位置": ["A区1架", "B区2架", "A区3架"],
        "备注": ["易碎品", "", "加急"],
        "状态": ["在库", "在库", "已取件"],
        "创建时间": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 3,
        "更新时间": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 3
    }
    express_df = pd.DataFrame(express_data)
    express_file = "test_express.xlsx"
    express_df.to_excel(express_file, index=False)
    print(f"✓ 测试快递数据已保存到: {express_file}")
    print(f"  记录数: {len(express_df)}")
    
    # 创建测试用户数据
    user_data = {
        "用户ID": ["P001", "P002", "P003", "P004", "P005", "P006"],
        "姓名": ["张三", "李四", "王五", "赵六", "钱七", "孙八"]
    }
    user_df = pd.DataFrame(user_data)
    user_file = "test_user.xlsx"
    user_df.to_excel(user_file, index=False)
    print(f"✓ 测试用户数据已保存到: {user_file}")
    print(f"  记录数: {len(user_df)}")
    
    return express_file, user_file

def test_blockchain_connection(rpc_url, private_key, contract_address):
    """测试区块链连接"""
    print("\n" + "=" * 60)
    print("测试区块链连接...")
    print("=" * 60)
    
    try:
        uploader = create_uploader(rpc_url, private_key, contract_address)
        print("✓ 区块链连接成功！")
        print(f"✓ 钱包地址: {uploader.account.address}")
        print(f"✓ 合约地址: {uploader.contract_address}")
        return uploader
    except Exception as e:
        print(f"✗ 区块链连接失败: {str(e)}")
        return None

def test_upload_data(uploader, express_file, user_file):
    """测试上传数据"""
    print("\n" + "=" * 60)
    print("测试数据上传...")
    print("=" * 60)
    
    if uploader is None:
        print("✗ 上传器未初始化，无法测试")
        return
    
    # 测试上传快递数据
    print("\n[1] 测试上传快递数据...")
    try:
        express_df = pd.read_excel(express_file)
        success, upload_id, image_path = uploader.upload_express_data(express_df)
        if success:
            print(f"✓ 快递数据上传成功！上链记录ID: {upload_id}")
        else:
            print("✗ 快递数据上传失败")
    except Exception as e:
        print(f"✗ 上传快递数据时出错: {str(e)}")
    
    # 测试上传用户数据
    print("\n[2] 测试上传用户数据...")
    try:
        user_df = pd.read_excel(user_file)
        success, upload_id = uploader.upload_user_data(user_df)
        if success:
            print(f"✓ 用户数据上传成功！上链记录ID: {upload_id}")
        else:
            print("✗ 用户数据上传失败")
    except Exception as e:
        print(f"✗ 上传用户数据时出错: {str(e)}")
    
    # 测试查询统计
    print("\n[3] 查询上链统计...")
    try:
        stats = uploader.get_statistics()
        print(f"✓ 总上链次数: {stats}")
    except Exception as e:
        print(f"✗ 查询统计时出错: {str(e)}")

def test_blockchain_manager(rpc_url, private_key, contract_address, express_file, user_file):
    """测试区块链管理器"""
    print("\n" + "=" * 60)
    print("测试区块链管理器...")
    print("=" * 60)
    
    manager = BlockchainManager(is_enabled=False)
    
    # 配置区块链
    print("\n[1] 配置区块链管理器...")
    if manager.configure(rpc_url, private_key, contract_address):
        print("✓ 区块链管理器配置成功")
    else:
        print(f"✗ 配置失败: {manager.last_error}")
        return
    
    # 测试异步上传
    print("\n[2] 测试异步上传所有数据...")
    def upload_callback(success, results):
        print("\n上传完成回调:")
        if success:
            print("✓ 上传成功！")
            print(f"  快递数据: {results.get('express', {})}")
            print(f"  用户数据: {results.get('user', {})}")
        else:
            print(f"✗ 上传失败: {results.get('error', '未知错误')}")
    
    thread = manager.upload_all_data_async(express_file, user_file, upload_callback)
    print("✓ 异步上传任务已启动，等待完成...")
    thread.join(timeout=300)  # 等待最多5分钟
    
    # 查询统计
    print("\n[3] 查询上链统计...")
    stats = manager.get_statistics()
    print(f"✓ 总上链次数: {stats}")

def main():
    """主函数"""
    print("=" * 60)
    print("区块链功能测试脚本")
    print("=" * 60)
    
    # 创建测试数据
    express_file, user_file = create_test_data()
    
    # 配置信息（需要根据实际情况修改）
    print("\n" + "=" * 60)
    print("区块链配置")
    print("=" * 60)
    print("\n请选择测试方式：")
    print("1. 使用本地测试网络 (Ganache) - 推荐用于开发测试")
    print("2. 使用公共测试网 (Sepolia) - 需要测试币")
    print("3. 仅测试数据导出功能（不连接区块链）")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == "3":
        print("\n✓ 测试数据已创建，文件位置：")
        print(f"  - {express_file}")
        print(f"  - {user_file}")
        print("\n您可以在快递管理系统中使用这些文件进行测试。")
        return
    
    # 获取配置信息
    print("\n请输入区块链配置信息：")
    rpc_url = input("RPC URL (例如: http://127.0.0.1:8545): ").strip()
    private_key = input("私钥 (带或不带0x前缀): ").strip()
    contract_address = input("合约地址: ").strip()
    
    if not all([rpc_url, private_key, contract_address]):
        print("✗ 配置信息不完整，退出测试")
        return
    
    # 测试1: 直接测试上传器
    uploader = test_blockchain_connection(rpc_url, private_key, contract_address)
    if uploader:
        test_upload_data(uploader, express_file, user_file)
    
    # 测试2: 测试管理器
    print("\n" + "=" * 60)
    test_choice = input("是否测试区块链管理器？(y/n): ").strip().lower()
    if test_choice == 'y':
        test_blockchain_manager(rpc_url, private_key, contract_address, express_file, user_file)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()

