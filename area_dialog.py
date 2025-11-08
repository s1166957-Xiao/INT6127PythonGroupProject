import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class AreaDialog:
    """仓库区域管理对话框"""
    def __init__(self, parent, db):
        self.dialog = tk.Toplevel(parent)
        self.parent = parent
        self.db = db
        
        self.dialog.title("仓库区域管理")
        self.setup_ui()
        self.load_areas()
        
        # 设置模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        parent.wait_window(self.dialog)
    
    def setup_ui(self):
        """设置用户界面"""
        # 区域列表
        list_frame = ttk.LabelFrame(self.dialog, text="区域列表")
        list_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # 创建树形视图
        columns = ("区域ID", "区域名称", "容量", "当前数量", "使用位置", "描述")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ("区域ID", "区域名称", "容量", "当前数量"):
                self.tree.column(col, width=100)
            elif col == "使用位置":
                self.tree.column(col, width=200)
            else:
                self.tree.column(col, width=150)
        
        # 添加滚动条
        yscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 编辑区域
        edit_frame = ttk.LabelFrame(self.dialog, text="添加/编辑区域")
        edit_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # 输入字段
        ttk.Label(edit_frame, text="区域ID:").grid(row=0, column=0, padx=5, pady=2)
        self.area_id_var = tk.StringVar()
        self.area_id_entry = ttk.Entry(edit_frame, textvariable=self.area_id_var)
        self.area_id_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(edit_frame, text="区域名称:").grid(row=0, column=2, padx=5, pady=2)
        self.area_name_var = tk.StringVar()
        self.area_name_entry = ttk.Entry(edit_frame, textvariable=self.area_name_var)
        self.area_name_entry.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(edit_frame, text="容量:").grid(row=0, column=4, padx=5, pady=2)
        self.capacity_var = tk.StringVar()
        self.capacity_entry = ttk.Entry(edit_frame, textvariable=self.capacity_var)
        self.capacity_entry.grid(row=0, column=5, padx=5, pady=2)
        
        ttk.Label(edit_frame, text="描述:").grid(row=1, column=0, padx=5, pady=2)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(edit_frame, textvariable=self.description_var)
        self.description_entry.grid(row=1, column=1, columnspan=5, sticky="ew", 
                                  padx=5, pady=2)
        
        # 按钮区域
        btn_frame = ttk.Frame(edit_frame)
        btn_frame.grid(row=2, column=0, columnspan=6, pady=5)
        
        ttk.Button(btn_frame, text="添加", command=self.add_area).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="更新", command=self.update_area).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除", command=self.delete_area).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="清空", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # 配置网格布局
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def load_areas(self):
        """加载区域数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加数据
        for area in self.db.get_all_areas():
            self.tree.insert("", tk.END, values=(
                area[0],  # area_id
                area[1],  # area_name
                area[2],  # capacity
                area[3],  # current_items
                area[4] or "",  # locations
                area[3]  # description
            ))
    
    def validate_input(self):
        """验证输入数据"""
        area_id = self.area_id_var.get().strip()
        area_name = self.area_name_var.get().strip()
        capacity = self.capacity_var.get().strip()
        
        if not all([area_id, area_name, capacity]):
            messagebox.showerror("错误", "区域ID、名称和容量不能为空")
            return False
        
        try:
            capacity = int(capacity)
            if capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "容量必须是正整数")
            return False
        
        return True
    
    def add_area(self):
        """添加区域"""
        if not self.validate_input():
            return
        
        area_id = self.area_id_var.get().strip()
        area_name = self.area_name_var.get().strip()
        capacity = int(self.capacity_var.get().strip())
        description = self.description_var.get().strip()
        
        if self.db.add_area(area_id, area_name, capacity, description):
            messagebox.showinfo("成功", "区域添加成功")
            self.load_areas()
            self.clear_fields()
        else:
            messagebox.showerror("错误", "区域添加失败")
    
    def update_area(self):
        """更新区域"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要更新的区域")
            return
        
        if not self.validate_input():
            return
        
        area_id = self.area_id_var.get().strip()
        area_name = self.area_name_var.get().strip()
        capacity = int(self.capacity_var.get().strip())
        description = self.description_var.get().strip()
        
        if self.db.update_area(area_id, area_name, capacity, description):
            messagebox.showinfo("成功", "区域更新成功")
            self.load_areas()
            self.clear_fields()
        else:
            messagebox.showerror("错误", "区域更新失败")
    
    def delete_area(self):
        """删除区域"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的区域")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的区域吗？"):
            area_id = self.tree.item(selection[0])['values'][0]
            success, message = self.db.delete_area(area_id)
            if success:
                messagebox.showinfo("成功", message)
                self.load_areas()
                self.clear_fields()
            else:
                messagebox.showerror("错误", message)
    
    def clear_fields(self):
        """清空输入字段"""
        self.area_id_var.set("")
        self.area_name_var.set("")
        self.capacity_var.set("")
        self.description_var.set("")
        # 清除树形视图的选择
        self.tree.selection_remove(self.tree.selection())
    
    def on_select(self, event):
        """处理选择事件"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.area_id_var.set(values[0])
            self.area_name_var.set(values[1])
            self.capacity_var.set(values[2])
            self.description_var.set(values[5])
