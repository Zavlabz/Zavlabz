import asyncio
import json
import re
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any

import aiohttp
from bs4 import BeautifulSoup

# Константы
BASE_URL = "https://markets.businessinsider.com"
INDEX_URL = f"{BASE_URL}/index/components/s&p_500"
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


# Универсальная функция для получения текста с URL
async def fetch_text(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


# Преобразование строки в Decimal с обработкой ошибок
def to_decimal(s: str) -> Decimal:
    try:
        return Decimal(s.replace(",", "").strip())
    except InvalidOperation:
        return Decimal("0")


# Получение курса USD→RUB с сайта ЦБ РФ
async def fetch_usd_rate(session: aiohttp.ClientSession) -> Decimal:
    xml_data = await fetch_text(session, CBR_URL)
    soup = BeautifulSoup(xml_data, "lxml-xml")
    # Идентификатор для USD у ЦБ РФ: R01235
    rate_str = soup.find("Valute", {"ID": "R01235"}).Value.text.replace(",", ".")
    print(f"Текущий курс USD→RUB: {rate_str}")
    return Decimal(rate_str)


# Парсинг страницы индекса для извлечения ссылок на компании и годового роста
def parse_index_page(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("div.table-responsive table.table tbody tr")
    companies = []
    print(f"Найдено строк в таблице: {len(rows)}")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        link_tag = cells[0].find("a")
        if not link_tag:
            continue
        comp_url = BASE_URL + link_tag.get("href")
        # Извлечение годового роста (из последней ячейки)
        growth_str = cells[-1].get_text(separator=" ", strip=True)
        growth_str = growth_str.replace("%", "").replace(",", ".")
        try:
            growth = float(growth_str)
        except ValueError:
            print(f"Не удалось преобразовать рост '{growth_str}'")
            growth = 0.0
        companies.append({"url": comp_url, "growth": growth})
    return companies


# Парсинг детальной информации со страницы компании
async def parse_company_details(session: aiohttp.ClientSession, url: str, usd_rate: Decimal) -> Dict[str, Any]:
    html = await fetch_text(session, url)
    soup = BeautifulSoup(html, "lxml")

    header = soup.find("h1", class_="price-section__identifiers")
    if not header:
        print(f"Блок с именем и кодом не найден: {url}")
        return {}

    name = header.find("span", class_="price-section__label").text.strip()
    code = header.find("span", class_="price-section__category").text.strip()

    price_usd = to_decimal(soup.find("span", class_="price-section__current-value").text)
    price_rub = price_usd * usd_rate

    # Поиск P/E Ratio по текстовому шаблону
    pe_search = soup.find(string=re.compile("P/E Ratio"))
    if pe_search:
        pe = to_decimal(pe_search.find_next("span").text)
    else:
        print(f"P/E Ratio не найден для {name} ({code})")
        pe = Decimal("inf")

    # Получаем значения 52 Week Low/High
    low_tag = soup.find(string="52 Week Low")
    high_tag = soup.find(string="52 Week High")
    if low_tag and high_tag:
        week_low = to_decimal(low_tag.find_next("span").text)
        week_high = to_decimal(high_tag.find_next("span").text)
    else:
        print(f"Не найдены данные 52 Week Low/High для {name} ({code})")
        week_low, week_high = Decimal("0"), Decimal("0")

    # Вычисление потенциальной прибыли
    if week_low == 0:
        potential_profit = 0
    else:
        potential_profit = ((week_high - week_low) / week_low) * 100

    print(f"Обработана компания: {name} ({code})")
    return {
        "name": name,
        "code": code,
        "price": float(price_rub),
        "P/E": float(pe),
        "potential_profit": float(potential_profit)
    }


# Сохранение данных в JSON-файл
def save_to_json(filename: str, data: List[Dict[str, Any]]):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Сохранено {len(data)} записей в файл: {filename}")


# Сохранение топ-10 по различным критериям
def save_top_ten(companies: List[Dict[str, Any]]):
    def sort_and_save(filename: str, key_func, reverse: bool):
        sorted_list = sorted(companies, key=key_func, reverse=reverse)[:10]
        save_to_json(filename, sorted_list)

    sort_and_save("top_price.json", key_func=lambda c: c["price"], reverse=True)
    sort_and_save("top_pe.json", key_func=lambda c: c["P/E"], reverse=False)
    sort_and_save("top_growth.json", key_func=lambda c: c["growth"], reverse=True)
    sort_and_save("top_potential_profit.json", key_func=lambda c: c["potential_profit"], reverse=True)


# Основная функция: собираем курс, индекс, данные по компаниям и сохраняем результаты
async def main():
    async with aiohttp.ClientSession() as session:
        usd_rate = await fetch_usd_rate(session)
        index_html = await fetch_text(session, INDEX_URL)
        index_companies = parse_index_page(index_html)

        # Обработка страниц компаний параллельно
        tasks = [parse_company_details(session, comp["url"], usd_rate) for comp in index_companies]
        details_list = await asyncio.gather(*tasks)

        # Объединяем детальную информацию с годовым ростом из индекса
        final_companies = []
        for detail, comp in zip(details_list, index_companies):
            if detail:
                detail["growth"] = comp["growth"]
                final_companies.append(detail)

        print(f"Обработано компаний: {len(final_companies)}")
        save_top_ten(final_companies)


if __name__ == "__main__":
    asyncio.run(main())
    print("Все данные успешно собраны и сохранены")
