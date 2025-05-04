from rest_framework import serializers

class FormattedDateTimeField(serializers.DateTimeField):
    """
    Формат даты и времени.
    """
    def to_representation(self, value):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None

class BalanceSerializer(serializers.Serializer):
    """
    Сериализатор для баланса одного адреса.
    """
    balance = serializers.FloatField()

class BalanceBatchRequestSerializer(serializers.Serializer):
    """
    Сериализатор для входных данных GetBalanceBatchView.
    """
    addresses = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
        error_messages={
            "required": "Поле 'addresses' обязательно.",
            "empty": "Список адресов не может быть пустым."
        }
    )

class BalanceBatchResponseSerializer(serializers.Serializer):
    """
    Сериализатор для выходных данных GetBalanceBatchView.
    """
    balances = serializers.ListField(child=serializers.FloatField())

class TopHolderSerializer(serializers.Serializer):
    """
    Сериализатор для одного топового держателя.
    """
    address = serializers.CharField()
    balance = serializers.FloatField()

class TopHoldersSerializer(serializers.Serializer):
    """
    Сериализатор для списка топовых держателей.
    """
    top_holders = TopHolderSerializer(many=True)

class TopHolderWithTransactionSerializer(serializers.Serializer):
    """
    Сериализатор для одного топового держателя с датой последней транзакции.
    """
    address = serializers.CharField()
    balance = serializers.FloatField()
    last_transaction_date = FormattedDateTimeField()

class TopHoldersWithTransactionsSerializer(serializers.Serializer):
    """
    Сериализатор для списка топовых держателей с датами последних транзакций.
    """
    top_holders = TopHolderWithTransactionSerializer(many=True)

class TokenInfoSerializer(serializers.Serializer):
    """
    Сериализатор для информации о токене.
    """
    name = serializers.CharField()
    symbol = serializers.CharField()
    totalSupply = serializers.FloatField()