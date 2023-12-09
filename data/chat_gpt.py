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
        self.username = 'customer-derivu'
        self.password = 'dc09yqux40tn81pt17qmcU'
        self.proxy = f"http://{self.username}:{self.password}@cz-pr.oxylabs.io:18001"

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
                                        ssl=False, proxy=self.proxy) as response:

                    try:
                        resp = await asyncio.wait_for(response.json(), timeout=30)
                    except asyncio.TimeoutError:
                        raise Exception('Результат не получен за 30 секунд')

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
        query = 'Привет! Как дела?'
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
            try:
                async with aiohttp.ClientSession(timeout=retry_timeout, trust_env=True) as session:
                    async with session.post(url=self.request_url, headers=self.request_header, json=data,
                                            proxy=self.proxy, ssl=False) as response:
                        if response:
                            print(response.status)
                            resp = await response.json()
                            if resp:
                                pprint(resp)
                                if resp['choices'][0]['message']['content']:
                                    return 'Аккаунт доступен.'
                                else:
                                    raise Exception('Аккаунт не доступен.')
                            else:
                                raise Exception('Ошибка получения ответа.')
                        else:
                            logger.error('no response')
            except Exception as e:
                logger.error(e)
                raise Exception(f"Request failed {e}")

        try:
            res = await send_request()
            return res
        except Exception as e:
            print(f"Request failed {e}")
            return 'Аккаунт не доступен.'