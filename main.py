import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from datetime import datetime
import random
from PIL import Image, ImageTk
import os
import qrcode_load
import qrcode_create
from database import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from totp_manager import TOTPManager

# 配置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

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
        
        # 创建系统菜单
        system_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="系统", menu=system_menu)
        
        # 添加退出登录选项
        system_menu.add_command(label="退出登录", command=self.logout)
        system_menu.add_separator()
        system_menu.add_command(label="退出程序", command=self.exit_program)
        
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
            self.totp_manager.generate_new_secret()
            
            # 显示配置对话框
            from dialogs import AdminLoginDialog
            AdminLoginDialog(self.root, self.totp_manager)
        
        # 设置各标签页的内容
        self.setup_in_tab()
        self.setup_out_tab()
        self.setup_query_tab()
        self.setup_list_tab()
        self.setup_users_tab()
        self.setup_stats_tab()
    
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
        
        if qr_path:
            # 清空输入框
            self.clear_in_fields()
            # 显示二维码对话框
            QRCodeDialog(self.root, qr_path, express_info)
        else:
            messagebox.showwarning("警告", f"快递入库成功，但二维码生成失败！\n快递单号：{express_id}")
        
        # 更新区域和位置列表
        self.update_area_list()
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
            self.location_entry.insert(0, info.get('location', ''))
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
        root = tk.Tk()
        
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
