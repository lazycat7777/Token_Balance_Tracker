from django.urls import path
from apps.token_app.views import (
    GetBalanceView,
    GetBalanceBatchView,
    GetTopHoldersView,
    GetTopHoldersWithTransactionsView,
    GetTokenInfoView,
)

urlpatterns = [
    path("get_balance/", GetBalanceView.as_view(), name="get_balance"),
    path("get_balance_batch/", GetBalanceBatchView.as_view(), name="get_balance_batch"),
    path("get_top_holders/", GetTopHoldersView.as_view(), name="get_top_holders"),
    path(
        "get_top_holders_with_transactions/",
        GetTopHoldersWithTransactionsView.as_view(),
        name="get_top_holders_with_transactions",
    ),
    path("get_token_info/", GetTokenInfoView.as_view(), name="get_token_info"),
]