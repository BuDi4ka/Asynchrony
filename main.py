import aiohttp
import asyncio
import argparse
from datetime import datetime, timedelta

API_URL = 'https://api.privatbank.ua/p24api/exchange_rates?date='
DATE_NOW = datetime.now().date()

async def fetch_rate(session, date):
    url = API_URL + date.strftime('%d.%m.%Y')
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Failed to fetch data for {date}: Status code {response.status}")
                return None
    except aiohttp.ClientError as e:
        print(f"Client error: {e}")
        return None

async def main(days):
    if days > 10:
        return "You can request rates for up to 10 days only."

    date = DATE_NOW - timedelta(days=days)
    async with aiohttp.ClientSession() as session:
        results = []
        while date <= DATE_NOW:
            data = await fetch_rate(session, date)
            if data:
                usd = next((rate for rate in data['exchangeRate'] if rate['currency'] == 'USD'), None)
                eur = next((rate for rate in data['exchangeRate'] if rate['currency'] == 'EUR'), None)
                result = {}
                if usd:
                    result['USD'] = {
                        'purchase': usd['purchaseRate'],
                        'sale': usd['saleRate']
                    }
                if eur:
                    result['EUR'] = {
                        'purchase': eur['purchaseRate'],
                        'sale': eur['saleRate']
                    }
                if result:
                    results.append(f"{date.strftime('%d.%m.%Y')}:\n{result}")
            date += timedelta(days=1)

        print("\n".join(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enter days to get currency rates for the last days")
    parser.add_argument('days', type=int, help="Days for currency rates")
    args = parser.parse_args()
    asyncio.run(main(args.days))

