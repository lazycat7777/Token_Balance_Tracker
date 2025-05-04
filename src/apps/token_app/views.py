from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.token_app.services.blockchain_service import BlockchainService
from apps.token_app.serializers import (
    BalanceSerializer,
    BalanceBatchRequestSerializer,
    BalanceBatchResponseSerializer,
    TopHoldersSerializer,
    TopHoldersWithTransactionsSerializer,
    TokenInfoSerializer,
)


class GetBalanceView(APIView):
    """
    Возвращает баланс токена для указанного адреса.
    """
    serializer_class = BalanceSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="address",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Адрес Polygon (строка в формате '0x...')",
                required=True,
            ),
        ],
        responses={200: BalanceSerializer},
    )
    
    async def get(self, request, *args, **kwargs):
        address = request.query_params.get("address")
        if not address:
            return Response({"error": "Адрес не указан"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            balance = await BlockchainService.get_balance(address)
            return Response(BalanceSerializer({"balance": balance}).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetBalanceBatchView(APIView):
    """
    Возвращает балансы токенов для списка адресов.
    """
    serializer_class = BalanceBatchResponseSerializer

    @extend_schema(
        request=BalanceBatchRequestSerializer,
        responses={200: BalanceBatchResponseSerializer},
    )
    
    async def post(self, request, *args, **kwargs):
        serializer = BalanceBatchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        if not isinstance(validated_data, dict) or "addresses" not in validated_data:
            return Response({"error": "Адреса не указаны"}, status=status.HTTP_400_BAD_REQUEST)
        addresses = validated_data.get("addresses")
        if not addresses:
            return Response({"error": "Адреса не указаны"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            balances = await BlockchainService.get_balances_batch(addresses)
            return Response(BalanceBatchResponseSerializer({"balances": balances}).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetTopHoldersView(APIView):
    """
    Возвращает топ N адресов по балансам токенов.
    """
    serializer_class = TopHoldersSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="n",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Количество топовых адресов",
                default=5,
            ),
        ],
        responses={200: TopHoldersSerializer},
    )
    
    async def get(self, request, *args, **kwargs):
        try:
            n = int(request.query_params.get("n", 5))
            top_holders = await BlockchainService.get_top_holders(n)
            top_holders_data = [{"address": addr, "balance": bal} for addr, bal in top_holders]
            return Response(TopHoldersSerializer({"top_holders": top_holders_data}).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetTopHoldersWithTransactionsView(APIView):
    """
    Возвращает топ N адресов по балансам токенов с датами последних транзакций.
    """
    serializer_class = TopHoldersWithTransactionsSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="n",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Количество топовых адресов",
                default=5,
            ),
        ],
        responses={200: TopHoldersWithTransactionsSerializer},
    )
    async def get(self, request, *args, **kwargs):
        try:
            n = int(request.query_params.get("n", 5))
            top_holders = await BlockchainService.get_top_holders_with_transactions(n)
            top_holders_data = [
                {"address": addr, "balance": bal, "last_transaction_date": date}  
                for addr, bal, date in top_holders
            ]
            return Response(TopHoldersWithTransactionsSerializer({"top_holders": top_holders_data}).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetTokenInfoView(APIView):
    """
    Возвращает информацию о токене.
    """
    serializer_class = TokenInfoSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="address",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Адрес Polygon (строка в формате '0x...')",
                required=True,
            ),
        ],
        responses={200: TokenInfoSerializer},
    )
    
    async def get(self, request, *args, **kwargs):
        try:
            token_info = await BlockchainService.get_token_info()
            return Response(TokenInfoSerializer(token_info).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)