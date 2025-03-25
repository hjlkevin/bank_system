#!/usr/bin/env python3
"""
简易银行系统命令行界面

此脚本提供了一个命令行界面来与银行系统交互。
"""

import os
import sys
from decimal import Decimal, InvalidOperation

from banking_system import BankingSystem


def display_menu():
    """显示主菜单选项。"""
    print("\n===== 简易银行系统 =====")
    print("1. 创建新账户")
    print("2. 查看账户详情")
    print("3. 列出所有账户")
    print("4. 存款")
    print("5. 取款")
    print("6. 转账")
    print("7. 保存账户到文件")
    print("8. 从文件加载账户")
    print("9. 退出程序")
    print("0. 切换到图形界面")
    print("========================")


def get_decimal_input(prompt: str) -> Decimal:
    """
    获取并验证用户输入的小数值。
    
    参数:
        prompt: 向用户显示的提示信息
        
    返回:
        一个有效的Decimal值
    """
    while True:
        try:
            value = input(prompt)
            return Decimal(value)
        except InvalidOperation:
            print("错误: 请输入有效的数字。")


def create_account(banking: BankingSystem):
    """处理账户创建。"""
    print("\n----- 创建新账户 -----")
    
    account_id = input("输入账户ID: ")
    owner_name = input("输入账户所有者姓名: ")
    
    try:
        initial_balance = get_decimal_input("输入初始余额 (0表示空账户): ")
        
        success, error = banking.create_account(account_id, owner_name, initial_balance)
        
        if success:
            print(f"账户创建成功！账户ID: {account_id}")
        else:
            print(f"账户创建失败: {error}")
    
    except KeyboardInterrupt:
        print("\n账户创建已取消。")


def view_account(banking: BankingSystem):
    """显示特定账户的详细信息。"""
    print("\n----- 查看账户详情 -----")
    
    account_id = input("输入账户ID: ")
    account = banking.get_account(account_id)
    
    if account:
        print(f"\n账户ID: {account.account_id}")
        print(f"所有者: {account.owner_name}")
        print(f"余额: ¥{account.balance}")
    else:
        print(f"未找到ID为 '{account_id}' 的账户。")


def list_accounts(banking: BankingSystem):
    """列出系统中的所有账户。"""
    accounts = banking.get_all_accounts()
    
    if not accounts:
        print("\n系统中没有找到账户。")
        return
    
    print(f"\n----- 所有账户 ({len(accounts)}) -----")
    print(f"{'ID':<10} {'所有者':<20} {'余额':<10}")
    print("-" * 40)
    
    for account in accounts:
        print(f"{account.account_id:<10} {account.owner_name:<20} ¥{account.balance:<10}")


def deposit(banking: BankingSystem):
    """处理向账户存款。"""
    print("\n----- 存款 -----")
    
    account_id = input("输入账户ID: ")
    
    if not banking.get_account(account_id):
        print(f"未找到ID为 '{account_id}' 的账户。")
        return
    
    try:
        amount = get_decimal_input("输入存款金额: ¥")
        
        success, error = banking.deposit(account_id, amount)
        
        if success:
            account = banking.get_account(account_id)
            print(f"存款成功！新余额: ¥{account.balance}")
        else:
            print(f"存款失败: {error}")
    
    except KeyboardInterrupt:
        print("\n存款已取消。")


def withdraw(banking: BankingSystem):
    """处理从账户取款。"""
    print("\n----- 取款 -----")
    
    account_id = input("输入账户ID: ")
    
    if not banking.get_account(account_id):
        print(f"未找到ID为 '{account_id}' 的账户。")
        return
    
    try:
        amount = get_decimal_input("输入取款金额: ¥")
        
        success, error = banking.withdraw(account_id, amount)
        
        if success:
            account = banking.get_account(account_id)
            print(f"取款成功！新余额: ¥{account.balance}")
        else:
            print(f"取款失败: {error}")
    
    except KeyboardInterrupt:
        print("\n取款已取消。")


