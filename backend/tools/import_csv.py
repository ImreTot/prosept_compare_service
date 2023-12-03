import csv

from products.models import Dealer, DealerPrice, Product

ITEMS_IN_MARKETING_DEALERPRICE = 7


def import_dealers_from_csv(path_to_csv):
    """
    Функция принимает путь к csv-файлу со списком дилеров.
    На основе обработанных данных создаются записи в БД.
    """
    with open(path_to_csv, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)
        dealer_list = [
            Dealer(id=id,
                   name=name)
            for id, name in csv_reader
        ]
        Dealer.objects.bulk_create(dealer_list)


def import_products_from_csv(path_to_csv):
    """
    Функция принимает путь со списком продуктов производителя.
    На основе обработанных данных создаются записи в БД.
    """
    with open(path_to_csv, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)
        products_list = [
            Product(
                article=article,
                ean_13=int(float(ean_13)) if ean_13 else None,
                name=name,
                cost=cost if cost else None,
                recommended_price=recommended_price
                if recommended_price else None,
                category_id=int(float(category_id))
                if category_id else None,
                ozon_name=ozon_name,
                name_1c=name_1c,
                wb_name=wb_name,
                ozon_article=ozon_article,
                wb_article=wb_article,
                ym_article=ym_article,
                wb_article_td=wb_article_td)
            for row_number, id, article, ean_13, name, cost,
            recommended_price, category_id, ozon_name,
            name_1c, wb_name, ozon_article, wb_article,
            ym_article, wb_article_td
            in csv_reader
        ]
        Product.objects.bulk_create(products_list)


def import_prices_from_csv(path_to_csv):
    """
    Функция принимает путь со списком объявлений дилеров.
    На основе обработанных данных создаются записи в БД.
    """
    with open(path_to_csv, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)
        dealers_dict = {dealer.id: dealer for dealer in Dealer.objects.all()}
        prices_list = []
        for row in csv_reader:
            if len(row) == ITEMS_IN_MARKETING_DEALERPRICE:
                (pk, product_key, price, product_url,
                 product_name, date, dealer_id) = row
                prices_list.append(
                    DealerPrice(
                        product_key=int(float(product_key))
                        if product_key.isdigit() else None,
                        price=float(price) if price else None,
                        product_url=product_url,
                        product_name=product_name,
                        date=date,
                        dealer_id=dealers_dict[int(dealer_id)]
                    )
                )
        DealerPrice.objects.bulk_create(prices_list)


# временные пути для файлов
path_dealer = 'data/marketing_dealer.csv'
path_product = 'data/marketing_product.csv'
path_prices = 'data/marketing_dealerprice.csv'
