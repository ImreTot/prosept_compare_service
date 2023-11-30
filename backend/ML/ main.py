#!/usr/bin/env python
# coding: utf-8

# In[19]:


# библиотеки
import io
import numpy as np
import pandas as pd
import re
import torch
from transformers import BertModel, BertTokenizer
from scipy.spatial.distance import cosine
import json
import warnings

# константы
SPACES = r'(?<=[а-яА-Я])(?=[a-zA-Z])|(?<=[a-zA-Z])(?=[а-яА-Я])'
COMMA_OUT_LINE = r',\s'
DROP_BRACKET = r'[()\s]'
DUP_SPACES = r'([ ])\1+'
DROP_SYMBOL = r'["\-/]'

# модель
bert_version = 'cointegrated/LaBSE-en-ru'
tokenizer = BertTokenizer.from_pretrained(bert_version)
model = BertModel.from_pretrained(bert_version)

# настройка
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.eval()
model.to(device)

# функция для предобработки текста
def clean_string(input_string: str) -> str:
    """
    Parameters:
    input_string (str): Строка для очистки.

    Returns:
    output_string (str): Очищенная строка.
    """
    input_string = re.sub(SPACES, ' ', input_string.lower()) # нижний регистр/пропущенные пробелы
    input_string = re.sub(COMMA_OUT_LINE, ' ', input_string) # убираем внешние запятые
    input_string = re.sub(DROP_BRACKET, ' ', input_string) # убираем '(',')'
    input_string = input_string.replace('prosept', '').replace('просепт', '') # убираем название фирмы
    input_string = re.sub(DROP_SYMBOL, ' ', input_string)
    output_string = re.sub(DUP_SPACES, r'\1', input_string) # обработка двойных пробелов
    return output_string

# функция для получения эмбеддингов
def sentence_embedding(sentence: str) -> np.ndarray:
    """
    Parameters:
    sentence (str): Название товара для создания эмбеддинга.

    Returns:
    np.ndarray: Эмбеддинг названия товара в виде массива NumPy.
    """
    input_ids = torch.tensor(tokenizer.encode(sentence)).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(input_ids)
        last_hidden_states = outputs[0].squeeze(0)
        sentence_embedding = torch.mean(last_hidden_states, dim=0)
    return sentence_embedding.cpu().numpy()

# функция для рассчета метрики
def cos_similarity(embedding_1: np.ndarray, 
                   embedding_2: np.ndarray) -> float:
    """
    Parameters:
    embedding_1 (np.ndarray): Эмбеддинг первого товара.
    embedding_2 (np.ndarray): Эмбеддинг второго товара.

    Returns:
    float: Косинусная схожесть между эмбеддингами.
    """
    return 1 - cosine(embedding_1, embedding_2)

# функция для ранжирования
def rank_products(dealer_product: str,
                  marketing_product_df: pd.DataFrame,
                  products_embedding: pd.Series,
                  quantity_int: int) -> list[str]:
    """
    Parameters:
    dealer_product (str): Название товара дилера.
    marketing_product_df (pd.DataFrame): Данные о товарах производитимых заказчиком.
    products_embedding (pd.Series): Эмбеддингами названий товаров производитимых заказчиком.
    quantity_int (int): Количество возвращаемых, наиболее подходящих товаров.

    Returns:
    list[str]: Список ранжированных товаров.
    """
    dealer_embedding = sentence_embedding(dealer_product)
    marketing_product_df['scores'] = products_embedding.apply(lambda x: cos_similarity(dealer_embedding, x))
    return marketing_product_df.sort_values(by='scores', ascending=False).head(quantity_int)['article'].to_list()



# основная функция
def result(marketing_product_csv: io.TextIOBase,
           marketing_dealerprice_csv: io.TextIOBase, 
           quantity_int: int) -> str:
    """
    Parameters:
    marketing_product_csv (io.TextIOBase): Файл CSV с информацией о товарах производимых заказчиком.
    marketing_dealerprice_csv (io.TextIOBase): Файл CSV с информацией о товарах дилера.
    quantity_int (int): Количество возвращаемых, наиболее подходящих товаров заказчика.

    Returns:
    str: Результат в формате JSON.
    """
    # csv to dataset
    marketing_product_df = pd.read_csv(marketing_product_csv, sep=';')
    marketing_dealerprice_df = pd.read_csv(marketing_dealerprice_csv, sep=';')
    
    # clean df
    marketing_product_df = marketing_product_df[['article', 'name']].dropna().drop_duplicates().reset_index(drop=True)
    marketing_dealerprice_df = marketing_dealerprice_df[['product_url', 'product_name']].dropna().drop_duplicates().reset_index(drop=True)
    
    # clean string
    marketing_product_df['name'] = marketing_product_df['name'].astype('str').apply(clean_string)
    marketing_dealerprice_df['product_name'] = marketing_dealerprice_df['product_name'].astype('str').apply(clean_string)
    
    # embedding product
    products_embedding = marketing_product_df['name'].apply(sentence_embedding)
    
    # predict
    rez = marketing_dealerprice_df.set_index('product_url')['product_name'].apply(lambda x: rank_products(x, 
                                                                                                          marketing_product_df, 
                                                                                                          products_embedding, 
                                                                                                          quantity_int)).to_dict()
    # result to JSON
    rez_json = json.dumps(rez, ensure_ascii=False)
    
    return rez_json

