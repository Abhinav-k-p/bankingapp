from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.contrib.auth import get_user_model
from django.conf import settings


class CustomUser(AbstractUser):
    USER = 'user'
    STAFF = 'staff'
    

    ROLE_CHOICES = [
        (USER, 'User'),
        (STAFF, 'Staff'),
        
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    email = models.EmailField(unique=True)

    def _str_(self):
        return self.username
    

class Account(models.Model):
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def str(self):
        return f"Account {self.account_number}"
    
    
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.save()

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.save()
    

    

class SavingsAccount(Account):
    
    def _str_(self):
        return f"Savings Account - {self.account_number}"
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)
    def generate_account_number(self):
        # Generate a random account number
        return ''.join(random.choices(string.digits, k=10))
    
    def _str_(self):
        return f"Savings Account - {self.account_number}"
    

    def deposit(self, amount):
        if amount > 0:
            super().deposit(amount)

    def withdraw(self, amount):
        if amount > 0 and amount <= self.balance:
            super().withdraw(amount)


class CurrentAccount(Account):
    
    def _str_(self):
        return f"Current Account - {self.account_number}"
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)
    def generate_account_number(self):
        # Generate a random account number
        return ''.join(random.choices(string.digits, k=10))
    
    def _str_(self):
        return f"Current Account - {self.account_number}"
    
    def deposit(self, amount):
        if amount > 0:
            super().deposit(amount)

    def withdraw(self, amount):
        if amount > 0 and amount <= self.balance:
            super().withdraw(amount)


class FixedDepositAccount(models.Model):
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    duration_months = models.IntegerField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def _str_(self):
        return f"Fixed Deposit Account - {self.account_number}"

class RecurringDepositAccount(models.Model):
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    installment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    duration_months = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class Transaction(models.Model):
    TRANSACTION_CHOICES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)  # Add the description field
    
    def _str_(self):
        return f"{self.transaction_type} of {self.amount} on {self.transaction_date} for account {self.account}"

class FundTransfer(models.Model):
    sender_account_number = models.CharField(max_length=10)
    receiver_account_number = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    


class InterestRate(models.Model):
    LOAN_TYPES = [
        ('Personal Loan', 'Personal Loan'),
        ('Home Loan', 'Home Loan'),
        ('Car Loan', 'Car Loan'),
        ('Education Loan', 'Education Loan'),
        # Add more loan types as needed
    ]

    loan_type = models.CharField(max_length=100, choices=LOAN_TYPES, unique=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # Interest rate in percentage

    def _str_(self):
        return f"{self.loan_type} Interest Rate: {self.rate}%"

class LoanApplication(models.Model):
    LOAN_TYPES = [
        ('Personal Loan', 'Personal Loan'),
        ('Home Loan', 'Home Loan'),
        ('Car Loan', 'Car Loan'),
        ('Education Loan', 'Education Loan'),
        # Add more loan types as needed
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loan_applications')
    loan_type = models.CharField(max_length=100, choices=LOAN_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    duration_months = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_date = models.DateField(auto_now_add=True)

    def _str_(self):
        return f"{self.user.username} - {self.loan_type} Application"
    
class LoanApproval(models.Model):
    loan_application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE)
    approved_date = models.DateField(auto_now_add=True)
    new_status = models.CharField(max_length=20, choices=LoanApplication.STATUS_CHOICES)

    def _str_(self):
        return f"{self.loan_application.user.username} - {self.loan_application.loan_type} Approval"


class Budget(models.Model):
    account_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    

    def _str_(self):
        return self.name
    
