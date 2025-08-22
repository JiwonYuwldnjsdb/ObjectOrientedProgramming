class BankAccount:
    total_accounts = 0
    
    def __init__(self, account_number, owner_name):
        self.account_number = account_number
        self.owner_name = owner_name
        self.balance = 0
        BankAccount.total_accounts += 1
    
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount

    def withdraw(self, amount):
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
    
    def display_balance(self):
        print(f"{self.owner_name}님의 현재 잔액은 {self.balance}원입니다.")

user1 = BankAccount(123123, "홍길동")
user1.deposit(100000)
user1.withdraw(50000)

user2 = BankAccount(234234, "김철수")
user2.deposit(2000)
user2.withdraw(30000)

user3 = BankAccount(345345, "김영희")
user3.deposit(15000)
user3.withdraw(2000)

user1.display_balance()
user2.display_balance()
user3.display_balance()
print(BankAccount.total_accounts)