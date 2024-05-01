from django.urls import path, include
from .views import IssueBookAPIView, ReturnBookAPIView, FulFillAPIView

urlpatterns = [
    path('issue_book/', IssueBookAPIView.as_view(), name='issue_book'),
    path('return_book/', ReturnBookAPIView.as_view(), name='return_book'),
    path('fulfill_reservation/', FulFillAPIView.as_view(), name='fulfill_reservation'),
]
