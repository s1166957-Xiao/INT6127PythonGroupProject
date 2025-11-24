import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk
import re
from datetime import datetime
import random
from PIL import Image, ImageTk
import os

# 尝试导入 qrcode_load，如果失败则设置为 None
try:
    import qrcode_load
    QRCODE_LOAD_AVAILABLE = True
except (ImportError, FileNotFoundError, OSError) as e:
    qrcode_load = None
    QRCODE_LOAD_AVAILABLE = False
    print(f"警告: qrcode_load 模块不可用，二维码识别功能将被禁用。错误: {e}")

import qrcode_create
from database import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from totp_manager import TOTPManager
from style_manager import tr, CURRENT_LANG

# 尝试导入区块链管理器，如果失败则设置为 None
try:
    from blockchain_manager import BlockchainManager
    BLOCKCHAIN_AVAILABLE = True
except (ImportError, FileNotFoundError) as e:
    BlockchainManager = None
    BLOCKCHAIN_AVAILABLE = False
    print(f"警告: 区块链模块不可用，区块链功能将被禁用。错误: {e}")

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号



CURRENT_LANG = "zh"  # 本来想实现根据系统语言自动切换，但是发现ttk不支持，所以先保留中文
# 全局变量：用户角色
USER_ROLE = "user"  # 可能的值: "user" 或 "admin"



class Person:
    """人物类"""
    def __init__(self, person_id, name):
        self.id = person_id
        self.name = name
    
    def __str__(self):
        return f"{self.name}(ID:{self.id})"

class Express:
    """快递类"""
    def __init__(self, express_id, pick_code, sender, receiver, location, notes, status):
        self.express_id = express_id
        self.pick_code = pick_code
        self.sender = sender  # Person对象
        self.receiver = receiver  # Person对象
        self.location = location
        self.notes = notes
        self.status = status  # 状态：在库/已取件
    
    def __str__(self):
        return (f"快递ID: {self.express_id}, 取件码: {self.pick_code}, "
                f"发件人: {self.sender}, 收件人: {self.receiver}, "
                f"位置: {self.location}, 备注: {self.notes}, 状态: {self.status}")

class QRCodeDialog:
    """二维码显示对话框"""
    def __init__(self, parent, qr_path, express_info):
        self.dialog = tk.Toplevel(parent)
        self.parent = parent
        self.qr_path = qr_path
        self.express_info = express_info
        self.dialog.title("快递二维码")
        
        # 设置对话框大小和位置
        dialog_width = 400
        dialog_height = 800
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 创建信息展示区域
        info_frame = ttk.LabelFrame(self.dialog, text="快递信息")
        info_frame.pack(padx=10, pady=5, fill="x")
        
        # 显示快递信息
        self.info_text = (
            f"快递单号: {express_info['express_id']}\n"
            f"取件码: {express_info['pick_code']}\n"
            f"发件人: {express_info['sender_name']}({express_info['sender']})\n"
            f"收件人: {express_info['receiver_name']}({express_info['receiver']})\n"
            f"位置: {express_info['location']}\n"
            f"备注: {express_info['notes']}"
        )
        tk.Label(info_frame, text=self.info_text, justify=tk.LEFT).pack(padx=5, pady=5)
        
        # 复制信息按钮
        ttk.Button(info_frame, text="复制信息", 
                  command=self.copy_info).pack(pady=5)
        
        # 显示二维码图像
        try:
            # 打开并调整二维码图片大小
            self.img = Image.open(qr_path)
            self.img = self.img.resize((300, 300), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.img)
            
            # 创建图像标签
            qr_label = tk.Label(self.dialog, image=self.photo)
            qr_label.pack(pady=10)
            
            # 图片操作按钮框架
            btn_frame = ttk.Frame(self.dialog)
            btn_frame.pack(pady=5)
            
            ttk.Button(btn_frame, text="另存为...", 
command=self.save_as).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="复制到剪贴板", 
                      command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
            
            # 显示保存位置
            tk.Label(self.dialog, text=f"二维码已保存至:\n{qr_path}", 
                    wraplength=350).pack(pady=5)
            
        except Exception as e:
            tk.Label(self.dialog, text=f"无法加载二维码图片: {str(e)}",
                    fg="red").pack(pady=10)
        
        # 关闭按钮
        ttk.Button(self.dialog, text="关闭", 
                  command=self.dialog.destroy).pack(pady=10)
        
# 设置模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        parent.wait_window(self.dialog)
    
    def save_as(self):
        """另存为对话框"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG图片", "*.png")],
            initialfile=f"快递_{self.express_info['express_id']}.png"
)
        if file_path:
            try:
                self.img.save(file_path)
                messagebox.showinfo("成功", f"二维码已保存至:\n{file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def copy_to_clipboard(self):
        """复制图片到剪贴板"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(self.qr_path)  # 实际上是复制文件路径
            messagebox.showinfo("成功", "二维码图片已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")
    
    def copy_info(self):
        """复制快递信息到剪贴板"""
        try:
            self.parent.clipboard_clear()
            self.parent.clipboard_append(self.info_text)
            messagebox.showinfo("成功", "快递信息已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {str(e)}")

