import unittest
import os
from decimal import Decimal
from tempfile import NamedTemporaryFile

from banking_system import BankAccount, BankingSystem


class TestBankAccount(unittest.TestCase):
    """银行账户类的测试用例。"""
    
    def test_init(self):
        """测试账户初始化和余额。"""
        # 默认余额应为0
        account = BankAccount("1", "张三")
        self.assertEqual(account.balance, Decimal('0.00'))
        
        # 初始余额应正确设置
        account = BankAccount("2", "李四", Decimal('100.00'))
        self.assertEqual(account.balance, Decimal('100.00'))
    
    def test_deposit(self):
        """测试存款功能。"""
        account = BankAccount("1", "张三")
        
        # 有效存款
        self.assertTrue(account.deposit(Decimal('50.75')))
        self.assertEqual(account.balance, Decimal('50.75'))
        
        # 另一笔有效存款应增加到余额中
        self.assertTrue(account.deposit(Decimal('25.25')))
        self.assertEqual(account.balance, Decimal('76.00'))
        
        # 零或负数存款应失败
        self.assertFalse(account.deposit(Decimal('0.00')))
        self.assertFalse(account.deposit(Decimal('-10.00')))
        
        # 失败存款后余额应保持不变
        self.assertEqual(account.balance, Decimal('76.00'))
    
    def test_withdraw(self):
        """测试取款功能。"""
        account = BankAccount("1", "张三", Decimal('100.00'))
        
        # 有效取款
        self.assertTrue(account.withdraw(Decimal('40.00')))
        self.assertEqual(account.balance, Decimal('60.00'))
        
        # 不能取零或负数金额
        self.assertFalse(account.withdraw(Decimal('0.00')))
        self.assertFalse(account.withdraw(Decimal('-10.00')))
        
        # 不能取超过余额的金额（无透支）
        self.assertFalse(account.withdraw(Decimal('70.00')))
        
        # 失败取款后余额应保持不变
        self.assertEqual(account.balance, Decimal('60.00'))
    
    def test_to_dict_and_from_dict(self):
        """测试转换为字典和从字典创建。"""
        original = BankAccount("123", "测试用户", Decimal('123.45'))
        data = original.to_dict()
        
        # 检查字典格式
        self.assertEqual(data['account_id'], "123")
        self.assertEqual(data['owner_name'], "测试用户")
        self.assertEqual(data['balance'], "123.45")
        
        # 测试从字典重新创建
        recreated = BankAccount.from_dict(data)
        self.assertEqual(recreated.account_id, "123")
        self.assertEqual(recreated.owner_name, "测试用户")
        self.assertEqual(recreated.balance, Decimal('123.45'))