def transfer(banking: BankingSystem):
    """处理账户之间的转账。"""
    print("\n----- 转账 -----")
    
    from_account_id = input("输入来源账户ID: ")
    
    if not banking.get_account(from_account_id):
        print(f"未找到ID为 '{from_account_id}' 的来源账户。")
        return
    
    to_account_id = input("输入目标账户ID: ")
    
    if not banking.get_account(to_account_id):
        print(f"未找到ID为 '{to_account_id}' 的目标账户。")
        return
    
    try:
        amount = get_decimal_input("输入转账金额: ¥")
        
        success, error = banking.transfer(from_account_id, to_account_id, amount)
        
        if success:
            from_account = banking.get_account(from_account_id)
            to_account = banking.get_account(to_account_id)
            print(f"转账成功！")
            print(f"来源账户 ({from_account_id}) 新余额: ¥{from_account.balance}")
            print(f"目标账户 ({to_account_id}) 新余额: ¥{to_account.balance}")
        else:
            print(f"转账失败: {error}")
    
    except KeyboardInterrupt:
        print("\n转账已取消。")


def save_to_file(banking: BankingSystem):
    """将账户数据保存到CSV文件。"""
    print("\n----- 保存账户到文件 -----")
    
    if not banking.get_all_accounts():
        print("当前没有账户可以保存。")
        return
    
    filename = input("输入要保存的文件名 (默认: accounts.csv): ").strip() or "accounts.csv"
    
    success, error = banking.save_to_csv(filename)
    
    if success:
        print(f"账户已成功保存到 '{filename}'")
    else:
        print(f"保存账户失败: {error}")


def load_from_file(banking: BankingSystem):
    """从CSV文件加载账户数据。"""
    print("\n----- 从文件加载账户 -----")
    
    filename = input("输入要加载的文件名 (默认: accounts.csv): ").strip() or "accounts.csv"
    
    if not os.path.exists(filename):
        print(f"未找到文件 '{filename}'。")
        return
    
    success, error = banking.load_from_csv(filename)
    
    if success:
        print(f"账户已成功从 '{filename}' 加载")
    else:
        print(f"加载账户失败: {error}")


def exit_app():
    """处理退出应用程序。"""
    print("\n----- 退出程序 -----")
    confirmation = input("您确定要退出吗？任何未保存的数据将会丢失。(是/否): ").strip().lower()
    
    if confirmation in ['是', 'y', 'yes']:
        print("\n感谢使用简易银行系统。再见！")
        return True
    else:
        print("已取消退出。")
        return False


def switch_to_gui():
    """切换到图形用户界面。"""
    print("\n----- 切换到图形界面 -----")
    
    try:
        import tkinter
        import bank_ui
        
        print("正在启动图形界面...")
        # 启动图形界面前保存当前状态（可选）
        
        return True
    except ImportError as e:
        print(f"无法切换到图形界面: {str(e)}")
        print("请确保您安装了tkinter库。")
        return False


def main():
    """主程序函数。"""
    banking = BankingSystem()
    
    # 如果需要，创建示例账户
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        print("创建示例账户...")
        banking.create_account("1", "张三", Decimal("1000.00"))
        banking.create_account("2", "李四", Decimal("500.00"))
        print("示例账户已创建。")
    
    while True:
        display_menu()
        
        try:
            choice = input("\n请输入您的选择 (0-9): ")
            
            if choice == "1":
                create_account(banking)
            elif choice == "2":
                view_account(banking)
            elif choice == "3":
                list_accounts(banking)
            elif choice == "4":
                deposit(banking)
            elif choice == "5":
                withdraw(banking)
            elif choice == "6":
                transfer(banking)
            elif choice == "7":
                save_to_file(banking)
            elif choice == "8":
                load_from_file(banking)
            elif choice == "9":
                if exit_app():
                    break
            elif choice == "0":
                if switch_to_gui():
                    # 导入并启动图形界面
                    from bank_ui import main as start_gui
                    return start_gui()
            else:
                print("无效选择。请输入0到9之间的数字。")
                
        except KeyboardInterrupt:
            print("\n\n操作已取消。返回主菜单。")
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 