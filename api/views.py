
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import authenticate
from .serializers import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import viewsets
from rest_framework import generics
from django.http import JsonResponse
import json
from .permissions import IsAdminOrStaffUser,IsCustomerUser
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import *
from decimal import Decimal
from django.core.mail import send_mail


class RegisterAPIView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        role = request.data.get('role')
        request.data['is_staff'] = role == 'staff'
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
User = get_user_model()
class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure user is authenticated
    def put(self, request, format=None):
            user = request.user
            data = request.data.copy()

            if 'password' in data:
                password = data.pop('password')
                user.set_password(password)
                user.save()

            serializer = UserRegistrationSerializer(user, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Profile update successful'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
 
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
           
            user = authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                user.save()  
                # Generate access token
                access_token = AccessToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'access': str(access_token),
                })
            else:
                return Response({'detail': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CreateSavingsAccountView(CreateAPIView):
    queryset = SavingsAccount.objects.all()
    serializer_class = SavingsAccountSerializer

    def perform_create(self, serializer):
        # Assign the authenticated user to the account being created
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Get the created account instance
        instance = serializer.instance

        # Modify the response data to include the account number
        response_data = serializer.data
        response_data['account_number'] = instance.account_number  # Add account number to response

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get(self, request):
            user_accounts = SavingsAccount.objects.filter(user=request.user)
            serializer = SavingsAccountSerializer(user_accounts, many=True)
            return Response(serializer.data)


class CreateCurrentAccountView(generics.CreateAPIView):
    queryset = CurrentAccount.objects.all()
    serializer_class = CurrentAccountSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Get the created account instance
        instance = serializer.instance

        # Modify the response data to include the account number
        response_data = serializer.data
        response_data['account_number'] = instance.account_number  # Add account number to response

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        # Assign the authenticated user to the account being created
        serializer.save(user=self.request.user)
    def get(self, request):
            user_accounts = CurrentAccount.objects.filter(user=request.user)
            serializer = CurrentAccountSerializer(user_accounts, many=True)
            return Response(serializer.data)
    def set_transaction_limit(self, request, limit):
        # Get the current user's current account
        current_account = CurrentAccount.objects.get(user=request.user)
        # Set the transaction limit
        current_account.transaction_limit = limit
        current_account.save()
        return Response({'message': 'Transaction limit updated successfully'}, status=status.HTTP_200_OK)


class CreateFixedDepositAccountView(generics.CreateAPIView):
    queryset = FixedDepositAccount.objects.all()
    serializer_class = FixedDepositAccountSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        # Assign the authenticated user to the account being created
        serializer.save(user=self.request.user)
    def get(self, request, *args, **kwargs):
        user = request.user
        # Filter fixed deposit accounts based on the logged-in user
        fixed_deposit_accounts = FixedDepositAccount.objects.filter(user=user)
        serializer = FixedDepositAccountSerializer(fixed_deposit_accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateRecurringDepositAccountView(generics.CreateAPIView):
    queryset = RecurringDepositAccount.objects.all()
    serializer_class = RecurringDepositAccountSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        # Assign the authenticated user to the account being created
        serializer.save(user=self.request.user)
    def get(self, request, *args, **kwargs):
        user = request.user
        # Filter fixed deposit accounts based on the logged-in user
        Recurrent_deposit_accounts = RecurringDepositAccount.objects.filter(user=user)
        serializer = RecurringDepositAccountSerializer(Recurrent_deposit_accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    TRANSACTION_LIMIT = 100000
    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            account_number = serializer.validated_data.get('account_number')
            transaction_type = serializer.validated_data.get('transaction_type')
            amount = serializer.validated_data.get('amount')
            description = serializer.validated_data.get('description', '')

            try:
                account = Account.objects.get(account_number=account_number)
                if transaction_type == 'DEPOSIT':
                    if amount > self.TRANSACTION_LIMIT:
                        return Response({"message": f"Deposit amount exceeds the transaction limit of {self.TRANSACTION_LIMIT}"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    account.deposit(amount)
                    message = "Deposit successful"
                elif transaction_type == 'WITHDRAWAL':
                    if amount > self.TRANSACTION_LIMIT:
                        return Response({"message": f"Withdrawal amount exceeds the transaction limit of {self.TRANSACTION_LIMIT}"}, status=status.HTTP_400_BAD_REQUEST)
                    if amount > account.balance:
                        return Response({"message": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
                    account.withdraw(amount)
                    if amount > account.balance:
                        return Response({"message": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
                    account.withdraw(amount)
                    message = "Withdrawal successful"
                    budget = Budget.objects.filter(name=description).first()
                    if budget:
                        budget.total_amount -= amount
                        budget.save()
                        if budget.total_amount < 0:
                            subject = 'Budget Exceeded'
                            message = f'Your budget "{budget.name}" has been exceeded.'
                            recipient_list = [request.user.email]  # Assuming each budget has a user field representing the owner
                            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)


                else:
                    return Response({"message": "Invalid transaction type"}, status=status.HTTP_400_BAD_REQUEST)

                transaction = Transaction.objects.create(account=account, transaction_type=transaction_type, amount=amount, description=description)
                return Response({"message": message}, status=status.HTTP_201_CREATED)

            except Account.DoesNotExist:
                return Response({"message": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class FundTransferView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = FundTransferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
    

class InterestRateCreateAPIView(generics.CreateAPIView):
    queryset = InterestRate.objects.all()
    serializer_class = InterestRateSerializer
    permission_classes = [IsAdminUser]

class InterestRateUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InterestRate.objects.all()
    serializer_class = InterestRateSerializer
    permission_classes = [IsAuthenticated]

class InterestListAPIView(generics.ListAPIView):
    queryset = InterestRate.objects.all()
    serializer_class = InterestRateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InterestRate.objects.all()



class LoanApplicationCreateAPIView(generics.CreateAPIView):
    queryset = LoanApplication.objects.all()
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.validated_data['user'] = request.user

        loan_type = serializer.validated_data['loan_type']

        amount = Decimal(serializer.validated_data['amount'])
        duration_years = Decimal(serializer.validated_data['duration_months']) / Decimal('12')

        try:
            interest_rate_obj = InterestRate.objects.get(loan_type=loan_type)
            interest_rate = Decimal(interest_rate_obj.rate) / Decimal('100')  # Convert to Decimal and percentage
        except InterestRate.DoesNotExist:
            interest_rate = Decimal('0.10')  # Default interest rate of 10%

        monthly_interest_rate = interest_rate / Decimal('12')

        total_payments = duration_years * Decimal('12')

        # Calculate monthly payment (EMI)
        monthly_payment = (amount * monthly_interest_rate) / (Decimal('1') - (Decimal('1') + monthly_interest_rate) ** -total_payments)

        # Calculate total amount payable after loan term
        total_amount_payable = monthly_payment * total_payments

        # Save the loan application
        self.perform_create(serializer)

        # Retrieve the saved loan application instance
        loan_application = serializer.instance

        return Response({
            "loan_details": {
                "Loan Amount": f"Rs {amount}",
                "Tenure": f"{duration_years} years",
                "Interest Rate": f"{interest_rate * 100}%",
                "Total Amount Payable After Loan Term": f"Rs {total_amount_payable}",
                "Monthly Payment (EMI)": f"Rs {monthly_payment}",
                "Applied Date": loan_application.applied_date.strftime("%Y-%m-%d %H:%M:%S"),
                "Status": loan_application.status,
            },
            "message": "Loan application created successfully."
        }, status=status.HTTP_201_CREATED)

class LoanApplicationListAPIView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        # Retrieve the authenticated user
        user = self.request.user
        # Filter loan applications based on the user
        return LoanApplication.objects.filter(user=user)


class LoanApprovalAPIView(generics.CreateAPIView):
    queryset = LoanApproval.objects.all()
    serializer_class = LoanApprovalSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Update loan application status
        loan_application = serializer.validated_data['loan_application']
        new_status = serializer.validated_data['new_status']
        loan_application.status = new_status
        loan_application.save()

        # Create loan approval instance
        loan_approval = serializer.save()

        send_mail(
            'Loan Approval Notification',
            f'Your loan application for {loan_application.loan_type} has been {new_status.lower()}.',
            'akp087@gmail.com',
            [loan_application.user.email],
            fail_silently=True,
        )

        return Response({'message': 'Loan status updated and notification sent'}, status=status.HTTP_201_CREATED)
    
class UserLoanApplicationListView(generics.ListAPIView):
    serializer_class = LoanApplicationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # user = self.request.user
        return LoanApplication.objects.all()
    
class BudgetListCreateAPIView(generics.ListCreateAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

class TransactionHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        account_number = request.data.get('account_number')
        if not account_number:
            return Response({"message":"account number is requried"},status=status.HTTP_400_BAD_REQUEST)
        try:
            transactions = Transaction.objects.filter(account__account_number=account_number)
            serializer = TransactionHistorySerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({"message": "No transaction history found for the provided account number"}, status=status.HTTP_404_NOT_FOUND)
    
class ViewAllFixedDepositAccounts(generics.ListAPIView):
    queryset = FixedDepositAccount.objects.all()
    serializer_class = FixedDepositAccountSerializer
    permission_classes = [ IsAdminUser]
    
class ViewAllRecurringDepositAccounts(generics.ListAPIView):
    queryset = RecurringDepositAccount.objects.all()
    serializer_class = RecurringDepositAccountSerializer
    permission_classes = [IsAdminUser]
    