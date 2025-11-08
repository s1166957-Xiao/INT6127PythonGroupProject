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
        self.dialog.title("快递二维码")
        
        # 设置对话框大小和位置
        dialog_width = 400
        dialog_height = 500
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 创建信息展示区域
        info_frame = ttk.LabelFrame(self.dialog, text="快递信息")
        info_frame.pack(padx=10, pady=5, fill="x")
        
        # 显示快递信息
        info_text = (
            f"快递单号: {express_info['express_id']}\n"
            f"取件码: {express_info['pick_code']}\n"
            f"发件人: {express_info['sender_name']}({express_info['sender']})\n"
            f"收件人: {express_info['receiver_name']}({express_info['receiver']})\n"
            f"位置: {express_info['location']}\n"
            f"备注: {express_info['notes']}"
        )
        tk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(padx=5, pady=5)
        
        # 显示二维码图像
        try:
            # 打开并调整二维码图片大小
            img = Image.open(qr_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            
            # 创建图像标签
            qr_label = tk.Label(self.dialog, image=self.photo)
            qr_label.pack(pady=10)
            
            # 显示保存位置
            tk.Label(self.dialog, text=f"二维码已保存至:\n{qr_path}", 
                    wraplength=350).pack(pady=5)
            
        except Exception as e:
            tk.Label(self.dialog, text=f"无法加载二维码图片: {str(e)}",
                    fg="red").pack(pady=10)
        
        # 关闭按钮
        tk.Button(self.dialog, text="关闭", command=self.dialog.destroy).pack(pady=10)
        
        # 设置模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        parent.wait_window(self.dialog)

class ExpressManagementSystem:
    """快递管理系统"""
    def __init__(self, root):
        self.root = root
        self.root.title("快递管理系统")
        
        # 设置最小窗口大小
        self.root.minsize(800, 600)
        
        # 配置主窗口的网格权重，使其可以自适应调整大小
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 初始化数据库管理器
        self.db = DatabaseManager()
        
        # 数据存储（内存缓存）
        self.people_dict = {}  # {person_id: Person对象}
        self.express_dict = {}  # {express_id: Express对象}
        self.pick_code_dict = {}  # {pick_code: express_id}
        
        # 创建界面
        self.create_widgets()
        self.load_data()
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
        self.root.after(60000, self.refresh_data)
    
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
            (express_id, pick_code, sender_id, receiver_id, location, 
             notes, status, create_time, update_time, sender_name, 
             receiver_name) = express_data
            
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
        # 创建标签页
        tab_control = ttk.Notebook(self.root)
        tab_control.grid(row=0, column=0, sticky="nsew")
        
        # 入库标签页
        self.tab_in = ttk.Frame(tab_control)
        tab_control.add(self.tab_in, text="快递入库")
        self.tab_in.grid_columnconfigure(0, weight=1)
        
        # 取件标签页
        self.tab_out = ttk.Frame(tab_control)
        tab_control.add(self.tab_out, text="快递取件")
        self.tab_out.grid_columnconfigure(0, weight=1)
        
        # 查询标签页
        self.tab_query = ttk.Frame(tab_control)
        tab_control.add(self.tab_query, text="快递查询")
        self.tab_query.grid_columnconfigure(0, weight=1)
        
        # 列表标签页
        self.tab_list = ttk.Frame(tab_control)
        tab_control.add(self.tab_list, text="快递列表")
        self.tab_list.grid_columnconfigure(0, weight=1)
        self.tab_list.grid_rowconfigure(0, weight=1)
        
        # 用户管理标签页
        self.tab_users = ttk.Frame(tab_control)
        tab_control.add(self.tab_users, text="用户管理")
        self.tab_users.grid_columnconfigure(0, weight=1)
        self.tab_users.grid_rowconfigure(0, weight=1)
        
        # 数据统计标签页
        self.tab_stats = ttk.Frame(tab_control)
        tab_control.add(self.tab_stats, text="数据统计")
        self.tab_stats.grid_columnconfigure(0, weight=1)
        self.tab_stats.grid_rowconfigure(1, weight=1)
        
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
        
        # 摆放位置
        tk.Label(info_frame, text="摆放位置:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.location_entry = tk.Entry(info_frame, width=30)
        self.location_entry.grid(row=6, column=1, padx=5, pady=5)
        
        # 备注
        tk.Label(info_frame, text="备注:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.notes_entry = tk.Entry(info_frame, width=30)
        self.notes_entry.grid(row=7, column=1, padx=5, pady=5)
        
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
        location = self.location_entry.get().strip()
        notes = self.notes_entry.get().strip()
        status = "在库"
        
        # 验证必填字段
        if not all([sender_id, sender_name, receiver_id, receiver_name, location]):
            messagebox.showerror("错误", "请填写所有必填字段！")
            return
        
        # 创建或更新发件人
        if sender_id in self.people_dict:
            # 更新现有发件人姓名（如果有变化）
            if self.people_dict[sender_id].name != sender_name:
                self.people_dict[sender_id].name = sender_name
        else:
            # 创建新发件人
            self.people_dict[sender_id] = Person(sender_id, sender_name)
            self.df_user.loc[len(self.df_user)] = [sender_id, sender_name]
            self.df_user.to_excel("user.xlsx", index=False, sheet_name='人物数据')
        
        # 创建或更新收件人
        if receiver_id in self.people_dict:
            # 更新现有收件人姓名（如果有变化）
            if self.people_dict[receiver_id].name != receiver_name:
                self.people_dict[receiver_id].name = receiver_name
        else:
            # 创建新收件人
            self.people_dict[receiver_id] = Person(receiver_id, receiver_name)
            self.df_user.loc[len(self.df_user)] = [receiver_id, receiver_name]
            self.df_user.to_excel("user.xlsx", index=False, sheet_name='人物数据')
        
        # 创建快递对象
        sender = self.people_dict[sender_id]
        receiver = self.people_dict[receiver_id]
        express = Express(express_id, pick_code, sender, receiver, location, notes, status)
        
        # 添加到数据库
        if not self.db.add_express(express_id, pick_code, sender_id, receiver_id, 
                                 location, notes, status):
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
            'location': location,
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
        self.location_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)
        
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
            # 获取统计数据
            stats = self.db.get_express_stats()
            
            # 更新标签
            self.stat_labels['in_storage'].config(text=str(stats['in_storage']))
            self.stat_labels['today_in'].config(text=str(stats['today_in']))
            self.stat_labels['today_out'].config(text=str(stats['today_out']))
            
            # 清除旧图表
            self.figure.clear()
            
            # 创建新的柱状图
            if stats['location_distribution']:
                ax = self.figure.add_subplot(111)
                
                locations = [loc for loc, _ in stats['location_distribution']]
                counts = [count for _, count in stats['location_distribution']]
                
                # 创建柱状图
                bars = ax.bar(locations, counts)
                
                # 设置标题和标签
                ax.set_title("Location Distribution of In-Storage Packages")
                ax.set_xlabel("Location")
                ax.set_ylabel("Number of Packages")
                
                # 旋转x轴标签，防止重叠
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                
                # 在柱子顶部显示数值
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom')
                
                # 调整布局，确保标签不被截断
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
    root = tk.Tk()
    app = ExpressManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()