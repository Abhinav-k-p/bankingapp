

from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    
    path('savings/', CreateSavingsAccountView.as_view(), name='savings-account-list'),
    path('current/', CreateCurrentAccountView.as_view(), name='current-account-list'),
    path('fixed-deposit/', CreateFixedDepositAccountView.as_view(), name='fixed-deposit-account-list'),
    path('recurring-deposit/', CreateRecurringDepositAccountView.as_view(), name='recurring-deposit-account-list'),
    path('transaction/', TransactionAPIView.as_view(), name='transaction'),
    # path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('fundtransfer/', FundTransferView.as_view(), name='fundtransfer'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('loan-interest/', InterestRateCreateAPIView.as_view(), name='create_interest_rate'),
    path('interest/<int:pk>/', InterestRateUpdateDestroyAPIView.as_view(), name='interest-rate-detail'),
    path('loan-applications/', LoanApplicationCreateAPIView.as_view(), name='loan-application-create'),
    path('loans/', InterestListAPIView.as_view(), name='loan_list'),
    path('view-loans/', LoanApplicationListAPIView.as_view(), name='loan-list'),
    path('approve/', LoanApprovalAPIView.as_view(), name='loan-approval'),
    path('loan-applied/', UserLoanApplicationListView.as_view(), name='user_loan_applications'),
    path('budgets/', BudgetListCreateAPIView.as_view(), name='budget-list-create'),
    path('transactionhistory/', TransactionHistoryAPIView.as_view(), name='transaction_history_by_account'),
    path('fixed-deposit-accounts/', ViewAllFixedDepositAccounts.as_view(), name='fixed_deposit_accounts'),
    path('Recurrent-deposit-accounts/', ViewAllRecurringDepositAccounts.as_view(), name='Recurrent_deposit_accounts'),
    path('update/', ProfileUpdateAPIView.as_view(), name='profile-update'),
    
]


