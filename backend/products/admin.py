from django.contrib import admin

from .models import Dealer, DealerPrice, Product, ProductDealerKey

admin.site.register(Dealer)
admin.site.register(Product)
admin.site.register(DealerPrice)
admin.site.register(ProductDealerKey)
