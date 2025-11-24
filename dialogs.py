import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class RoleSelectionDialog:
    """角色选择对话框，用于在程序启动时选择用户角色"""
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("请选择用户角色")
        self.result = None
        
        # 设置对话框大小和位置
        dialog_width = 500
        dialog_height = 150
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 设置对话框为模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建标签
        ttk.Label(self.dialog, text="请选择您的角色：", 
                font=("Arial", 12)).pack(pady=20)
        
        # 创建按钮框架
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        # 创建按钮
        ttk.Button(button_frame, text="普通用户", 
                  command=self.select_user).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="管理员", 
                  command=self.select_admin).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="退出程序", 
                  command=self.exit_program).pack(side=tk.LEFT, padx=10)
        
        # 禁止关闭按钮
        self.dialog.protocol("WM_DELETE_WINDOW", self.exit_program)
        
        # 等待对话框关闭
        parent.wait_window(self.dialog)
    
    def select_user(self):
        """选择普通用户角色"""
        self.result = "user"
        self.dialog.destroy()
    
    def select_admin(self):
        """选择管理员角色"""
        self.result = "admin"
        self.dialog.destroy()
        
    def exit_program(self):
        """退出程序"""
        if messagebox.askyesno("确认退出", "确定要退出程序吗？"):
            self.result = "exit"
            self.dialog.quit()  # 结束主事件循环
            self.dialog.destroy()


