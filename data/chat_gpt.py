import asyncio
from pprint import pprint
import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from data.logger import logger
from tenacity import retry, stop_after_attempt, wait_fixed


class AuthOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.request_url = "https://api.openai.com/v1/chat/completions"
        self.request_header = {"Authorization": f"Bearer {api_key}"}

    @retry(stop=stop_after_attempt(3))
    async def process_question(self, question):
        query = question
        data = {
            'model': 'gpt-3.5-turbo-16k',
            'messages': [
                {'role': 'user',
                 'content': query}
            ]
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=self.request_url, headers=self.request_header, json=data,
                                        ssl=False) as response:

                    try:
                        resp = await asyncio.wait_for(response.json(), timeout=50)
                    except asyncio.TimeoutError:
                        raise Exception('Результат не получен за 50 секунд')

            if resp:
                if resp.get('error') and resp['error']['code'] == 503:
                    raise Exception('Ошибка запроса. Сервис недоступен.')
                elif resp.get('choices') and resp['choices'][0]['message']['content']:
                    return ''.join(resp['choices'][0]['message']['content'])
        except Exception as e:
            logger.error(f"Request failed {e}")
            raise

    async def check_work(self):
        print(self.api_key)
        query = 'Тестовое сообщение'
        data = {
            'model': 'gpt-3.5-turbo-16k',
            'messages': [
                {'role': 'user', 'content': query}
            ]
        }

        retries = 3
        retry_timeout = aiohttp.ClientTimeout(total=20)

        @retry(stop=stop_after_attempt(retries), wait=wait_fixed(retry_timeout.total))
        async def send_request():
            async with aiohttp.ClientSession(timeout=retry_timeout) as session:
                async with session.post(url=self.request_url, headers=self.request_header, json=data,
                                        ssl=False) as response:
                    resp = await response.json()
                    if resp:
                        pprint(resp)
                        if resp['choices'][0]['message']['content']:
                            return 'Аккаунт доступен.'
                        else:
                            raise Exception('Аккаунт не доступен.')
                    else:
                        raise Exception('Ошибка получения ответа.')

        try:
            res = await send_request()
            if res == 'Аккаунт доступен.':
                return res
            else:
                return 'Аккаунт не доступен.'
        except Exception as e:
            print(f"Request failed {e}")
            return 'Аккаунт не доступен.'