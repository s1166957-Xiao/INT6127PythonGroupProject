import tkinter as tk
from tkinter import ttk, messagebox
import re
import pandas as pd

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

class ExpressManagementSystem:
    """快递管理系统"""
    def __init__(self, root):
        self.root = root
        self.root.title("快递管理系统")
        self.root.geometry("800x600")
        
        # 数据存储
        self.people_dict = {}  # {person_id: Person对象}
        self.express_dict = {}  # {express_id: Express对象}
        self.pick_code_dict = {}  # {pick_code: express_id}
        
        # 创建界面
        self.create_widgets()
        self.load_user()
        self.load_exprss()
        self.update_express_list()
        # 初始化一些测试数据
        # self.init_test_data()
    
    def init_test_data(self):
        """初始化测试数据"""
        # 创建测试人物
        person1 = Person("P001", "张三")
        person2 = Person("P002", "李四")
        person3 = Person("P003", "王五")
        
        self.people_dict = {
            "P001": person1,
            "P002": person2,
            "P003": person3
        }
        
        # 创建测试快递
        express1 = Express("E001", "123456", person1, person2, "A区1架", "易碎品")
        express2 = Express("E002", "654321", person2, person3, "B区2架", "")
        
        self.express_dict = {
            "E001": express1,
            "E002": express2
        }
        
        self.pick_code_dict = {
            "123456": "E001",
            "654321": "E002"
        }
        
        # 更新显示
        self.update_express_list()
    
    def load_user(self):
        self.df_user = pd.read_excel('user.xlsx', header = 0, engine='openpyxl')
        for k,v in self.df_user.iterrows():
            self.people_dict[v[0]] = Person(v[0], v[1])
    
    def load_exprss(self):
        self.df_express = pd.read_excel('express.xlsx', header = 0, engine='openpyxl')
        for k,v in self.df_express.iterrows():
            self.express_dict[v[0]] = Express(v[0], v[1], self.people_dict[v[2]], self.people_dict[v[3]], v[4], v[5], v[6])
            self.pick_code_dict[v[1]] = v[0]
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建标签页
        tab_control = ttk.Notebook(self.root)
        
        # 入库标签页
        self.tab_in = ttk.Frame(tab_control)
        tab_control.add(self.tab_in, text="快递入库")
        
        # 取件标签页
        self.tab_out = ttk.Frame(tab_control)
        tab_control.add(self.tab_out, text="快递取件")
        
        # 查询标签页
        self.tab_query = ttk.Frame(tab_control)
        tab_control.add(self.tab_query, text="快递查询")
        
        # 列表标签页
        self.tab_list = ttk.Frame(tab_control)
        tab_control.add(self.tab_list, text="快递列表")
        
        tab_control.pack(expand=1, fill="both")
        
        # 设置各标签页的内容
        self.setup_in_tab()
        self.setup_out_tab()
        self.setup_query_tab()
        self.setup_list_tab()
    
    def setup_in_tab(self):
        """设置入库标签页"""
        # 快递ID
        tk.Label(self.tab_in, text="快递ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.express_id_entry = tk.Entry(self.tab_in, width=30)
        self.express_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # 取件码
        tk.Label(self.tab_in, text="取件码:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pick_code_entry = tk.Entry(self.tab_in, width=30)
        self.pick_code_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 发件人ID
        tk.Label(self.tab_in, text="发件人ID:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.sender_id_entry = tk.Entry(self.tab_in, width=30)
        self.sender_id_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # 发件人姓名
        tk.Label(self.tab_in, text="发件人姓名:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.sender_name_entry = tk.Entry(self.tab_in, width=30)
        self.sender_name_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # 收件人ID
        tk.Label(self.tab_in, text="收件人ID:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.receiver_id_entry = tk.Entry(self.tab_in, width=30)
        self.receiver_id_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # 收件人姓名
        tk.Label(self.tab_in, text="收件人姓名:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.receiver_name_entry = tk.Entry(self.tab_in, width=30)
        self.receiver_name_entry.grid(row=5, column=1, padx=5, pady=5)
        
        # 摆放位置
        tk.Label(self.tab_in, text="摆放位置:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.location_entry = tk.Entry(self.tab_in, width=30)
        self.location_entry.grid(row=6, column=1, padx=5, pady=5)
        
        # 备注
        tk.Label(self.tab_in, text="备注:").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.notes_entry = tk.Entry(self.tab_in, width=30)
        self.notes_entry.grid(row=7, column=1, padx=5, pady=5)
        
        # 按钮
        tk.Button(self.tab_in, text="入库", command=self.add_express, 
                 bg="lightgreen", width=15).grid(row=8, column=0, columnspan=2, pady=10)
        
        # 清空按钮
        tk.Button(self.tab_in, text="清空", command=self.clear_in_fields, 
                 bg="lightyellow", width=15).grid(row=9, column=0, columnspan=2, pady=5)
    
    def setup_out_tab(self):
        """设置取件标签页"""
        tk.Label(self.tab_out, text="请输入取件码:").pack(pady=10)
        
        self.pick_code_out_entry = tk.Entry(self.tab_out, width=30, font=("Arial", 14))
        self.pick_code_out_entry.pack(pady=10)
        
        tk.Button(self.tab_out, text="取件", command=self.pick_up_express, 
                 bg="lightcoral", width=15, height=2).pack(pady=20)
        
        # 结果显示
        self.result_label = tk.Label(self.tab_out, text="", font=("Arial", 12), fg="blue")
        self.result_label.pack(pady=10)
    
    def setup_query_tab(self):
        """设置查询标签页"""
        tk.Label(self.tab_query, text="请输入查询条件(快递ID/发件人ID/收件人ID):").pack(pady=10)
        
        self.query_entry = tk.Entry(self.tab_query, width=30, font=("Arial", 12))
        self.query_entry.pack(pady=10)
        
        tk.Button(self.tab_query, text="查询", command=self.query_express, 
                 bg="lightblue", width=15).pack(pady=10)
        
        # 查询结果文本框
        self.query_result_text = tk.Text(self.tab_query, width=80, height=20)
        self.query_result_text.pack(pady=10, padx=10, fill="both", expand=True)
        
        # 添加滚动条
        scrollbar = tk.Scrollbar(self.query_result_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.query_result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.query_result_text.yview)
    
    def setup_list_tab(self):
        """设置快递列表标签页"""
        # 创建树形视图显示快递列表
        columns = ("快递ID", "取件码", "发件人", "收件人", "位置", "备注", "状态")
        self.express_tree = ttk.Treeview(self.tab_list, columns=columns, show="headings", height=20)
        
        # 设置列标题
        for col in columns:
            self.express_tree.heading(col, text=col)
            self.express_tree.column(col, width=100)
        
        self.express_tree.pack(pady=10, padx=10, fill="both", expand=True)
        
        # 刷新按钮
        tk.Button(self.tab_list, text="刷新列表", command=self.update_express_list).pack(pady=5)
    
    def add_express(self):
        """添加快递入库"""
        # 获取输入数据
        express_id = self.express_id_entry.get().strip()
        pick_code = self.pick_code_entry.get().strip()
        sender_id = self.sender_id_entry.get().strip()
        sender_name = self.sender_name_entry.get().strip()
        receiver_id = self.receiver_id_entry.get().strip()
        receiver_name = self.receiver_name_entry.get().strip()
        location = self.location_entry.get().strip()
        notes = self.notes_entry.get().strip()
        status = "在库"
        
        # 验证输入
        if not all([express_id, pick_code, sender_id, sender_name, receiver_id, receiver_name, location]):
            messagebox.showerror("错误", "请填写所有必填字段！")
            return
        
        # 检查快递ID是否已存在
        if express_id in self.express_dict:
            messagebox.showerror("错误", f"快递ID {express_id} 已存在！")
            return
        
        # 检查取件码是否已存在
        if pick_code in self.pick_code_dict:
            messagebox.showerror("错误", f"取件码 {pick_code} 已存在！")
            return
        
        # 验证取件码格式（6位数字）
        if not re.match(r'^\d{6}$', pick_code):
            messagebox.showerror("错误", "取件码必须是6位数字！")
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
        
        # 添加到数据存储
        self.express_dict[express_id] = express
        self.pick_code_dict[pick_code] = express_id
        # 更新显示
        self.df_express.loc[len(self.df_express)] = [express_id, pick_code, sender_id, receiver_id, location, notes, status]
        self.df_express.to_excel("express.xlsx", index=False, sheet_name='快递数据')

        self.update_express_list()
        
        # 清空输入框
        self.clear_in_fields()
        messagebox.showinfo("成功", f"快递 {express_id} 入库成功！")
    
    def pick_up_express(self):
        """快递取件"""
        pick_code = self.pick_code_out_entry.get().strip()
        
        if not pick_code:
            messagebox.showerror("错误", "请输入取件码！")
            return
        pick_code = int(pick_code)
        # 查找快递
        if self.pick_code_dict.get(pick_code) is not None:
            express_id = self.pick_code_dict[pick_code]
            express = self.express_dict[express_id]
            
            if express.status == "已取件":
                self.result_label.config(text="该快递已被取走！", fg="red")
            else:
                # 更新状态
                express.status = "已取件"
                self.df_express.loc[self.df_express["express_id"] == express_id, "status"] = '已取件'
                self.df_express.to_excel("express.xlsx", index=False, sheet_name='快递数据')
                # 显示成功信息
                result_text = f"取件成功，请与【{express.location}】取走您的快递！"
                self.result_label.config(text=result_text, fg="green")
                
                # 清空输入框
                self.pick_code_out_entry.delete(0, tk.END)
                
                # 更新显示
                self.update_express_list()
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
        self.express_id_entry.delete(0, tk.END)
        self.pick_code_entry.delete(0, tk.END)
        self.sender_id_entry.delete(0, tk.END)
        self.sender_name_entry.delete(0, tk.END)
        self.receiver_id_entry.delete(0, tk.END)
        self.receiver_name_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = ExpressManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()