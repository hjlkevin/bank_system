#!/usr/bin/env python3
"""
简易银行系统图形用户界面

此脚本提供了一个基于tkinter的图形界面来与银行系统交互。
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from decimal import Decimal, InvalidOperation

from banking_system import BankingSystem


class BankingApp(tk.Tk):
    """银行系统的主应用窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.title("简易银行系统")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # 设置应用图标（如果有）
        # self.iconbitmap("bank_icon.ico")
        
        # 初始化银行系统
        self.banking = BankingSystem()
        
        # 初始化界面
        self._init_ui()
        
        # 添加示例账户（可选）
        if len(sys.argv) > 1 and sys.argv[1] == "--sample":
            self._create_sample_accounts()
    
    def _init_ui(self):
        """初始化用户界面组件"""
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建标题标签
        title_label = ttk.Label(
            self.main_frame, 
            text="欢迎使用简易银行系统", 
            font=("黑体", 24)
        )
        title_label.pack(pady=20)
        
        # 创建按钮框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        # 创建操作按钮
        buttons = [
            ("创建新账户", self.create_account_window),
            ("查看账户详情", self.view_account_window),
            ("列出所有账户", self.list_accounts_window),
            ("存款", self.deposit_window),
            ("取款", self.withdraw_window),
            ("转账", self.transfer_window),
            ("保存账户到文件", self.save_accounts_window),
            ("从文件加载账户", self.load_accounts_window),
            ("退出", self.exit_app)
        ]
        
        for text, command in buttons:
            button = ttk.Button(
                button_frame,
                text=text,
                command=command,
                width=20
            )
            button.pack(pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        status_bar = ttk.Label(
            self, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_sample_accounts(self):
        """创建示例账户"""
        self.banking.create_account("1", "张三", Decimal("1000.00"))
        self.banking.create_account("2", "李四", Decimal("500.00"))
        self.status_var.set("已创建示例账户")
    
    def create_account_window(self):
        """打开创建账户窗口"""
        window = tk.Toplevel(self)
        window.title("创建新账户")
        window.geometry("400x300")
        window.transient(self)  # 设置为主窗口的子窗口
        window.grab_set()  # 模态窗口
        
        # 创建表单
        ttk.Label(window, text="创建新账户", font=("黑体", 16)).pack(pady=10)
        
        form_frame = ttk.Frame(window)
        form_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # 账户ID
        ttk.Label(form_frame, text="账户ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        id_entry = ttk.Entry(form_frame, width=30)
        id_entry.grid(row=0, column=1, pady=5)
        
        # 所有者姓名
        ttk.Label(form_frame, text="所有者姓名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=1, column=1, pady=5)
        
        # 初始余额
        ttk.Label(form_frame, text="初始余额:").grid(row=2, column=0, sticky=tk.W, pady=5)
        balance_entry = ttk.Entry(form_frame, width=30)
        balance_entry.insert(0, "0.00")
        balance_entry.grid(row=2, column=1, pady=5)
        
        # 提交按钮
        def on_submit():
            account_id = id_entry.get().strip()
            owner_name = name_entry.get().strip()
            
            try:
                initial_balance = Decimal(balance_entry.get().strip())
                
                success, error = self.banking.create_account(
                    account_id, owner_name, initial_balance
                )
                
                if success:
                    messagebox.showinfo(
                        "成功", 
                        f"账户创建成功！\n账户ID: {account_id}"
                    )
                    window.destroy()
                    self.status_var.set(f"已创建账户: {account_id}")
                else:
                    messagebox.showerror("错误", f"账户创建失败: {error}")
            
            except InvalidOperation:
                messagebox.showerror("错误", "请输入有效的余额数字")
        
        button_frame = ttk.Frame(window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="创建账户", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=window.destroy).pack(side=tk.LEFT, padx=5)
    
    def view_account_window(self):
        """打开查看账户窗口"""
        account_id = simpledialog.askstring("查看账户", "请输入账户ID:")
        
        if not account_id:
            return
        
        account = self.banking.get_account(account_id)
        
        if not account:
            messagebox.showerror("错误", f"未找到ID为 '{account_id}' 的账户")
            return
        
        # 显示账户信息窗口
        window = tk.Toplevel(self)
        window.title(f"账户详情 - {account_id}")
        window.geometry("400x300")
        window.transient(self)
        
        ttk.Label(window, text="账户详情", font=("黑体", 16)).pack(pady=10)
        
        info_frame = ttk.Frame(window)
        info_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # 账户信息
        ttk.Label(info_frame, text="账户ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=account.account_id).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="所有者:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=account.owner_name).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="余额:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=f"¥{account.balance}").grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(window, text="关闭", command=window.destroy).pack(pady=10)
        
        self.status_var.set(f"正在查看账户: {account_id}")
    
    def list_accounts_window(self):
        """打开账户列表窗口"""
        accounts = self.banking.get_all_accounts()
        
        window = tk.Toplevel(self)
        window.title("所有账户")
        window.geometry("600x400")
        window.transient(self)
        
        ttk.Label(window, text="所有账户", font=("黑体", 16)).pack(pady=10)
        
        if not accounts:
            ttk.Label(window, text="系统中没有找到账户").pack(pady=20)
        else:
            # 创建表格
            columns = ("账户ID", "所有者", "余额")
            tree = ttk.Treeview(window, columns=columns, show="headings")
            
            # 设置列标题
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            
            # 添加数据
            for account in accounts:
                tree.insert("", tk.END, values=(
                    account.account_id,
                    account.owner_name,
                    f"¥{account.balance}"
                ))
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(window, text="关闭", command=window.destroy).pack(pady=10)
        
        self.status_var.set(f"列出账户: {len(accounts)}个")
    
    def deposit_window(self):
        """打开存款窗口"""
        window = tk.Toplevel(self)
        window.title("存款")
        window.geometry("400x250")
        window.transient(self)
        window.grab_set()
        
        ttk.Label(window, text="存款", font=("黑体", 16)).pack(pady=10)
        
        form_frame = ttk.Frame(window)
        form_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # 账户ID
        ttk.Label(form_frame, text="账户ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        id_entry = ttk.Entry(form_frame, width=30)
        id_entry.grid(row=0, column=1, pady=5)
        
        # 存款金额
        ttk.Label(form_frame, text="存款金额:").grid(row=1, column=0, sticky=tk.W, pady=5)
        amount_entry = ttk.Entry(form_frame, width=30)
        amount_entry.grid(row=1, column=1, pady=5)
        
        # 提交按钮
        def on_submit():
            account_id = id_entry.get().strip()
            
            if not account_id:
                messagebox.showerror("错误", "请输入账户ID")
                return
            
            if not self.banking.get_account(account_id):
                messagebox.showerror("错误", f"未找到ID为 '{account_id}' 的账户")
                return
            
            try:
                amount = Decimal(amount_entry.get().strip())
                
                success, error = self.banking.deposit(account_id, amount)
                
                if success:
                    account = self.banking.get_account(account_id)
                    messagebox.showinfo(
                        "成功", 
                        f"存款成功！\n新余额: ¥{account.balance}"
                    )
                    window.destroy()
                    self.status_var.set(f"已向账户 {account_id} 存款 ¥{amount}")
                else:
                    messagebox.showerror("错误", f"存款失败: {error}")
            
            except InvalidOperation:
                messagebox.showerror("错误", "请输入有效的金额数字")
        
        button_frame = ttk.Frame(window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="存款", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=window.destroy).pack(side=tk.LEFT, padx=5)
    
    def withdraw_window(self):
        """打开取款窗口"""
        window = tk.Toplevel(self)
        window.title("取款")
        window.geometry("400x250")
        window.transient(self)
        window.grab_set()
        
        ttk.Label(window, text="取款", font=("黑体", 16)).pack(pady=10)
        
        form_frame = ttk.Frame(window)
        form_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # 账户ID
        ttk.Label(form_frame, text="账户ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        id_entry = ttk.Entry(form_frame, width=30)
        id_entry.grid(row=0, column=1, pady=5)
        
        # 取款金额
        ttk.Label(form_frame, text="取款金额:").grid(row=1, column=0, sticky=tk.W, pady=5)
        amount_entry = ttk.Entry(form_frame, width=30)
        amount_entry.grid(row=1, column=1, pady=5)
        
        # 提交按钮
        def on_submit():
            account_id = id_entry.get().strip()
            
            if not account_id:
                messagebox.showerror("错误", "请输入账户ID")
                return
            
            if not self.banking.get_account(account_id):
                messagebox.showerror("错误", f"未找到ID为 '{account_id}' 的账户")
                return
            
            try:
                amount = Decimal(amount_entry.get().strip())
                
                success, error = self.banking.withdraw(account_id, amount)
                
                if success:
                    account = self.banking.get_account(account_id)
                    messagebox.showinfo(
                        "成功", 
                        f"取款成功！\n新余额: ¥{account.balance}"
                    )
                    window.destroy()
                    self.status_var.set(f"已从账户 {account_id} 取款 ¥{amount}")
                else:
                    messagebox.showerror("错误", f"取款失败: {error}")
            
            except InvalidOperation:
                messagebox.showerror("错误", "请输入有效的金额数字")
        
        button_frame = ttk.Frame(window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="取款", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=window.destroy).pack(side=tk.LEFT, padx=5)
    
    def transfer_window(self):
        """打开转账窗口"""
        window = tk.Toplevel(self)
        window.title("转账")
        window.geometry("400x300")
        window.transient(self)
        window.grab_set()
        
        ttk.Label(window, text="转账", font=("黑体", 16)).pack(pady=10)
        
        form_frame = ttk.Frame(window)
        form_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # 来源账户ID
        ttk.Label(form_frame, text="来源账户ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        from_id_entry = ttk.Entry(form_frame, width=30)
        from_id_entry.grid(row=0, column=1, pady=5)
        
        # 目标账户ID
        ttk.Label(form_frame, text="目标账户ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        to_id_entry = ttk.Entry(form_frame, width=30)
        to_id_entry.grid(row=1, column=1, pady=5)
        
        # 转账金额
        ttk.Label(form_frame, text="转账金额:").grid(row=2, column=0, sticky=tk.W, pady=5)
        amount_entry = ttk.Entry(form_frame, width=30)
        amount_entry.grid(row=2, column=1, pady=5)
        
        # 提交按钮
        def on_submit():
            from_account_id = from_id_entry.get().strip()
            to_account_id = to_id_entry.get().strip()
            
            if not from_account_id or not to_account_id:
                messagebox.showerror("错误", "请输入来源和目标账户ID")
                return
            
            if not self.banking.get_account(from_account_id):
                messagebox.showerror("错误", f"未找到ID为 '{from_account_id}' 的来源账户")
                return
            
            if not self.banking.get_account(to_account_id):
                messagebox.showerror("错误", f"未找到ID为 '{to_account_id}' 的目标账户")
                return
            
            try:
                amount = Decimal(amount_entry.get().strip())
                
                success, error = self.banking.transfer(from_account_id, to_account_id, amount)
                
                if success:
                    from_account = self.banking.get_account(from_account_id)
                    to_account = self.banking.get_account(to_account_id)
                    messagebox.showinfo(
                        "成功", 
                        f"转账成功！\n来源账户 ({from_account_id}) 新余额: ¥{from_account.balance}\n"
                        f"目标账户 ({to_account_id}) 新余额: ¥{to_account.balance}"
                    )
                    window.destroy()
                    self.status_var.set(f"已从账户 {from_account_id} 转账 ¥{amount} 到账户 {to_account_id}")
                else:
                    messagebox.showerror("错误", f"转账失败: {error}")
            
            except InvalidOperation:
                messagebox.showerror("错误", "请输入有效的金额数字")
        
        button_frame = ttk.Frame(window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="转账", command=on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=window.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_accounts_window(self):
        """保存账户到文件"""
        if not self.banking.get_all_accounts():
            messagebox.showwarning("警告", "当前没有账户可以保存")
            return
        
        filename = simpledialog.askstring(
            "保存账户", 
            "请输入要保存的文件名:", 
            initialvalue="accounts.csv"
        )
        
        if not filename:
            return
        
        success, error = self.banking.save_to_csv(filename)
        
        if success:
            messagebox.showinfo("成功", f"账户已成功保存到 '{filename}'")
            self.status_var.set(f"已保存账户到 {filename}")
        else:
            messagebox.showerror("错误", f"保存账户失败: {error}")
    
    def load_accounts_window(self):
        """从文件加载账户"""
        filename = simpledialog.askstring(
            "加载账户", 
            "请输入要加载的文件名:", 
            initialvalue="accounts.csv"
        )
        
        if not filename:
            return
        
        if not os.path.exists(filename):
            messagebox.showerror("错误", f"未找到文件 '{filename}'")
            return
        
        success, error = self.banking.load_from_csv(filename)
        
        if success:
            messagebox.showinfo("成功", f"账户已成功从 '{filename}' 加载")
            self.status_var.set(f"已从 {filename} 加载账户")
        else:
            messagebox.showerror("错误", f"加载账户失败: {error}")
    
    def exit_app(self):
        """退出应用程序"""
        if messagebox.askyesno("退出", "确定要退出应用程序吗？"):
            self.destroy()
            sys.exit(0)


def main():
    """主程序入口点"""
    app = BankingApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main()) 