class AdminLoginDialog:
    """管理员登录对话框，使用TOTP进行双因素认证"""
    def __init__(self, parent, totp_manager, force_setup=False):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("管理员登录")
        self.parent = parent
        self.totp_manager = totp_manager
        self.result = False
        self.update_timer = None  # 初始化定时器变量
        self.force_setup = force_setup  # 是否强制显示设置界面
        
        # 设置对话框大小和位置
        dialog_width = 400
        dialog_height = 250
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 设置对话框为模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签
        ttk.Label(main_frame, text="请输入身份验证器中的6位验证码：", 
                 font=("Arial", 12)).pack(pady=10)
        
        # 创建验证码输入框
        self.code_entry = ttk.Entry(main_frame, width=10, justify='center', 
                                  font=("Arial", 16))
        self.code_entry.pack(pady=5)
        
        # 创建错误消息标签
        self.error_label = ttk.Label(main_frame, text="", foreground="red")
        self.error_label.pack(pady=5)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # 创建按钮
        ttk.Button(button_frame, text="登录", 
                  command=self.verify_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", 
                  command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # 调试信息标签（开发模式）
        self.debug_label = ttk.Label(main_frame, text="", foreground="blue")
        self.debug_label.pack(pady=5)
        
        # 绑定回车键到验证函数
        self.code_entry.bind('<Return>', lambda e: self.verify_code())
        
        # 设置初始焦点
        self.code_entry.focus()
        
        # 如果TOTP未配置或强制显示设置界面，显示二维码和说明
        if not self.totp_manager.is_configured() or self.force_setup:
            self.show_totp_setup()
        else:
            # 启动验证码更新定时器
            self.update_totp_debug_info()
            
        # 绑定窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 等待对话框关闭
        parent.wait_window(self.dialog)
        
    def update_totp_debug_info(self):
        """更新调试信息（验证码和倒计时）"""
        if not self.totp_manager.is_configured():
            return
            
        # 获取当前验证码
        current_code = self.totp_manager.get_current_totp()
        
        # 计算剩余时间
        import time
        remaining = 30 - int(time.time()) % 30
        
        # 更新标签文本
        self.debug_label.config(
            text=f"调试用: {current_code} (剩余 {remaining} 秒)")
        
        # 每秒更新一次
        self.update_timer = self.dialog.after(1000, self.update_totp_debug_info)
        
    def on_close(self):
        """处理窗口关闭事件"""
        # 取消定时器
        if self.update_timer:
            self.dialog.after_cancel(self.update_timer)
            self.update_timer = None
        self.result = False  # 确保取消登录
        self.dialog.destroy()
    
    def show_totp_setup(self):
        """显示TOTP设置说明和二维码"""
        # 如果强制设置模式，确保密钥已生成（重置密钥时已经生成）
        if self.force_setup and not self.totp_manager.secret_key:
            self.totp_manager.generate_new_secret()
        
        # 确保密钥存在
        if not self.totp_manager.secret_key:
            self.totp_manager.generate_new_secret()
        
        # 生成TOTP密钥和二维码
        qr_path, qr_img = self.totp_manager.generate_qr_code()
        
        # 创建并显示设置说明窗口
        setup_dialog = tk.Toplevel(self.dialog)
        title = "重置密钥配置" if self.force_setup else "首次登录配置"
        setup_dialog.title(title)
        
        # 设置窗口大小和位置
        setup_width = 500
        setup_height = 650
        x = (self.parent.winfo_screenwidth() - setup_width) // 2
        y = (self.parent.winfo_screenheight() - setup_height) // 2
        setup_dialog.geometry(f"{setup_width}x{setup_height}+{x}+{y}")
        
        # 说明文本
        if self.force_setup:
            instruction_text = """
密钥已重置！请按以下步骤重新配置：

1. 打开您的身份验证器应用（如 Authy, Google Authenticator）
2. 删除旧的密钥（如果存在）
3. 扫描下方的二维码以添加新密钥
4. 添加成功后，返回登录界面输入应用生成的6位验证码即可登录

注意：请妥善保管您的验证器应用，它是登录系统的必要工具。
            """
        else:
            instruction_text = """
首次登录，请按以下步骤操作：

1. 打开您的身份验证器应用（如 Authy, Google Authenticator）
2. 扫描下方的二维码以添加密钥
3. 添加成功后，返回登录界面输入应用生成的6位验证码即可登录

注意：请妥善保管您的验证器应用，它是登录系统的必要工具。
            """
        
        ttk.Label(setup_dialog, text=instruction_text, 
                 wraplength=450, justify='left').pack(pady=10, padx=20)
        
        # 显示密钥文本（备用方案）
        key_frame = ttk.LabelFrame(setup_dialog, text="密钥信息（备用）")
        key_frame.pack(pady=5, padx=20, fill="x")
        
        key_text = f"密钥: {self.totp_manager.secret_key}"
        key_label = ttk.Label(key_frame, text=key_text, font=("Courier", 10))
        key_label.pack(pady=5, padx=10)
        
        # 复制密钥按钮
        def copy_key():
            setup_dialog.clipboard_clear()
            setup_dialog.clipboard_append(self.totp_manager.secret_key)
            messagebox.showinfo("成功", "密钥已复制到剪贴板")
        
        ttk.Button(key_frame, text="复制密钥", command=copy_key).pack(pady=5)
        
        try:
            # 加载并显示二维码图片
            img = Image.open(qr_path)
            img = img.resize((300, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            image_label = ttk.Label(setup_dialog, image=photo)
            image_label.image = photo  # 保持引用
            image_label.pack(pady=10)
            
            # 显示二维码文件路径
            path_label = ttk.Label(setup_dialog, 
                                 text=f"二维码已保存至:\n{qr_path}", 
                                 font=("Arial", 8),
                                 foreground="gray")
            path_label.pack(pady=5)
            
        except Exception as e:
            error_msg = f"无法加载二维码图片: {str(e)}\n\n二维码文件路径: {qr_path}"
            ttk.Label(setup_dialog, text=error_msg, 
                     foreground="red", wraplength=450).pack(pady=20)
        
        # 确认按钮
        ttk.Button(setup_dialog, text="我已完成设置", 
                  command=setup_dialog.destroy).pack(pady=10)
        
        # 设置模态
        setup_dialog.transient(self.dialog)
        setup_dialog.grab_set()
        
        # 等待设置完成
        self.dialog.wait_window(setup_dialog)
    
    def verify_code(self):
        """验证输入的验证码"""
        code = self.code_entry.get().strip()
        
        if not code:
            self.error_label.config(text="请输入验证码")
            return
        
        if not code.isdigit() or len(code) != 6:
            self.error_label.config(text="验证码必须是6位数字")
            return
        
        if self.totp_manager.verify_totp(code):
            self.result = True
            self.dialog.destroy()
        else:
            self.error_label.config(text="验证码错误，请重试")
            self.code_entry.delete(0, tk.END)
    
    def cancel(self):
        """取消登录"""
        if self.update_timer:
            self.dialog.after_cancel(self.update_timer)
            self.update_timer = None
        self.result = False
        self.dialog.destroy()


# 全局样式设置（建议放在主入口，但此处演示）
def setup_styles():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', font=('微软雅黑', 12))
    style.configure('TButton', font=('微软雅黑', 12), foreground='#0055aa')
    style.configure('TEntry', font=('微软雅黑', 12))
    style.configure('TFrame', background='#f7f7f7')
    style.configure('TLabelFrame', font=('微软雅黑', 13, 'bold'))

# 在对话框类初始化时调用 setup_styles()
class ExampleDialog:
    def __init__(self, parent):
        setup_styles()
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("示例对话框")
        self.dialog.configure(bg='#f7f7f7')
        
        frame = ttk.LabelFrame(self.dialog, text="信息填写")
        frame.pack(padx=20, pady=15, fill="x")
        
        ttk.Label(frame, text="姓名:").grid(row=0, column=0, padx=8, pady=8, sticky="e")
        self.name_entry = ttk.Entry(frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=8, pady=8)
        
        ttk.Label(frame, text="手机号:").grid(row=1, column=0, padx=8, pady=8, sticky="e")
        self.phone_entry = ttk.Entry(frame, width=25)
        self.phone_entry.grid(row=1, column=1, padx=8, pady=8)
        
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def on_ok(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        messagebox.showinfo("信息", f"姓名: {name}\n手机号: {phone}")
        self.dialog.destroy()