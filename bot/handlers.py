import requests
from bs4 import BeautifulSoup
from lxml import html
from aiogram import types
import pandas as pd
import os
from .db import save_to_db


REQUIRED_COLUMNS = {'title', 'url', 'xpath'}


async def start(message: types.Message):
    await message.answer('Привет! Пришлите мне Excel файл с информацией о сайтах для парсинга.')

async def handle_file(message: types.Message):
    if message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        os.makedirs("data", exist_ok=True)
        
        file_name = os.path.join('data', message.document.file_name)
        
        await message.document.download(destination=file_name)
        
        df = pd.read_excel(file_name)
        missing_columns = REQUIRED_COLUMNS - set(df.columns)

        if missing_columns:
            await message.reply(f'Ошибка: В файле отсутствуют необходимые колонки: {", ".join(missing_columns)}')
        else:
            
            table_string = df.to_markdown(index=False)

            await message.reply(f'Содержимое файла:\n<pre>{table_string}</pre>', parse_mode='HTML')

            avg_price = await calculate_average_price(df)
            if avg_price is not None:
                await message.reply(f'Средняя цена по всем сайтам: {avg_price:.2f}', parse_mode='HTML')
            else:
                await message.reply(f'Мы не смогли найти среднюю цену по сайтам', parse_mode='HTML')
            save_to_db(df)
            await message.reply('Данные успешно сохранены в базу данных.')

        os.remove(file_name)
    else:
        await message.reply('Пожалуйста, загрузите Excel файл.')

async def calculate_average_price(df) -> float | None:
    all_prices = []

    for _, row in df.iterrows():
        url = row['url']
        xpath = row['xpath']
        prices = []

        try:
            response = requests.get(url)
            tree = html.fromstring(response.content)

            elements = tree.xpath(xpath)
            for element in elements:
                price_text = element.text_content().strip()
                print(price_text)
                price = extract_price(price_text)
                if price:
                    prices.append(price)

            if prices:
                all_prices.extend(prices)

        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

    if all_prices:
        avg_price = sum(all_prices) / len(all_prices)
        return avg_price
    else:
        return None

def extract_price(price_text):

    price_text = ''.join(char for char in price_text if char.isdigit() or char == '.')
    try:
        return float(price_text)
    except ValueError:
        return None