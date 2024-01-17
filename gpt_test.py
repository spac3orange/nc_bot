import aiohttp


class AuthOpenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.request_url = "https://api.openai.com/v1/chat/completions"
        self.request_header = {"Authorization": f"Bearer {api_key}"}

    async def process_question(self, promt, question):
        query = question
        data = {
            'model': 'gpt-3.5-turbo-16k',
            'messages': [
                {'role': 'system', 'content': promt},
                {'role': 'user', 'content': query}
            ]
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=self.request_url, headers=self.request_header, json=data, ssl=False) as response:
                    resp = await response.json()
        except Exception as e:
            print(f"Request failed {e}")
        return ''.join(resp['choices'][0]['message']['content'])

    async def check_work(self):
        query = 'Тестовое сообщение'
        data = {
            'model': 'gpt-3.5-turbo-16k',
            'messages': [
                {'role': 'user', 'content': query}
            ]
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=self.request_url, headers=self.request_header, json=data,
                                        ssl=False) as response:
                    resp = await response.json()
        except Exception as e:
            print(f"Request failed {e}")
        return ''.join(resp['choices'][0]['message']['content'])