class TestBankingSystem(unittest.TestCase):
    """银行系统类的测试用例。"""
    
    def setUp(self):
        """每个测试前设置新的银行系统。"""
        self.banking = BankingSystem()
    
    def test_create_account(self):
        """测试账户创建。"""
        # 有效账户创建
        success, error = self.banking.create_account("1", "张三", Decimal('100.00'))
        self.assertTrue(success)
        self.assertIsNone(error)
        
        # 账户应存在于系统中
        account = self.banking.get_account("1")
        self.assertIsNotNone(account)
        self.assertEqual(account.owner_name, "张三")
        self.assertEqual(account.balance, Decimal('100.00'))
        
        # 不能创建重复ID的账户
        success, error = self.banking.create_account("1", "另一个用户")
        self.assertFalse(success)
        self.assertIn("已存在", error)
        
        # 不能创建负余额的账户
        success, error = self.banking.create_account("2", "李四", Decimal('-50.00'))
        self.assertFalse(success)
        self.assertIn("不能为负数", error)
        
        # 空ID或名称应失败
        success, error = self.banking.create_account("", "无ID")
        self.assertFalse(success)
        
        success, error = self.banking.create_account("3", "")
        self.assertFalse(success)
    
    def test_deposit(self):
        """测试系统级存款。"""
        # 创建测试账户
        self.banking.create_account("1", "张三", Decimal('100.00'))
        
        # 有效存款
        success, error = self.banking.deposit("1", Decimal('50.00'))
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(self.banking.get_account("1").balance, Decimal('150.00'))
        
        # 不能向不存在的账户存款
        success, error = self.banking.deposit("999", Decimal('50.00'))
        self.assertFalse(success)
        self.assertIn("未找到", error)
        
        # 不能存入零或负数金额
        success, error = self.banking.deposit("1", Decimal('0.00'))
        self.assertFalse(success)
        
        success, error = self.banking.deposit("1", Decimal('-10.00'))
        self.assertFalse(success)
    
    def test_withdraw(self):
        """测试系统级取款。"""
        # 创建测试账户
        self.banking.create_account("1", "张三", Decimal('100.00'))
        
        # 有效取款
        success, error = self.banking.withdraw("1", Decimal('30.00'))
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(self.banking.get_account("1").balance, Decimal('70.00'))
        
        # 不能从不存在的账户取款
        success, error = self.banking.withdraw("999", Decimal('10.00'))
        self.assertFalse(success)
        self.assertIn("未找到", error)
        
        # 不能取零或负数金额
        success, error = self.banking.withdraw("1", Decimal('0.00'))
        self.assertFalse(success)
        
        success, error = self.banking.withdraw("1", Decimal('-10.00'))
        self.assertFalse(success)
        
        # 不能取超过余额的金额
        success, error = self.banking.withdraw("1", Decimal('100.00'))
        self.assertFalse(success)
        self.assertIn("余额不足", error)
        
        # 失败取款后余额应保持不变
        self.assertEqual(self.banking.get_account("1").balance, Decimal('70.00'))
    
    def test_transfer(self):
        """测试账户间转账。"""
        # 创建测试账户
        self.banking.create_account("1", "张三", Decimal('100.00'))
        self.banking.create_account("2", "李四", Decimal('50.00'))
        
        # 有效转账
        success, error = self.banking.transfer("1", "2", Decimal('30.00'))
        self.assertTrue(success)
        self.assertIsNone(error)
        
        # 转账后检查余额
        self.assertEqual(self.banking.get_account("1").balance, Decimal('70.00'))
        self.assertEqual(self.banking.get_account("2").balance, Decimal('80.00'))
        
        # 不能转账到同一账户
        success, error = self.banking.transfer("1", "1", Decimal('10.00'))
        self.assertFalse(success)
        self.assertIn("同一账户", error)
        
        # 不能从不存在的账户转账
        success, error = self.banking.transfer("999", "2", Decimal('10.00'))
        self.assertFalse(success)
        self.assertIn("未找到", error)
        
        # 不能转账到不存在的账户
        success, error = self.banking.transfer("1", "999", Decimal('10.00'))
        self.assertFalse(success)
        self.assertIn("未找到", error)
        
        # 不能转账零或负数金额
        success, error = self.banking.transfer("1", "2", Decimal('0.00'))
        self.assertFalse(success)
        
        success, error = self.banking.transfer("1", "2", Decimal('-10.00'))
        self.assertFalse(success)
        
        # 不能转账超过来源账户余额的金额
        success, error = self.banking.transfer("1", "2", Decimal('100.00'))
        self.assertFalse(success)
        self.assertIn("资金不足", error)
        
        # 失败转账后余额应保持不变
        self.assertEqual(self.banking.get_account("1").balance, Decimal('70.00'))
        self.assertEqual(self.banking.get_account("2").balance, Decimal('80.00'))
    
    def test_save_and_load(self):
        """测试保存和加载系统状态。"""
        # 创建测试账户
        self.banking.create_account("1", "张三", Decimal('100.00'))
        self.banking.create_account("2", "李四", Decimal('200.00'))
        
        # 使用临时文件路径而不是实际文件，以避免权限问题
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "banking_test.csv")
        
        try:
            # 保存到临时文件
            success, error = self.banking.save_to_csv(temp_path)
            self.assertTrue(success)
            self.assertIsNone(error)
            
            # 创建新的银行系统并从文件加载
            new_banking = BankingSystem()
            success, error = new_banking.load_from_csv(temp_path)
            self.assertTrue(success)
            self.assertIsNone(error)
            
            # 检查账户是否正确加载
            self.assertEqual(len(new_banking.get_all_accounts()), 2)
            self.assertEqual(new_banking.get_account("1").owner_name, "张三")
            self.assertEqual(new_banking.get_account("1").balance, Decimal('100.00'))
            self.assertEqual(new_banking.get_account("2").owner_name, "李四")
            self.assertEqual(new_banking.get_account("2").balance, Decimal('200.00'))
            
            # 测试从不存在的文件加载
            success, error = new_banking.load_from_csv("non_existent_file.csv")
            self.assertFalse(success)
            self.assertIn("未找到", error)
            
        finally:
            # 清理临时文件 - 带有适当的错误处理
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except PermissionError:
                # 在Windows上，有时文件仍在使用中
                # 由于只是测试清理，忽略错误
                pass
    
    def test_get_all_accounts(self):
        """测试获取所有账户。"""
        # 应该从没有账户开始
        self.assertEqual(len(self.banking.get_all_accounts()), 0)
        
        # 添加账户并检查列表
        self.banking.create_account("1", "张三")
        self.banking.create_account("2", "李四")
        
        accounts = self.banking.get_all_accounts()
        self.assertEqual(len(accounts), 2)
        
        # 检查账户详情
        account_ids = [acc.account_id for acc in accounts]
        self.assertIn("1", account_ids)
        self.assertIn("2", account_ids)


if __name__ == '__main__':
    unittest.main() 