import csv
import os
from decimal import Decimal
from typing import Dict, List, Optional, Tuple


class BankAccount:
    """表示银行系统中的一个银行账户。"""

    def __init__(self, account_id: str, owner_name: str, balance: Decimal = Decimal('0.00')):
        """
        初始化一个新的银行账户。
        
        参数:
            account_id: 账户的唯一标识符
            owner_name: 账户所有者的姓名
            balance: 初始账户余额（默认为0）
        """
        self.account_id = account_id
        self.owner_name = owner_name
        self._balance = Decimal('0.00')  # 从零开始，然后存款
        
        # 如果提供了初始余额，则存入
        if balance > Decimal('0.00'):
            self.deposit(balance)
    
    @property
    def balance(self) -> Decimal:
        """获取账户的当前余额。"""
        return self._balance
    
    def deposit(self, amount: Decimal) -> bool:
        """
        向账户存款。
        
        参数:
            amount: 存款金额（必须为正数）
            
        返回:
            如果存款成功返回True，否则返回False
        """
        if amount <= Decimal('0.00'):
            return False
        
        self._balance += amount
        return True
    
    def withdraw(self, amount: Decimal) -> bool:
        """
        从账户取款。
        
        参数:
            amount: 取款金额（必须为正数且小于等于余额）
            
        返回:
            如果取款成功返回True，否则返回False
        """
        if amount <= Decimal('0.00') or amount > self._balance:
            return False
        
        self._balance -= amount
        return True
    
    def to_dict(self) -> Dict:
        """将账户转换为字典以便存储。"""
        return {
            'account_id': self.account_id,
            'owner_name': self.owner_name,
            'balance': str(self._balance)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BankAccount':
        """从字典数据创建账户。"""
        return cls(
            account_id=data['account_id'],
            owner_name=data['owner_name'],
            balance=Decimal(data['balance'])
        )


class BankingSystem:
    """管理系统中的所有银行账户和操作。"""
    
    def __init__(self):
        """初始化一个没有账户的新银行系统。"""
        self.accounts: Dict[str, BankAccount] = {}
    
    def create_account(self, account_id: str, owner_name: str, 
                       initial_balance: Decimal = Decimal('0.00')) -> Tuple[bool, Optional[str]]:
        """
        创建一个新的银行账户。
        
        参数:
            account_id: 账户的唯一标识符
            owner_name: 账户所有者的姓名
            initial_balance: 初始余额（必须 >= 0）
            
        返回:
            包含（成功状态，错误信息（如果有））的元组
        """
        # 验证输入
        if not account_id or not owner_name:
            return False, "账户ID和所有者姓名不能为空"
            
        if account_id in self.accounts:
            return False, f"账户ID '{account_id}' 已存在"
            
        if initial_balance < Decimal('0.00'):
            return False, "初始余额不能为负数"
        
        # 创建账户
        account = BankAccount(account_id, owner_name, initial_balance)
        self.accounts[account_id] = account
        
        return True, None
    
    def get_account(self, account_id: str) -> Optional[BankAccount]:
        """通过ID获取账户，如果不存在则返回None。"""
        return self.accounts.get(account_id)
    
    def deposit(self, account_id: str, amount: Decimal) -> Tuple[bool, Optional[str]]:
        """
        向账户存款。
        
        参数:
            account_id: 要存款的账户ID
            amount: 存款金额（必须为正数）
            
        返回:
            包含（成功状态，错误信息（如果有））的元组
        """
        account = self.get_account(account_id)
        if not account:
            return False, f"未找到账户 '{account_id}'"
        
        if amount <= Decimal('0.00'):
            return False, "存款金额必须为正数"
        
        success = account.deposit(amount)
        if success:
            return True, None
        else:
            return False, "存款失败"
    
    def withdraw(self, account_id: str, amount: Decimal) -> Tuple[bool, Optional[str]]:
        """
        从账户取款。
        
        参数:
            account_id: 要取款的账户ID
            amount: 取款金额（必须为正数且小于等于余额）
            
        返回:
            包含（成功状态，错误信息（如果有））的元组
        """
        account = self.get_account(account_id)
        if not account:
            return False, f"未找到账户 '{account_id}'"
        
        if amount <= Decimal('0.00'):
            return False, "取款金额必须为正数"
        
        if amount > account.balance:
            return False, "余额不足"
        
        success = account.withdraw(amount)
        if success:
            return True, None
        else:
            return False, "取款失败"
    
    def transfer(self, from_account_id: str, to_account_id: str, 
                 amount: Decimal) -> Tuple[bool, Optional[str]]:
        """
        在账户之间转账。
        
        参数:
            from_account_id: 来源账户的ID
            to_account_id: 目标账户的ID
            amount: 转账金额
            
        返回:
            包含（成功状态，错误信息（如果有））的元组
        """
        if from_account_id == to_account_id:
            return False, "不能向同一账户转账"
            
        source = self.get_account(from_account_id)
        destination = self.get_account(to_account_id)
        
        if not source:
            return False, f"未找到来源账户 '{from_account_id}'"
            
        if not destination:
            return False, f"未找到目标账户 '{to_account_id}'"
        
        if amount <= Decimal('0.00'):
            return False, "转账金额必须为正数"
        
        if amount > source.balance:
            return False, "转账资金不足"
        
        # 执行转账
        if source.withdraw(amount) and destination.deposit(amount):
            return True, None
        else:
            return False, "转账失败"
    
    def save_to_csv(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        将所有账户保存到CSV文件。
        
        参数:
            filename: 保存CSV文件的路径
            
        返回:
            包含（成功状态，错误信息（如果有））的元组
        """
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['account_id', 'owner_name', 'balance'])
                writer.writeheader()
                
                for account in self.accounts.values():
                    writer.writerow(account.to_dict())
            
            return True, None
        except Exception as e:
            return False, f"保存数据时出错: {str(e)}"
    
    def load_from_csv(self, filename: str) -> Tuple[bool, Optional[str]]:
        """
        从CSV文件加载账户。
        
        参数:
            filename: 要加载的CSV文件路径
            
        返回:
            包含（成功状态，错误信息（如果有））的元组
        """
        if not os.path.exists(filename):
            return False, f"未找到文件 '{filename}'"
            
        try:
            self.accounts = {}  # 清除现有账户
            
            with open(filename, 'r', newline='') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    account = BankAccount.from_dict(row)
                    self.accounts[account.account_id] = account
            
            return True, None
        except Exception as e:
            return False, f"加载数据时出错: {str(e)}"
    
    def get_all_accounts(self) -> List[BankAccount]:
        """获取系统中所有账户的列表。"""
        return list(self.accounts.values()) 