class ExpressManagementSystem:
    """快递管理系统"""
    
    def __init__(self, root):
        self.root = root
        self.user_role = USER_ROLE  # 保存当前用户角色
        title_suffix = "（管理员模式）" if self.user_role == "admin" else "（普通用户模式）"
        self.root.title(f"快递管理系统 {title_suffix}")
        
        # 设置最小窗口大小
        self.root.minsize(800, 600)
        
        # 配置主窗口的网格权重，使其可以自适应调整大小
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 初始化数据库管理器
        self.db = DatabaseManager()
        
        # 初始化TOTP管理器（用于重置安全密钥）
        if self.user_role == "admin":
            self.totp_manager = TOTPManager()
        
        # 初始化区块链管理器（默认禁用）
        if BLOCKCHAIN_AVAILABLE:
            self.blockchain_manager = BlockchainManager(is_enabled=False)
        else:
            self.blockchain_manager = None
        
        # 数据存储（内存缓存）
        self.people_dict = {}  # {person_id: Person对象}
        self.express_dict = {}  # {express_id: Express对象}
        self.pick_code_dict = {}  # {pick_code: express_id}
        
        # 加载数据
        self.load_data()
        
        # 创建界面
        self.create_widgets()
        
        # 更新显示
        if self.user_role == "admin":  # 只有管理员才能看到快递列表
            self.update_express_list()
        
        # 设置窗口大小和位置（居中显示）
        window_width = 1000
        window_height = 800
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置定时刷新（每60秒更新一次数据）
        # self.root.after(60000, self.refresh_data)
        self.after_id = self.root.after(60000, self.refresh_data)
    
    # def init_test_data(self):
    #     """初始化测试数据"""
    #     # 创建测试人物
    #     person1 = Person("P001", "张三")
    #     person2 = Person("P002", "李四")
    #     person3 = Person("P003", "王五")
        
    #     self.people_dict = {
    #         "P001": person1,
    #         "P002": person2,
    #         "P003": person3
    #     }
        
    #     # 创建测试快递
    #     express1 = Express("E001", "123456", person1, person2, "A区1架", "易碎品")
    #     express2 = Express("E002", "654321", person2, person3, "B区2架", "")
        
    #     self.express_dict = {
    #         "E001": express1,
    #         "E002": express2
    #     }
        
    #     self.pick_code_dict = {
    #         "123456": "E001",
    #         "654321": "E002"
    #     }
        
    #     # 更新显示
    #     self.update_express_list()
    
    def load_data(self):
        """从数据库加载所有数据"""
        # 加载用户数据
        users = self.db.get_all_users()
        self.people_dict.clear()
        for user_id, name in users:
            self.people_dict[user_id] = Person(user_id, name)
        
        # 加载快递数据
        expresses = self.db.get_all_express()
        self.express_dict.clear()
        self.pick_code_dict.clear()
        for express_data in expresses:
            (express_id, pick_code, sender_id, receiver_id, area_id, location, 
             notes, status, create_time, update_time, sender_name, 
             receiver_name, area_name) = express_data
            
            # 创建Express对象
            express = Express(
                express_id, 
                pick_code,
                self.people_dict[sender_id],
                self.people_dict[receiver_id],
                location,
                notes,
                status
            )
            
            self.express_dict[express_id] = express
            self.pick_code_dict[pick_code] = express_id
    
    def refresh_data(self):
        """定时刷新数据"""
        self.load_data()
        self.update_express_list()
        self.update_stats()  # 更新统计数据
        # 设置下一次刷新
        self.root.after(60000, self.refresh_data)
            
    def generate_express_id(self):
        """生成唯一的快递ID"""
        return f"E{datetime.now().strftime('%Y%m%d%H%M%S%f')[:15]}"
    
    def generate_pick_code(self):
        """生成唯一的6位数字取件码"""
        while True:
            # 生成6位随机数
            code = random.randint(100000, 999999)
            # 确保取件码不重复
            if code not in self.pick_code_dict:
                return str(code)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建标签页
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.grid(row=0, column=0, sticky="nsew")
        
        # 创建所有标签页，但只为管理员创建特殊页面
        if self.user_role == "admin":
            self.create_all_tabs()
            
            # 设置各标签页的内容
            self.setup_in_tab()
            self.setup_out_tab()
            self.setup_query_tab()
            self.setup_list_tab()
            self.setup_users_tab()
            self.setup_stats_tab()
            
            # 为管理员添加额外的菜单
            # self.create_admin_menu() # This method does not exist and seems redundant
        else:
            # 普通用户只创建必要的标签页
            self.tab_out = ttk.Frame(self.tab_control)
            self.tab_control.add(self.tab_out, text="快递取件")
            self.tab_out.grid_columnconfigure(0, weight=1)
            
            self.tab_query = ttk.Frame(self.tab_control)
            self.tab_control.add(self.tab_query, text="快递查询")
            self.tab_query.grid_columnconfigure(0, weight=1)
            
            # 设置普通用户可用的标签页
            self.setup_out_tab()
            self.setup_query_tab()
            
            # 显示提示信息
            messagebox.showinfo("普通用户模式", 
                "您已进入普通用户模式。\n"
                "可以使用快递取件和查询功能。")

    def change_language(self, lang):
        from style_manager import CURRENT_LANG
        CURRENT_LANG = lang
        self.refresh_ui()

    def refresh_ui(self):
        # 重新设置所有控件文本
        # self.update_title()  # 方法不存在，暂时注释
        self.create_menu_bar()
        # 其他界面控件也可遍历刷新
    
    def create_all_tabs(self):
        """创建所有标签页"""
        # 入库标签页
        self.tab_in = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_in, text="快递入库")
        self.tab_in.grid_columnconfigure(0, weight=1)
        
        # 取件标签页
        self.tab_out = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_out, text="快递取件")
        self.tab_out.grid_columnconfigure(0, weight=1)
        
        # 查询标签页
        self.tab_query = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_query, text="快递查询")
        self.tab_query.grid_columnconfigure(0, weight=1)
        
        # 列表标签页
        self.tab_list = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_list, text="快递列表")
        self.tab_list.grid_columnconfigure(0, weight=1)
        self.tab_list.grid_rowconfigure(0, weight=1)
        
        # 用户管理标签页
        self.tab_users = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_users, text="用户管理")
        self.tab_users.grid_columnconfigure(0, weight=1)
        self.tab_users.grid_rowconfigure(0, weight=1)
        
        # 数据统计标签页
        self.tab_stats = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_stats, text="数据统计")
        self.tab_stats.grid_columnconfigure(0, weight=1)
        self.tab_stats.grid_rowconfigure(1, weight=1)
    
    def apply_user_restrictions(self):
        """应用普通用户的权限限制"""
        # 删除管理员专用标签页和相关变量
        admin_tabs = [self.tab_in, self.tab_list, self.tab_users, self.tab_stats]
        for tab in admin_tabs:
            self.tab_control.forget(tab)
            # 确保删除所有对标签页的引用
            if hasattr(self, 'express_tree'):
                delattr(self, 'express_tree')
            if hasattr(self, 'users_tree'):
                delattr(self, 'users_tree')
            if hasattr(self, 'stat_labels'):
                delattr(self, 'stat_labels')
            if hasattr(self, 'figure'):
                delattr(self, 'figure')
            if hasattr(self, 'canvas'):
                delattr(self, 'canvas')
        
        # 选中取件标签页作为默认显示
        self.tab_control.select(self.tab_out)
        
        # 禁用不必要的更新
        try:
            self.root.after_cancel(self.after_id)
        except AttributeError:
            pass
        
        # 显示提示信息
        messagebox.showinfo("普通用户模式", 
            "您已进入普通用户模式。\n"
            "可以使用快递取件和查询功能。")
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 系统菜单
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="系统", menu=system_menu)
        system_menu.add_command(label="退出登录", command=self.logout)
        system_menu.add_separator()
        system_menu.add_command(label="退出程序", command=self.exit_program)
        
        # 主题菜单
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="主题", menu=theme_menu)
        # 主题名称映射：显示名称 -> 实际主题名称
        themes = {
            "arc弧光纪": "arc",
            "plastik塑境集": "plastik",
            "clearlooks清透观": "clearlooks",
            "radiance焕光录": "radiance",
            "equilux衡光赋": "equilux",
            "breeze清飔集": "breeze",
            "black墨韵调": "black"
        }
        for display_name, theme_name in themes.items():
            theme_menu.add_command(label=display_name, 
                                 command=lambda t=theme_name: self.change_theme(t))

        if self.user_role == "admin":
            # 创建仓库菜单
            warehouse_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="仓库", menu=warehouse_menu)
            
            # 添加仓库区域管理选项
            from area_dialog import AreaDialog
            warehouse_menu.add_command(label="区域管理", 
                                     command=lambda: AreaDialog(self.root, self.db))
            
            # 创建安全菜单（仅管理员可见）
            security_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="安全", menu=security_menu)
            
            # 添加重置TOTP密钥选项
            security_menu.add_command(label="重置安全密钥", 
                                    command=self.reset_security_key)
            
            # 创建区块链菜单（仅管理员可见）
            if BLOCKCHAIN_AVAILABLE:
                blockchain_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="区块链", menu=blockchain_menu)
                
                # 添加区块链配置选项
                blockchain_menu.add_command(label="配置区块链", 
                                           command=self.configure_blockchain)
                blockchain_menu.add_separator()
                blockchain_menu.add_command(label="上传所有数据到区块链", 
                                           command=self.upload_all_to_blockchain)
                blockchain_menu.add_command(label="上传快递数据到区块链", 
                                           command=self.upload_express_to_blockchain)
                blockchain_menu.add_command(label="上传用户数据到区块链", 
                                           command=self.upload_users_to_blockchain)
                blockchain_menu.add_separator()
                blockchain_menu.add_command(label="查看上链统计", 
                                           command=self.show_blockchain_stats)
                blockchain_menu.add_command(label="查看运行状态", 
                                           command=self.show_blockchain_status)
    
    def logout(self):
        """退出登录"""
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.root.destroy()  # 关闭当前窗口
    
    def exit_program(self):
        """退出程序"""
        if messagebox.askyesno("确认", "确定要退出程序吗？"):
            self._exit_program = True  # 标记是通过退出程序关闭的
            self.root.quit()
    
    def reset_security_key(self):
        """重置TOTP安全密钥"""
        if messagebox.askyesno("确认", 
            "确定要重置安全密钥吗？\n重置后需要重新配置您的身份验证器。"):
            # 生成新的密钥
            new_secret = self.totp_manager.generate_new_secret()
            
            # 显示成功消息
            messagebox.showinfo("密钥已重置", 
                f"新的安全密钥已生成。\n"
                f"请扫描即将显示的二维码以重新配置您的身份验证器。")
            
            # 显示配置对话框（强制显示设置界面）
            from dialogs import AdminLoginDialog
            AdminLoginDialog(self.root, self.totp_manager, force_setup=True)
    
    def configure_blockchain(self):
        """配置区块链连接"""
        if not BLOCKCHAIN_AVAILABLE or self.blockchain_manager is None:
            messagebox.showerror("错误", "区块链模块不可用，请检查依赖是否已安装。")
            return
        
        # 创建配置对话框
        config_dialog = tk.Toplevel(self.root)
        config_dialog.title("区块链配置")
        config_dialog.geometry("500x300")
        config_dialog.transient(self.root)
        config_dialog.grab_set()
        
        # RPC URL
        ttk.Label(config_dialog, text="RPC URL:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        rpc_entry = ttk.Entry(config_dialog, width=50)
        rpc_entry.grid(row=0, column=1, padx=10, pady=10)
        rpc_entry.insert(0, "http://localhost:8545")  # 默认值
        
        # 私钥
        ttk.Label(config_dialog, text="私钥:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        private_key_entry = ttk.Entry(config_dialog, width=50, show="*")
        private_key_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # 合约地址
        ttk.Label(config_dialog, text="合约地址:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        contract_entry = ttk.Entry(config_dialog, width=50)
        contract_entry.grid(row=2, column=1, padx=10, pady=10)
        
        def save_config():
            rpc_url = rpc_entry.get().strip()
            private_key = private_key_entry.get().strip()
            contract_address = contract_entry.get().strip()
            
            if not all([rpc_url, private_key, contract_address]):
                messagebox.showerror("错误", "请填写所有配置项！")
                return
            
            if self.blockchain_manager.configure(rpc_url, private_key, contract_address):
                messagebox.showinfo("成功", "区块链配置成功！")
                config_dialog.destroy()
            else:
                error_msg = self.blockchain_manager.last_error or "未知错误"
                messagebox.showerror("错误", f"配置失败：{error_msg}")
        
        # 按钮
        btn_frame = ttk.Frame(config_dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="保存", command=save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=config_dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def export_to_excel(self, data_type="express"):
        """导出数据到Excel文件"""
        import pandas as pd
        from datetime import datetime
        
        # 检查openpyxl是否安装
        try:
            import openpyxl
        except ImportError:
            messagebox.showerror(
                "缺少依赖", 
                "导出Excel功能需要openpyxl库。\n\n"
                "请运行以下命令安装：\n"
                "pip install openpyxl\n\n"
                "或在项目目录运行：\n"
                "pip install -r requirements.txt"
            )
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if data_type == "express":
            # 导出快递数据
            expresses = self.db.get_all_express()
            if not expresses:
                messagebox.showwarning("警告", "没有快递数据可导出。")
                return None
            
            data = []
            for express_data in expresses:
                (express_id, pick_code, sender_id, receiver_id, area_id, location, 
                 notes, status, create_time, update_time, sender_name, 
                 receiver_name, area_name) = express_data
                data.append({
                    "快递单号": express_id,
                    "取件码": pick_code,
                    "发件人ID": sender_id,
                    "发件人姓名": sender_name,
                    "收件人ID": receiver_id,
                    "收件人姓名": receiver_name,
                    "区域ID": area_id,
                    "区域名称": area_name,
                    "位置": location,
                    "备注": notes,
                    "状态": status,
                    "创建时间": create_time,
                    "更新时间": update_time
                })
            
            df = pd.DataFrame(data)
            file_path = f"express_{timestamp}.xlsx"
            df.to_excel(file_path, index=False)
            return file_path
        
        elif data_type == "user":
            # 导出用户数据
            users = self.db.get_all_users()
            if not users:
                messagebox.showwarning("警告", "没有用户数据可导出。")
                return None
            
            data = []
            for user_id, name in users:
                data.append({
                    "用户ID": user_id,
                    "姓名": name
                })
            
            df = pd.DataFrame(data)
            file_path = f"user_{timestamp}.xlsx"
            df.to_excel(file_path, index=False)
            return file_path
        
        return None
    
    def upload_all_to_blockchain(self):
        """上传所有数据到区块链"""
        if not BLOCKCHAIN_AVAILABLE or self.blockchain_manager is None:
            messagebox.showerror("错误", "区块链模块不可用。")
            return
        
        if not self.blockchain_manager.is_enabled:
            messagebox.showwarning("警告", "请先配置区块链连接。")
            self.configure_blockchain()
            return
        
        # 导出数据
        express_file = self.export_to_excel("express")
        user_file = self.export_to_excel("user")
        
        if not express_file or not user_file:
            return
        
        # 显示上传进度提示
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("上传中...")
        progress_dialog.geometry("300x100")
        progress_dialog.transient(self.root)
        progress_label = ttk.Label(progress_dialog, text="正在上传数据到区块链，请稍候...")
        progress_label.pack(pady=20)
        
        def upload_callback(success, results):
            progress_dialog.destroy()
            if success:
                # 获取快递数据的图片路径（优先使用快递数据的图片）
                image_path = None
                if isinstance(results, dict):
                    express_result = results.get("express", {})
                    if isinstance(express_result, dict):
                        image_path = express_result.get("image_path")
                
                # 创建自定义成功对话框，显示消息和图片
                success_dialog = tk.Toplevel(self.root)
                success_dialog.title("成功")
                success_dialog.transient(self.root)
                success_dialog.grab_set()
                
                # 检查图片是否存在
                has_image = image_path and os.path.exists(image_path)
                
                # 设置对话框大小和位置（根据是否有图片调整）
                dialog_width = 400
                dialog_height = 400 if has_image else 150
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = (screen_width - dialog_width) // 2
                y = (screen_height - dialog_height) // 2
                success_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
                
                # 设置对话框背景色
                success_dialog.configure(bg='white')
                
                # 显示成功消息（使用tk.Label避免灰色底纹）
                message_label = tk.Label(success_dialog, text="快递数据上链成功", 
                                         font=("Arial", 14, "bold"),
                                         bg='white', fg='black')
                message_label.pack(pady=20)
                
                # 显示图片（如果存在）
                if has_image:
                    try:
                        img = Image.open(image_path)
                        # 调整图片大小以适应对话框
                        img.thumbnail((250, 250), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label = tk.Label(success_dialog, image=photo, bg='white')
                        img_label.image = photo  # 保持引用
                        img_label.pack(pady=10)
                    except Exception as e:
                        print(f"[WARNING] 无法加载图片: {str(e)}")
                
                # 关闭按钮（使用tk.Button确保文字显示）
                close_button = tk.Button(success_dialog, text="确定", 
                                        command=success_dialog.destroy,
                                        bg='#f0f0f0', fg='black',
                                        font=("Arial", 10),
                                        width=10, height=1)
                close_button.pack(pady=20)
            else:
                error_msg = results.get('error', '未知错误') if isinstance(results, dict) else '未知错误'
                messagebox.showerror("失败", f"数据上传失败：{error_msg}")
        
        # 异步上传
        self.blockchain_manager.upload_all_data_async(express_file, user_file, upload_callback)
    
    def upload_express_to_blockchain(self):
        """上传快递数据到区块链"""
        if not BLOCKCHAIN_AVAILABLE or self.blockchain_manager is None:
            messagebox.showerror("错误", "区块链模块不可用。")
            return
        
        if not self.blockchain_manager.is_enabled:
            messagebox.showwarning("警告", "请先配置区块链连接。")
            self.configure_blockchain()
            return
        
        express_file = self.export_to_excel("express")
        if not express_file:
            return
        
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("上传中...")
        progress_dialog.geometry("300x100")
        progress_dialog.transient(self.root)
        progress_label = ttk.Label(progress_dialog, text="正在上传快递数据到区块链，请稍候...")
        progress_label.pack(pady=20)
        
        def upload_callback(success, image_path):
            progress_dialog.destroy()
            if success:
                # 创建自定义成功对话框，显示消息和图片
                success_dialog = tk.Toplevel(self.root)
                success_dialog.title("成功")
                success_dialog.transient(self.root)
                success_dialog.grab_set()
                
                # 检查图片是否存在
                has_image = image_path and os.path.exists(image_path)
                
                # 设置对话框大小和位置（根据是否有图片调整）
                dialog_width = 400
                dialog_height = 400 if has_image else 150
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = (screen_width - dialog_width) // 2
                y = (screen_height - dialog_height) // 2
                success_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
                
                # 设置对话框背景色
                success_dialog.configure(bg='white')
                
                # 显示成功消息（使用tk.Label避免灰色底纹）
                message_label = tk.Label(success_dialog, text="快递数据上链成功", 
                                         font=("Arial", 14, "bold"),
                                         bg='white', fg='black')
                message_label.pack(pady=20)
                
                # 显示图片（如果存在）
                if has_image:
                    try:
                        img = Image.open(image_path)
                        # 调整图片大小以适应对话框
                        img.thumbnail((250, 250), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label = tk.Label(success_dialog, image=photo, bg='white')
                        img_label.image = photo  # 保持引用
                        img_label.pack(pady=10)
                    except Exception as e:
                        print(f"[WARNING] 无法加载图片: {str(e)}")
                
                # 关闭按钮（使用tk.Button确保文字显示）
                close_button = tk.Button(success_dialog, text="确定", 
                                        command=success_dialog.destroy,
                                        bg='#f0f0f0', fg='black',
                                        font=("Arial", 10),
                                        width=10, height=1)
                close_button.pack(pady=20)
            else:
                messagebox.showerror("失败", "快递数据上传失败。")
        
        self.blockchain_manager.upload_express_data_async(express_file, upload_callback)
    
    def upload_users_to_blockchain(self):
        """上传用户数据到区块链"""
        if not BLOCKCHAIN_AVAILABLE or self.blockchain_manager is None:
            messagebox.showerror("错误", "区块链模块不可用。")
            return
        
        if not self.blockchain_manager.is_enabled:
            messagebox.showwarning("警告", "请先配置区块链连接。")
            self.configure_blockchain()
            return
        
        user_file = self.export_to_excel("user")
        if not user_file:
            return
        
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("上传中...")
        progress_dialog.geometry("300x100")
        progress_dialog.transient(self.root)
        progress_label = ttk.Label(progress_dialog, text="正在上传用户数据到区块链，请稍候...")
        progress_label.pack(pady=20)
        
        def upload_callback(success, image_path):
            progress_dialog.destroy()
            if success:
                # 创建自定义成功对话框，显示消息和图片
                success_dialog = tk.Toplevel(self.root)
                success_dialog.title("成功")
                success_dialog.transient(self.root)
                success_dialog.grab_set()
                
                # 检查图片是否存在
                has_image = image_path and os.path.exists(image_path)
                
                # 设置对话框大小和位置（根据是否有图片调整）
                dialog_width = 400
                dialog_height = 400 if has_image else 150
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = (screen_width - dialog_width) // 2
                y = (screen_height - dialog_height) // 2
                success_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
                
                # 设置对话框背景色
                success_dialog.configure(bg='white')
                
                # 显示成功消息（使用tk.Label避免灰色底纹）
                message_label = tk.Label(success_dialog, text="用户数据上链成功", 
                                         font=("Arial", 14, "bold"),
                                         bg='white', fg='black')
                message_label.pack(pady=20)
                
                # 显示图片（如果存在）
                if has_image:
                    try:
                        img = Image.open(image_path)
                        # 调整图片大小以适应对话框
                        img.thumbnail((250, 250), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label = tk.Label(success_dialog, image=photo, bg='white')
                        img_label.image = photo  # 保持引用
                        img_label.pack(pady=10)
                    except Exception as e:
                        print(f"[WARNING] 无法加载图片: {str(e)}")
                
                # 关闭按钮（使用tk.Button确保文字显示）
                close_button = tk.Button(success_dialog, text="确定", 
                                        command=success_dialog.destroy,
                                        bg='#f0f0f0', fg='black',
                                        font=("Arial", 10),
                                        width=10, height=1)
                close_button.pack(pady=20)
            else:
                messagebox.showerror("失败", "用户数据上传失败。")
        
        self.blockchain_manager.upload_user_data_async(user_file, upload_callback)
    
    def show_blockchain_stats(self):
        """显示区块链上链统计"""
        if not BLOCKCHAIN_AVAILABLE or self.blockchain_manager is None:
            messagebox.showerror("错误", "区块链模块不可用。")
            return
        
        if not self.blockchain_manager.is_enabled:
            messagebox.showwarning("警告", "请先配置区块链连接。")
            self.configure_blockchain()
            return
        
        stats = self.blockchain_manager.get_statistics()
        messagebox.showinfo("上链统计", f"总上链次数: {stats}")
        
    
    def show_blockchain_status(self):
        """显示区块链运行状态"""
        if not BLOCKCHAIN_AVAILABLE or self.blockchain_manager is None:
            messagebox.showerror("错误", "区块链模块不可用。")
            return
        
        status = self.blockchain_manager.get_status_info()
        is_running = self.blockchain_manager.is_running()
        running_count = self.blockchain_manager.get_running_count()
        
        status_text = f"""区块链状态信息：

启用状态: {'已启用' if status['is_enabled'] else '未启用'}
运行状态: {'正在运行' if is_running else '空闲'}
运行任务数: {running_count}
上传器状态: {'已配置' if status['has_uploader'] else '未配置'}
"""
        
        if status['last_error']:
            status_text += f"\n最后错误: {status['last_error']}"
        
        if is_running:
            status_text += f"\n\n提示: 当前有 {running_count} 个上传任务正在后台运行。"
        
        messagebox.showinfo("区块链运行状态", status_text)
    
    def setup_in_tab(self):
        """设置入库标签页"""
        # 创建信息展示区域
        info_frame = ttk.LabelFrame(self.tab_in, text="快递信息")
        info_frame.pack(padx=10, pady=5, fill="x")
        
        # 快递ID展示（只读）
        tk.Label(info_frame, text="快递ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.express_id_label = tk.Label(info_frame, text="<自动生成>", width=30, relief="sunken", bg="lightgray")
        self.express_id_label.grid(row=0, column=1, padx=5, pady=5)
        
        # 取件码展示（只读）
        tk.Label(info_frame, text="取件码:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pick_code_label = tk.Label(info_frame, text="<自动生成>", width=30, relief="sunken", bg="lightgray")
        self.pick_code_label.grid(row=1, column=1, padx=5, pady=5)
        
        # 发件人ID
        tk.Label(info_frame, text="发件人ID:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.sender_id_entry = tk.Entry(info_frame, width=30)
        self.sender_id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 发件人姓名
        tk.Label(info_frame, text="发件人姓名:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.sender_name_entry = tk.Entry(info_frame, width=30)
        self.sender_name_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 收件人ID
        tk.Label(info_frame, text="收件人ID:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.receiver_id_entry = tk.Entry(info_frame, width=30)
        self.receiver_id_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # 收件人姓名
        tk.Label(info_frame, text="收件人姓名:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.receiver_name_entry = tk.Entry(info_frame, width=30)
        self.receiver_name_entry.grid(row=5, column=1, padx=5, pady=5)
        
        # 仓库区域
        tk.Label(info_frame, text="仓库区域:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.area_combobox = ttk.Combobox(info_frame, width=27, state="readonly")
        self.area_combobox.grid(row=6, column=1, padx=5, pady=5)
        self.area_combobox.bind("<<ComboboxSelected>>", self.update_location_list)
        
        # 摆放位置
        tk.Label(info_frame, text="摆放位置:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.location_combobox = ttk.Combobox(info_frame, width=27)
        self.location_combobox.grid(row=7, column=1, padx=5, pady=5)
        
        # 备注
        tk.Label(info_frame, text="备注:").grid(row=8, column=0, padx=5, pady=5, sticky="e")
        self.notes_entry = tk.Entry(info_frame, width=30)
        self.notes_entry.grid(row=8, column=1, padx=5, pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(self.tab_in)
        button_frame.pack(pady=10)
        
        # 入库按钮
        tk.Button(button_frame, text="入库", command=self.add_express, 
                 bg="lightgreen", width=15).pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        tk.Button(button_frame, text="清空", command=self.clear_in_fields, 
                 bg="lightyellow", width=15).pack(side=tk.LEFT, padx=5)
        
        # QR码解析按钮
        tk.Button(button_frame, text="QR码解析", command=self.qr_read, 
                 bg="lightblue", width=15).pack(side=tk.LEFT, padx=5)
        
        # 加载仓库区域列表
        self.update_area_list()
    def setup_out_tab(self):
        """设置取件标签页"""
        # 创建框架来组织按钮
        button_frame = tk.Frame(self.tab_out)
        button_frame.pack(pady=10)
        
        tk.Label(self.tab_out, text="请输入取件码或扫描快递二维码:").pack(pady=10)
        
        self.pick_code_out_entry = tk.Entry(self.tab_out, width=30, font=("Arial", 14))
        self.pick_code_out_entry.pack(pady=10)
        # 在同一行放置两个按钮
        tk.Button(button_frame, text="取件", command=self.pick_up_express, 
                 bg="lightcoral", width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="扫描二维码", command=self.qr_read_for_pickup,
                 bg="lightblue", width=15, height=2).pack(side=tk.LEFT, padx=5)
        
        # 结果显示
        self.result_label = tk.Label(self.tab_out, text="", font=("Arial", 12), fg="blue")
        self.result_label.pack(pady=10)
    
    def setup_query_tab(self):
        """设置查询标签页"""
        # 配置查询页面的网格
        self.tab_query.grid_rowconfigure(2, weight=1)  # 文本框所在行可以拉伸
        self.tab_query.grid_columnconfigure(0, weight=1)
        
        # 标签
        label = tk.Label(self.tab_query, text="请输入查询条件(快递ID/发件人ID/收件人ID)或扫描快递二维码:")
        label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        # 创建输入区域框架
        input_frame = ttk.Frame(self.tab_query)
        input_frame.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)  # 让输入框可以横向拉伸
        
        # 查询输入框和按钮
        self.query_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.query_entry.grid(row=0, column=0, padx=(0, 5))
        
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky="e")
        
        ttk.Button(button_frame, text="查询", 
                  command=self.query_express).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="扫描二维码",
                  command=self.qr_read_for_query).pack(side=tk.LEFT, padx=5)
        
        # 创建文本框框架
        text_frame = ttk.Frame(self.tab_query)
        text_frame.grid(row=2, column=0, pady=5, padx=10, sticky="nsew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # 查询结果文本框
        self.query_result_text = tk.Text(text_frame)
        self.query_result_text.grid(row=0, column=0, sticky="nsew")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", 
                                command=self.query_result_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.query_result_text.config(yscrollcommand=scrollbar.set)
    
    def setup_list_tab(self):
        """设置快递列表标签页"""
        # 创建树形视图显示快递列表
        columns = ("快递ID", "取件码", "发件人", "收件人", "位置", "备注", "状态")
        self.express_tree = ttk.Treeview(self.tab_list, columns=columns, show="headings", height=20)
        
        # 设置列标题和排序功能
        for col in columns:
            self.express_tree.heading(col, text=col, 
                                    command=lambda c=col: self.sort_treeview(c, False))
            self.express_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.tab_list, orient="vertical", command=self.express_tree.yview)
        self.express_tree.configure(yscrollcommand=scrollbar.set)
        
        # 使用网格布局来组织树形视图和滚动条
        self.express_tree.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        scrollbar.grid(row=0, column=1, pady=10, sticky="ns")
        
        # 设置网格布局的权重
        self.tab_list.grid_columnconfigure(0, weight=1)
        self.tab_list.grid_rowconfigure(0, weight=1)
        
        # 刷新按钮
        tk.Button(self.tab_list, text="刷新列表", command=self.update_express_list).grid(
            row=1, column=0, columnspan=2, pady=5)
        
        # 用于跟踪排序状态
        self.sort_state = {"column": None, "reverse": False}
    
    def add_express(self):
        """添加快递入库"""
        # 生成快递ID和取件码
        express_id = self.generate_express_id()
        pick_code = self.generate_pick_code()
        
        # 获取其他输入数据
        sender_id = self.sender_id_entry.get().strip()
        sender_name = self.sender_name_entry.get().strip()
        receiver_id = self.receiver_id_entry.get().strip()
        receiver_name = self.receiver_name_entry.get().strip()
        area_str = self.area_combobox.get()
        location = self.location_combobox.get().strip()
        notes = self.notes_entry.get().strip()
        status = "在库"
        
        # 验证必填字段
        if not all([sender_id, sender_name, receiver_id, receiver_name, area_str, location]):
            messagebox.showerror("错误", "请填写所有必填字段！")
            return
        
        # 从选择的文本中提取区域ID
        area_id = area_str.split("(")[1].rstrip(")")
        
        # 检查区域容量
        area_info = self.db.get_area_capacity_info(area_id)
        if area_info:
            _, _, capacity, used_capacity = area_info
            if used_capacity >= capacity:
                messagebox.showerror("错误", f"区域 {area_str} 已满！")
                return
        else:
            messagebox.showerror("错误", f"区域 {area_str} 不存在！")
            return
        
        # 创建或更新发件人
        if sender_id in self.people_dict:
            # 更新现有发件人姓名（如果有变化）
            if self.people_dict[sender_id].name != sender_name:
                self.people_dict[sender_id].name = sender_name
                self.db.update_user(sender_id, sender_name)
        else:
            # 创建新发件人
            self.people_dict[sender_id] = Person(sender_id, sender_name)
            self.db.add_user(sender_id, sender_name)
        
        # 创建或更新收件人
        if receiver_id in self.people_dict:
            # 更新现有收件人姓名（如果有变化）
            if self.people_dict[receiver_id].name != receiver_name:
                self.people_dict[receiver_id].name = receiver_name
                self.db.update_user(receiver_id, receiver_name)
        else:
            # 创建新收件人
            self.people_dict[receiver_id] = Person(receiver_id, receiver_name)
            self.db.add_user(receiver_id, receiver_name)
        
        # 创建快递对象
        sender = self.people_dict[sender_id]
        receiver = self.people_dict[receiver_id]
        full_location = f"{area_str} {location}"
        express = Express(express_id, pick_code, sender, receiver, full_location, notes, status)
        
        # 添加到数据库
        if not self.db.add_express(express_id, pick_code, sender_id, receiver_id, area_id,
                              full_location, notes, status):
            messagebox.showerror("错误", "保存快递信息失败！")
            return
            
        # 更新内存缓存
        self.express_dict[express_id] = express
        self.pick_code_dict[pick_code] = express_id
        
        # 更新显示
        self.update_express_list()
        self.update_stats()  # 更新统计数据
        
        # 生成快递二维码
        express_info = {
            'express_id': express_id,
            'pick_code': pick_code,
            'sender': sender_id,
            'sender_name': sender_name,
            'receiver': receiver_id,
            'receiver_name': receiver_name,
            'location': full_location,
            'notes': notes
        }
        
        qr_path, _ = qrcode_create.generate_qr_code(express_info)
        
        # 如果区块链已配置，在后台自动上传快递数据（可选，不阻塞UI）
        if (BLOCKCHAIN_AVAILABLE and self.blockchain_manager and 
            self.blockchain_manager.is_enabled):
            # 异步上传，不显示进度对话框，静默执行
            def silent_upload():
                try:
                    express_file = self.export_to_excel("express")
                    if express_file:
                        print(f"[区块链] 自动上传快递数据: {express_file}")
                        self.blockchain_manager.upload_express_data_async(express_file, None)
                except Exception as e:
                    print(f"[区块链] 自动上传失败: {str(e)}")
            import threading
            threading.Thread(target=silent_upload, daemon=True).start()

    def change_theme(self, theme_name):
        """一键切换主题"""
        try:
            # ThemedTk 的 set_theme 方法
            if hasattr(self.root, "set_theme"):
                self.root.set_theme(theme_name)
            else:
                # 兼容普通 Tk，不做处理
                messagebox.showinfo("提示", "当前窗口不支持主题切换，请使用 ThemedTk 启动程序。")
        except Exception as e:
            messagebox.showerror("错误", f"切换主题失败：{str(e)}")
    def pick_up_express(self):
        """快递取件"""
        pick_code = self.pick_code_out_entry.get().strip()
        
        if not pick_code:
            messagebox.showerror("错误", "请输入取件码！")
            return
            
        try:
            pick_code = int(pick_code)
        except ValueError:
            messagebox.showerror("错误", "取件码必须是数字！")
            return
            
        # 查找快递
        if str(pick_code) in self.pick_code_dict:
            express_id = self.pick_code_dict[str(pick_code)]
            express = self.express_dict[express_id]
            
            if express.status == "已取件":
                self.result_label.config(text="该快递已被取走！", fg="red")
                return
                
            # 显示确认对话框
            confirm = messagebox.askyesno("确认取件", 
                f"确认要取走以下快递吗？\n\n"
                f"快递单号：{express_id}\n"
                f"发件人：{express.sender.name}\n"
                f"收件人：{express.receiver.name}\n"
                f"位置：{express.location}")
                
            if not confirm:
                return
                
            # 更新数据库状态
            if not self.db.update_express_status(express_id, "已取件"):
                messagebox.showerror("错误", "更新快递状态失败！")
                return
# 更新内存状态
            express.status = "已取件"
            
            # 显示成功信息
            result_text = f"取件成功，请与【{express.location}】取走您的快递！"
            self.result_label.config(text=result_text, fg="green")
            self.pick_code_out_entry.delete(0, tk.END)  # 清空输入框
            
            # 更新显示和统计
            self.update_express_list()
            self.update_stats()
            
            # 如果区块链已配置，在后台自动上传更新后的快递数据（可选，不阻塞UI）
            if (BLOCKCHAIN_AVAILABLE and self.blockchain_manager and 
                self.blockchain_manager.is_enabled):
                # 异步上传，不显示进度对话框，静默执行
                def silent_upload():
                    try:
                        express_file = self.export_to_excel("express")
                        if express_file:
                            print(f"[区块链] 自动上传更新后的快递数据: {express_file}")
                            self.blockchain_manager.upload_express_data_async(express_file, None)
                    except Exception as e:
                        print(f"[区块链] 自动上传失败: {str(e)}")
                import threading
                threading.Thread(target=silent_upload, daemon=True).start()
        else:
            self.result_label.config(text="取件码错误，请重新输入！", fg="red")
    
    def query_express(self):
        """查询快递"""
        query_text = self.query_entry.get().strip()
        
        if not query_text:
            messagebox.showerror("错误", "请输入查询条件！")
            return
        
        # 清空之前的查询结果
        self.query_result_text.delete(1.0, tk.END)
        
        # 查找匹配的快递
        results = []
        for express in self.express_dict.values():
            if (query_text == express.express_id or 
                query_text == express.sender.id or 
                query_text == express.receiver.id):
                results.append(express)
        
        # 显示结果
        if results:
            self.query_result_text.insert(tk.END, f"找到 {len(results)} 个匹配的快递：\n\n")
            for express in results:
                self.query_result_text.insert(tk.END, f"{express}\n\n")
        else:
            self.query_result_text.insert(tk.END, "未找到匹配的快递！")
    
    def update_express_list(self):
        """更新快递列表显示"""
        # 只有管理员才能更新快递列表
        if self.user_role != "admin" or not hasattr(self, 'express_tree'):
            return
            
        # 清空现有列表
        for item in self.express_tree.get_children():
            self.express_tree.delete(item)
        
        # 添加快递数据
        for express in self.express_dict.values():
            self.express_tree.insert("", tk.END, values=(
                express.express_id,
                express.pick_code,
                f"{express.sender.name}({express.sender.id})",
                f"{express.receiver.name}({express.receiver.id})",
                express.location,
                express.notes,
                express.status
            ))
    
    def clear_in_fields(self):
        """清空入库输入框"""
        self.express_id_label.config(text="<自动生成>")
        self.pick_code_label.config(text="<自动生成>")
        self.sender_id_entry.delete(0, tk.END)
        self.sender_name_entry.delete(0, tk.END)
        self.receiver_id_entry.delete(0, tk.END)
        self.receiver_name_entry.delete(0, tk.END)
        self.area_combobox.set("")
        self.location_combobox.set("")
        self.notes_entry.delete(0, tk.END)
    
    def update_area_list(self):
        """更新仓库区域列表"""
        try:
            areas = self.db.get_all_areas()
            self.area_combobox['values'] = [f"{area[1]} ({area[0]})" for area in areas]
            
            # 更新图表数据
            self.update_storage_chart(areas)
            
        except Exception as e:
            messagebox.showerror("错误", f"加载仓库区域失败: {str(e)}")

    def update_location_list(self, event=None):
        """根据选择的区域更新位置列表"""
        try:
            selected_area_str = self.area_combobox.get()
            if not selected_area_str:
                return
            
            area_id = selected_area_str.split('(')[-1].replace(')', '')
            
            # 从数据库获取区域的详细信息
            areas = self.db.get_all_areas()
            area_info = next((area for area in areas if area[0] == area_id), None)
            
            if not area_info:
                self.location_combobox['values'] = []
                return
            
            capacity = area_info[2]
            used_locations = area_info[5].split(',') if area_info[5] else []
            
            # 生成所有可能的位置
            all_locations = [f"货位 {i+1}" for i in range(capacity)]
            
            # 筛选出可用的位置
            available_locations = [loc for loc in all_locations if loc not in used_locations]
            
            self.location_combobox['values'] = available_locations
            if available_locations:
                self.location_combobox.set(available_locations[0])
            else:
                self.location_combobox.set("该区域已满")
                
        except Exception as e:
            messagebox.showerror("错误", f"加载位置列表失败: {str(e)}")

    def update_storage_chart(self, areas=None):
        """更新仓储图表"""
        if areas is None:
            areas = self.db.get_all_areas()
        
        if not hasattr(self, 'storage_ax'):
            return # 如果图表还没创建，就先不更新
            
        self.storage_ax.clear()
        
        area_names = [area[1] for area in areas]
        capacities = [area[2] for area in areas]
        current_items = [area[4] for area in areas]
        
        colors = ['skyblue', 'lightgreen', 'lightcoral', 'gold']
        
        # 绘制条形图
        bars = self.storage_ax.bar(area_names, capacities, color=[c + 'a0' for c in colors], label='总容量')
        used_bars = self.storage_ax.bar(area_names, current_items, color=colors, label='已使用')
        
        # 添加标签
        self.storage_ax.set_ylabel('数量')
        self.storage_ax.set_title('各区域仓储情况')
        self.storage_ax.legend()
        
        # 在条形图上显示数值
        for bar, used in zip(bars, current_items):
            height = bar.get_height()
            self.storage_ax.text(bar.get_x() + bar.get_width() / 2.0, height, 
                               f'{used}/{height}', ha='center', va='bottom')
        
        self.storage_canvas.draw()
    
    def show_area_dialog(self):
        """显示仓库区域管理对话框"""
        from area_dialog import AreaDialog
        AreaDialog(self.root, self.db)
        
    def setup_users_tab(self):
        """设置用户管理标签页"""
        # 创建左侧的用户列表框架
        list_frame = ttk.LabelFrame(self.tab_users, text="用户列表")
        list_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # 创建用户列表的Treeview
        columns = ("用户ID", "用户姓名")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # 设置列标题和排序功能
        for col in columns:
            self.users_tree.heading(col, text=col, 
                                  command=lambda c=col: self.sort_users(c, False))
            self.users_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置Treeview和滚动条
        self.users_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 配置网格权重
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # 创建右侧的操作框架
        action_frame = ttk.LabelFrame(self.tab_users, text="用户操作")
        action_frame.grid(row=0, column=1, padx=10, pady=5, sticky="n")
        
        # 用户信息输入区域
        tk.Label(action_frame, text="用户ID:").grid(row=0, column=0, padx=5, pady=5)
        self.user_id_entry = ttk.Entry(action_frame, width=20)
        self.user_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(action_frame, text="用户姓名:").grid(row=1, column=0, padx=5, pady=5)
        self.user_name_entry = ttk.Entry(action_frame, width=20)
        self.user_name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 操作按钮
        ttk.Button(action_frame, text="添加用户", 
                  command=self.add_user).grid(row=2, column=0, 
                                            columnspan=2, pady=5)
        
        ttk.Button(action_frame, text="修改用户", 
                  command=self.modify_user).grid(row=3, column=0, 
                                               columnspan=2, pady=5)
        
        ttk.Button(action_frame, text="删除用户", 
                  command=self.delete_user).grid(row=4, column=0, 
                                               columnspan=2, pady=5)
        
        # 绑定选择事件
        self.users_tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # 更新用户列表
        self.update_users_list()
        
    def sort_users(self, column, reverse=False):
        """对用户列表进行排序"""
        data = [(self.users_tree.set(item, column), item) for item in self.users_tree.get_children("")]
        data.sort(reverse=reverse)
        
        for index, (_, item) in enumerate(data):
            self.users_tree.move(item, "", index)
            
        self.users_tree.heading(column, 
                              command=lambda: self.sort_users(column, not reverse))
    
    def update_users_list(self):
        """更新用户列表显示"""
        # 清空现有列表
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
            
        # 添加用户数据
        for user_id, user in self.people_dict.items():
            self.users_tree.insert("", tk.END, values=(user_id, user.name))
    
    def on_user_select(self, event):
        """处理用户选择事件"""
        selected_items = self.users_tree.selection()
        if not selected_items:
            return
            
        # 获取选中的用户信息
        user_id = self.users_tree.item(selected_items[0])['values'][0]
        user_name = self.users_tree.item(selected_items[0])['values'][1]
        
        # 填充到输入框
        self.user_id_entry.delete(0, tk.END)
        self.user_name_entry.delete(0, tk.END)
        self.user_id_entry.insert(0, user_id)
        self.user_name_entry.insert(0, user_name)
    
    def add_user(self):
        """添加新用户"""
        user_id = self.user_id_entry.get().strip()
        user_name = self.user_name_entry.get().strip()
        
        if not user_id or not user_name:
            messagebox.showerror("错误", "请填写用户ID和姓名！")
            return
            
        if user_id in self.people_dict:
            messagebox.showerror("错误", f"用户ID {user_id} 已存在！")
            return
            
        # 添加到数据库
        if not self.db.add_user(user_id, user_name):
            messagebox.showerror("错误", "添加用户失败！")
            return
            
        # 更新内存缓存
        self.people_dict[user_id] = Person(user_id, user_name)
        
        # 清空输入框
        self.user_id_entry.delete(0, tk.END)
        self.user_name_entry.delete(0, tk.END)
        
        # 更新显示
        self.update_users_list()
        messagebox.showinfo("成功", f"用户 {user_name} 添加成功！")
    
    def modify_user(self):
        """修改用户信息"""
        selected_items = self.users_tree.selection()
        if not selected_items:
            messagebox.showerror("错误", "请先选择要修改的用户！")
            return
            
        user_id = self.user_id_entry.get().strip()
        new_name = self.user_name_entry.get().strip()
        
        if not user_id or not new_name:
            messagebox.showerror("错误", "请填写用户ID和姓名！")
            return
            
        if user_id not in self.people_dict:
            messagebox.showerror("错误", f"用户ID {user_id} 不存在！")
            return
            
        # 更新数据库
        if not self.db.update_user(user_id, new_name):
            messagebox.showerror("错误", "更新用户信息失败！")
            return
            
        # 更新内存缓存
        self.people_dict[user_id].name = new_name
        
        # 清空输入框
        self.user_id_entry.delete(0, tk.END)
        self.user_name_entry.delete(0, tk.END)
        
        # 更新显示
        self.update_users_list()
        messagebox.showinfo("成功", f"用户 {user_id} 修改成功！")
    
    def delete_user(self):
        """删除用户"""
        selected_items = self.users_tree.selection()
        if not selected_items:
            messagebox.showerror("错误", "请先选择要删除的用户！")
            return
            
        user_id = self.user_id_entry.get().strip()
        
        # 检查是否有关联的快递
        has_express = False
        for express in self.express_dict.values():
            if express.sender.id == user_id or express.receiver.id == user_id:
                has_express = True
                break
                
        if has_express:
            messagebox.showerror("错误", "该用户有关联的快递记录，无法删除！")
            return
            
        # 确认删除
        if not messagebox.askyesno("确认", f"确定要删除用户 {user_id} 吗？"):
            return
            
        # 从数据库删除用户
        if not self.db.delete_user(user_id):
            messagebox.showerror("错误", "删除用户失败！")
            return
            
        # 更新内存缓存
        del self.people_dict[user_id]
        
        # 清空输入框
        self.user_id_entry.delete(0, tk.END)
        self.user_name_entry.delete(0, tk.END)
        
        # 更新显示
        self.update_users_list()
        messagebox.showinfo("成功", f"用户 {user_id} 删除成功！")
    
    def setup_stats_tab(self):
        """设置统计页面"""
        # 创建概览面板
        overview_frame = ttk.LabelFrame(self.tab_stats, text="快递概览")
        overview_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # 创建统计标签
        self.stat_labels = {}
        
        # 在库快递
        label_frame = ttk.Frame(overview_frame)
        label_frame.pack(side=tk.LEFT, padx=20, pady=5)
        ttk.Label(label_frame, text="In storage：").pack()
        self.stat_labels['in_storage'] = ttk.Label(label_frame, text="0", 
                                                 font=("Arial", 24, "bold"))
        self.stat_labels['in_storage'].pack()
        
        # 今日入库
        label_frame = ttk.Frame(overview_frame)
        label_frame.pack(side=tk.LEFT, padx=20, pady=5)
        ttk.Label(label_frame, text="Today's inbound：").pack()
        self.stat_labels['today_in'] = ttk.Label(label_frame, text="0", 
                                               font=("Arial", 24, "bold"))
        self.stat_labels['today_in'].pack()
        
        # 今日取件
        label_frame = ttk.Frame(overview_frame)
        label_frame.pack(side=tk.LEFT, padx=20, pady=5)
        ttk.Label(label_frame, text="Today's outbound：").pack()
        self.stat_labels['today_out'] = ttk.Label(label_frame, text="0", 
                                                font=("Arial", 24, "bold"))
        self.stat_labels['today_out'].pack()
        
        # 创建图表区域
        chart_frame = ttk.LabelFrame(self.tab_stats, text="Location Distribution")
        chart_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # 创建图表
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 首次更新统计数据
        self.update_stats()
    
    def update_stats(self):
        """更新统计数据"""
        try:
            # 导入numpy
            import numpy as np

            # 获取统计数据
            stats = self.db.get_express_stats()
            
            # 更新标签
            self.stat_labels['in_storage'].config(text=str(stats['in_storage']))
            self.stat_labels['today_in'].config(text=str(stats['today_in']))
            self.stat_labels['today_out'].config(text=str(stats['today_out']))
            
            # 创建两个子图
            if stats['area_distribution']:
                # 清除现有图表
                self.figure.clf()
                
                # 创建网格布局
                gs = self.figure.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.3)
                
                # 区域容量使用情况
                ax1 = self.figure.add_subplot(gs[0])
                
                area_names = []
                capacities = []
                used_capacities = []
                
                for area_name, capacity, used in stats['area_distribution']:
                    area_names.append(area_name)
                    capacities.append(capacity)
                    used_capacities.append(used if used else 0)
                
                x = np.arange(len(area_names))
                width = 0.35
                
                ax1.bar(x - width/2, capacities, width, label='总容量', color='lightblue')
                ax1.bar(x + width/2, used_capacities, width, label='已使用', color='lightcoral')
                
                ax1.set_ylabel('快递数量')
                ax1.set_title('各区域容量使用情况')
                ax1.set_xticks(x)
                ax1.set_xticklabels(area_names, rotation=45, ha='right')
                ax1.legend()
                
                # 添加数值标签
                for i, (c, u) in enumerate(zip(capacities, used_capacities)):
                    ax1.text(i - width/2, c, str(c), ha='center', va='bottom')
                    ax1.text(i + width/2, u, str(u), ha='center', va='bottom')
                
                # 区域位置分布
                if stats['location_distribution']:
                    ax2 = self.figure.add_subplot(gs[1])
                    
                    # 按区域分组数据
                    area_data = {}
                    for loc, count, area_name in stats['location_distribution']:
                        if area_name not in area_data:
                            area_data[area_name] = {'locations': [], 'counts': []}
                        area_data[area_name]['locations'].append(loc.split(" ")[-1])  # 只显示位置号
                        area_data[area_name]['counts'].append(count)
                    
                    # 为每个区域创建柱状图
                    colors = plt.cm.Pastel1(np.linspace(0, 1, len(area_data)))
                    bottom = np.zeros(len(next(iter(area_data.values()))['locations']))
                    
                    for (area_name, data), color in zip(area_data.items(), colors):
                        ax2.bar(data['locations'], data['counts'], 
                               label=area_name, bottom=bottom, color=color)
                        bottom += np.array(data['counts'])
                    
                    ax2.set_title('各区域位置分布')
                    ax2.set_xlabel('位置编号')
                    ax2.set_ylabel('快递数量')
                    ax2.legend()
                    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
                
                # 调整布局
                self.figure.tight_layout()
            
            # 刷新画布
            self.canvas.draw()
            
        except Exception as e:
            print(f"更新统计数据时出错: {str(e)}")
        
    def sort_treeview(self, column, reverse=False):
        """对树形视图的数据进行排序"""
        # 获取所有数据
        data = [(self.express_tree.set(item, column), item) for item in self.express_tree.get_children("")]
        
        # 根据列的类型选择排序方法
        if column in ["取件码"]:  # 数字类型的列
            data.sort(key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'), reverse=reverse)
        else:  # 字符串类型的列
            data.sort(key=lambda x: x[0], reverse=reverse)
        
        # 重新排列项目
        for index, (_, item) in enumerate(data):
            self.express_tree.move(item, "", index)
        
        # 切换排序方向
        self.express_tree.heading(column, command=lambda: self.sort_treeview(column, not reverse))
        
        # 更新排序状态
        self.sort_state["column"] = column
        self.sort_state["reverse"] = reverse
    def read_qr_code(self, title="选择二维码图片"):
        """通用二维码读取函数"""
        if not QRCODE_LOAD_AVAILABLE or qrcode_load is None:
            messagebox.showerror("错误", "二维码识别功能不可用，请安装 pyzbar 所需的 DLL 文件。")
            return None
            
        filepath = tk.filedialog.askopenfilename(
            title=title,
            filetypes=[("PNG图片", "*.png"), ("所有文件", "*.*")]
        )
        if not filepath:  # 用户取消选择
            return None
            
        info = qrcode_load.read_express_qr_code(filepath)
        if info is None:
            messagebox.showerror("错误", "无法读取二维码，请确保图片清晰且包含有效的快递信息二维码。")
            return None
            
        return info
    
    def qr_read(self):
        """入库页面的二维码读取"""
        info = self.read_qr_code("选择入库快递二维码")
        if not info:
            return
            
        # 清空现有输入
        self.clear_in_fields()
        
        try:
            # 生成新的快递ID和取件码
            express_id = self.generate_express_id()
            pick_code = self.generate_pick_code()
            
            # 更新显示标签
            self.express_id_label.config(text=express_id)
            self.pick_code_label.config(text=pick_code)
            
            # 填充其他字段
            self.sender_id_entry.insert(0, info.get('sender', ''))
            self.sender_name_entry.insert(0, info.get('sender_name', ''))
            self.receiver_id_entry.insert(0, info.get('receiver', ''))
            self.receiver_name_entry.insert(0, info.get('receiver_name', ''))
            # 位置信息需要解析区域和具体位置
            location = info.get('location', '')
            if location:
                # 尝试解析位置信息（格式可能是 "区域名(区域ID) 具体位置"）
                parts = location.split(' ', 1)
                if len(parts) == 2:
                    area_str = parts[0]
                    location_str = parts[1]
                    # 设置区域下拉框
                    self.area_combobox.set(area_str)
                    self.update_location_list()  # 更新位置列表
                    # 设置具体位置
                    self.location_combobox.set(location_str)
            self.notes_entry.insert(0, info.get('notes', ''))
        except Exception as e:
            messagebox.showerror("错误", f"解析二维码数据时出错：{str(e)}")
            
    def qr_read_for_pickup(self):
        """取件页面的二维码读取"""
        info = self.read_qr_code("扫描取件二维码")
        if not info:
            return
            
        try:
            pick_code = info.get('pick_code', '')
            if pick_code:
                self.pick_code_out_entry.delete(0, tk.END)
                self.pick_code_out_entry.insert(0, pick_code)
                # 自动触发取件操作
                self.pick_up_express()
            else:
                messagebox.showerror("错误", "二维码中未包含取件码信息")
        except Exception as e:
            messagebox.showerror("错误", f"处理取件二维码时出错：{str(e)}")
            
    def qr_read_for_query(self):
        """查询页面的二维码读取"""
        info = self.read_qr_code("扫描查询二维码")
        if not info:
            return
            
        try:
            express_id = info.get('express_id', '')
            if express_id:
                self.query_entry.delete(0, tk.END)
                self.query_entry.insert(0, express_id)
                # 自动触发查询操作
                self.query_express()
            else:
                messagebox.showerror("错误", "二维码中未包含快递单号信息")
        except Exception as e:
            messagebox.showerror("错误", f"解析二维码数据时出错：{str(e)}")


def main():
    while True:
        root = ThemedTk(theme="arc")
        # root = tk.Tk()
        style = ttk.Style()
        style.theme_use('clam')  # 可选: 'default', 'clam', 'alt', 'classic'
        style.configure('TButton', font=('微软雅黑', 12), foreground='#0055aa')
        style.configure('TLabel', font=('微软雅黑', 12))
        style.configure('TEntry', font=('微软雅黑', 12))
        style.configure('TNotebook', background='#f7f7f7')
        style.configure('TFrame', background='#f7f7f7')
    
        # 创建TOTP管理器
        totp_manager = TOTPManager()
        
        # 显示角色选择对话框
        from dialogs import RoleSelectionDialog, AdminLoginDialog
        role_dialog = RoleSelectionDialog(root)
        
        # 声明全局变量
        global USER_ROLE
        
        if role_dialog.result == "admin":
            # 显示管理员登录对话框
            login_dialog = AdminLoginDialog(root, totp_manager)
            if not login_dialog.result:
                # 登录失败，返回角色选择
                root.destroy()
                continue
            
            USER_ROLE = "admin"
        elif role_dialog.result == "user":
            USER_ROLE = "user"
        elif role_dialog.result == "exit":
            # 用户选择退出程序
            root.destroy()
            break
        else:
            # 用户取消选择，返回角色选择
            root.destroy()
            continue
        
        # 创建主程序实例
        app = ExpressManagementSystem(root)
        root.mainloop()
        
        # 如果程序是通过退出登录关闭的，继续循环
        # 如果是通过退出程序关闭的，跳出循环
        if not hasattr(app, '_exit_program'):
            continue
        break

if __name__ == "__main__":
    main()