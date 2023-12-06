from django.db import models


class Dealer(models.Model):
    """
    Модель данных для таблицы 'marketing_dealer'.
    """
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Модель данных для таблицы 'marketing_product'.
    """
    article = models.CharField(max_length=100, primary_key=True)
    ean_13 = models.FloatField(null=True)
    name = models.CharField(max_length=250)
    cost = models.FloatField(null=True)
    recommended_price = models.FloatField(null=True)
    category_id = models.IntegerField(null=True)
    ozon_name = models.CharField(max_length=250)
    name_1c = models.CharField(max_length=250)
    wb_name = models.CharField(max_length=250)
    ozon_article = models.CharField(max_length=250)
    wb_article = models.CharField(max_length=250)
    ym_article = models.CharField(max_length=250)
    wb_article_td = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class DealerPrice(models.Model):
    """
    Модель данных для таблицы 'marketing_dealerprice'.
    """
    product_key = models.IntegerField(null=True)
    price = models.FloatField(null=True)
    product_url = models.URLField(unique=True, primary_key=True)
    product_name = models.CharField(max_length=250)
    date = models.DateField()
    dealer_id = models.ForeignKey(Dealer,
                                  related_name='dealer_prices',
                                  on_delete=models.CASCADE)
    marking_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.product_url


class ProductDealerKey(models.Model):
    """
    Модель данных, связывающая DealerPrice c Product.
    Заполняется данными, возвращенными ML.
    """
    key = models.ForeignKey(DealerPrice,
                            related_name='matching_products',
                            on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product,
                                   related_name='product_dealer_keys',
                                   on_delete=models.CASCADE)
<<<<<<< HEAD
    compliance_number = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"ProductDealerKey {self.id} for Product {self.product_id}"
    

class Statistics(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_markup_count = models.IntegerField()
    none_chosen_count = models.IntegerField()
    choices_order = models.JSONField()
    chosen_options_stats = models.JSONField()

    def __str__(self):
        return f"Statistics for {self.start_date} - {self.end_date}"
