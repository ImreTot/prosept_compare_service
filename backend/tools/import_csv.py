import csv
import io

import pandas as pd
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


def export_model_to_csv(model):
    # Открываем объект для записи CSV в памяти
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)

    # Заголовки CSV - имена полей модели
    headers = [field.name for field in model._meta.fields]
    csv_writer.writerow(headers)

    # Записываем данные из базы данных в CSV
    for row in model.objects.all():
        csv_writer.writerow([getattr(row, field) for field in headers])

    # Возвращаем объект для чтения CSV из памяти
    csv_buffer.seek(0)

    return csv_buffer


def send_csv_to_model(file_path):
    # Открываем файл для чтения
    with open(file_path, 'r') as file:
        # Открываем объект для записи CSV в памяти
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)

        # Читаем первую строку файла, которая обычно содержит заголовки
        headers = file.readline().strip().split(',')
        csv_writer.writerow(headers)

        # Читаем остальные строки и записываем их в CSV
        for line in file:
            row_data = line.strip().split(',')
            csv_writer.writerow(row_data)

        # Возвращаем объект для чтения CSV из памяти
        csv_buffer.seek(0)

        return csv_buffer


def export_db_to_csv(model, file_path):
    # Заголовки CSV - имена полей модели
    headers = [field.name for field in model._meta.fields]

    # Создаем DataFrame из данных модели
    data = [[getattr(row, field) for field in headers] for row in model.objects.all()]
    df = pd.DataFrame(data, columns=headers)

    # Сохраняем DataFrame в CSV файл
    df.to_csv(file_path, index=False)


# временные пути для файлов
path_dealer = 'data/marketing_dealer.csv'
path_product = 'data/marketing_product.csv'
path_prices = 'data/marketing_dealerprice.csv'
