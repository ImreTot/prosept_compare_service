from products.models import Dealer, DealerPrice, Product, ProductDealerKey
from rest_framework import serializers


class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class DealerPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerPrice
        fields = '__all__'
        

class ProductDealerKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDealerKey
        fields = '__all__'
