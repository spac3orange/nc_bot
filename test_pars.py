import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon import functions
from environs import Env, load_dotenv
from typing import List
import openpyxl
import json
env = Env()
env.read_env(path="data/.env", recurse=False)


async def fetch_channel_info(client, channel_url):
    try:
        channel = await client.get_entity(channel_url)
        full_channel = await client(GetFullChannelRequest(channel))
        # Проверяем, есть ли linked chat (это может быть supergroup, привязанная к каналу)
        has_linked_chat = hasattr(full_channel.full_chat, 'linked_chat_id') and full_channel.full_chat.linked_chat_id is not None
        print(f'l chat: {has_linked_chat}')
        return has_linked_chat
    except Exception as e:
        print(f"Error fetching {channel_url}: {e}")
        return False


async def fetch_chann_recs(client, channel_url: str):
    try:
        channel = await client.get_entity(channel_url)
        result = await client(functions.channels.GetChannelRecommendationsRequest(
            channel=channel
        ))
        print(result.stringify())
        print(type(result))
        return result
    except Exception as e:
        print(f"Error fetching {channel_url} recomendations: {e}")
        return False


async def process_get_recs(session_files: List, channel_urls: List):
    seen_ids = set()
    all_channels_info = []
    for session_file in session_files:
        client = TelegramClient(session_file, api_id, api_hash)
        await client.connect()
        for url in channel_urls:
            await asyncio.sleep(5)
            recs = await fetch_chann_recs(client, url)
            if recs and hasattr(recs, 'chats'):
                channels_info = []
                for chat in recs.chats:
                    if chat.id not in seen_ids:  # Проверка на уникальность ID
                        seen_ids.add(chat.id)
                        chat_info = {
                            'id': chat.id,
                            'username': getattr(chat, 'username', None),
                            'title': getattr(chat, 'title', None),
                            'participants_count': getattr(chat, 'participants_count', None),
                            'has_link': getattr(chat, 'has_link', None)
                        }
                        channels_info.append(chat_info)
                        all_channels_info.append(chat_info)

                # Определение имени файла на основе URL или ID канала
                channel_username = url.split('/')[-1] if '/' in url else url
                file_name = f"{channel_username}_recs.json"

                # Сохранение данных в JSON файл
                with open(f'recs/{file_name}', 'w', encoding='utf-8') as json_file:
                    json.dump(channels_info, json_file, ensure_ascii=False, indent=4)
                print(f'recs saved to {file_name}')
        await client.disconnect()

        # Спрашиваем название файла для сохранения таблицы
        # Создание Excel файла с данными
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = table_name

        # Заголовки столбцов
        columns = ["ID", "username", "title", "participants Count", "has_link"]
        sheet.append(columns)

        # Добавление данных в таблицу
        for channel in all_channels_info:
            row = [channel['id'], channel['username'], channel['title'], channel['participants_count'], channel['has_link']]
            sheet.append(row)

        # Сохраняем таблицу
        workbook.save(f"{table_name}.xlsx")
        print(f"Все данные сохранены в {table_name}.xlsx")
        break

async def process_channels(session_files, channel_urls):
    with open('results.txt', 'w') as file:
        for session_file in session_files:
            client = TelegramClient(session_file, api_id, api_hash)
            await client.connect()
            print(client.is_connected())
            request_count = 0
            for url in channel_urls:
                if request_count >= 200:  # Предотвращаем ошибку из-за ограничения в 200 запросов
                    break
                has_link = await fetch_channel_info(client, url)
                file.write(f"{url},{has_link}\n")
                request_count += 1
                await asyncio.sleep(1)
            await client.disconnect()
            if request_count < len(channel_urls):  # Перейдем к следующей сессии, если текущая достигла лимита
                continue
            else:
                break


# Список URL каналов и файлов сессий
channel_urls = [
    "https://t.me/prodavaydorogo",
    "https://t.me/imaeva_psy",
    "https://t.me/nastya_lubarskaya",
    "https://t.me/marketing_lukovkin",
    "https://t.me/anna_elkina",
    "https://t.me/timkadyrovvv",
    "https://t.me/JLSystemBigMoney",
    "https://t.me/SistemaMari",
    "https://t.me/fateev_blog",
    "https://t.me/kkerpowerr",
    "https://t.me/bytashko",
    "https://t.me/smartpromotion_sp",
    "https://t.me/nastyaforbes7",
    "https://t.me/antontum1",
    "https://t.me/av_sibirtseva",
    "https://t.me/s_voskoboynikov",
    "https://t.me/MilaForYou",
    "https://t.me/elyaagalieva",
    "https://t.me/osinashtab",
    "https://t.me/belaya_svet",
    "https://t.me/griban_d",
    "https://t.me/wowfairysmm",
    "https://t.me/le_kott",
    "https://t.me/prihodko_yuliya",
    "https://t.me/imkatiyaofficial",
    "https://t.me/elizaveta_avanesovaa",
    "https://t.me/nankina_blog",
    "https://t.me/noheadmarketer",
    "https://t.me/ekaterina_latyshevaa",
    "https://t.me/vvoronke",
    "https://t.me/kosenkoeffect",
    "https://t.me/ushakovaonline",
    "https://t.me/ignat_marketing",
    "https://t.me/morozmillion",
    "https://t.me/guzelsafinaa",
    "https://t.me/housesmm",
    "https://t.me/udodmaksim",
    "https://t.me/Mikhailova_OV",
    "https://t.me/pisarevblog",
    "https://t.me/juliessosays",
    "https://t.me/ab_chat",
    "https://t.me/anyaalbertovnaa",
    "https://t.me/tg_rylit",
    "https://t.me/nastyathecoach",
    "https://t.me/ayaz_protiv",
    "https://t.me/polyaprodazhi",
    "https://t.me/July_Teta",
    "https://t.me/karinapronastavnichestvo",
    "https://t.me/Nadezhdapronas",
    "https://t.me/tanyapromarketing",
    "https://t.me/liya_story",
    "https://t.me/ContentbyN",
    "https://t.me/anastyv1",
    "https://t.me/matvienkoeffect",
    "https://t.me/realitiprolubov",
    "https://t.me/pavel_mind",
    "https://t.me/cumom_irina",
    "https://t.me/MDmitryGolovanich",
    "https://t.me/dubenskaia",
    "https://t.me/yakuban",
    "https://t.me/valeriavgp",
    "https://t.me/tanmil_iya",
    "https://t.me/dashanofilter",
    "https://t.me/pomogatiprodavat",
    "https://t.me/klienti_vtg",
    "https://t.me/nastya_prodai",
    "https://t.me/gereeva_reality",
    "https://t.me/yana_offeristka",
    "https://t.me/alfiyagazizovaa",
    "https://t.me/alexandraminakova",
    "https://t.me/adelprolubov",
    "https://t.me/alenagereeva",
    "https://t.me/bymatvienko",
    "https://t.me/pavelshiriaev",
    "https://t.me/berezanskaya_oksana",
    "https://t.me/sbitneva_nastia",
    "https://t.me/vasyutta",
    "https://t.me/infohilights",
    "https://t.me/tm_producer",
    "https://t.me/denamir1",
    "https://t.me/lazyproducer",
    "https://t.me/gordovbiz",
    "https://t.me/ElizavetaGolovinskaya",
    "https://t.me/antonov_launch",
    "https://t.me/timeartem",
    "https://t.me/billions_mate",
    "https://t.me/epsteinblog",
    "https://t.me/engageforsales",
    "https://t.me/glavsasha",
    "https://t.me/turchinovich",
    "https://t.me/grebenukm",
    "https://t.me/dimgavrilov_blog",
    "https://t.me/irina_trafik",
    "https://t.me/camilla_business",
    "https://t.me/vgavrilov_online",
    "https://t.me/dymshakovmethod",
    "https://t.me/daria_kicheva",
    "https://t.me/infogleb",
    "https://t.me/nastavnik_scvortcov",
    "https://t.me/bymorozov1",
    "https://t.me/MaximKruchkov",
    "https://t.me/mari_zapuski",
    "https://t.me/academyzapuskov",
    "https://t.me/egorpyrikov",
    "https://t.me/DmitryLedovskih",
    "https://t.me/alenatsel_proprodazhi",
    "https://t.me/infobiz_roma",
    "https://t.me/reklamaa_v_telegram",
    "https://t.me/expertpromotion",
    "https://t.me/TorbosovLife",
    "https://t.me/zagorodnikovnews",
    "https://t.me/perkulimov",
    "https://t.me/volkovsky_zero",
    "https://t.me/arikovapro",
    "https://t.me/artemamazur",
    "https://t.me/mitroshinablogging",
    "https://t.me/milasya_ts",
    "https://t.me/wolfmarketer",
    "https://t.me/frolova_i_experty",
    "https://t.me/mmargosavchuk",
    "https://t.me/partners_zapuski_muraveva",
    "https://t.me/mari_vse",
    "https://t.me/davaizapuskai",
    "https://t.me/durovs_mate",
    "https://t.me/infomem",
    "https://t.me/mullanur_target",
    "https://t.me/ainfobis",
    "https://t.me/anika_tg",
    "https://t.me/fogel_biz",
    "https://t.me/Tanya_rylit",
    "https://t.me/fishkiprodaj",
    "https://t.me/elenasolzhnews",
    "https://t.me/dma_pro",
    "https://t.me/mlnza3dny",
    "https://t.me/Natali_all2",
    "https://t.me/andreimizev",
    "https://t.me/targetveka",
    "https://t.me/drumyanzev",
    "https://t.me/tyzhexpert",
    "https://t.me/InfobusinessMeat",
    "https://t.me/CashChest",
    "https://t.me/petrochenkow",
    "https://t.me/workforwriters",
    "https://t.me/molyanov",
    "https://t.me/firstwhitechannel",
    "https://t.me/tinder_tm",
    "https://t.me/surgaygraf",
    "https://t.me/ed_growth",
    "https://t.me/eji4kaa",
    "https://t.me/puzzlebrains",
    "https://t.me/opershtabtg",
    "https://t.me/neudobnyezhiba",
    "https://t.me/ZhukovskyPro",
    "https://t.me/bzdynko",
    "https://t.me/dimamarketing",
    "https://t.me/kaifsurfing",
    "https://t.me/content_for_sales",
    "https://t.me/smmolga",
    "https://t.me/masha_pro_marketing",
    "https://t.me/ilyana_levina",
    "https://t.me/easybillions",
    "https://t.me/ugumarketing",
    "https://t.me/yellowsme",
    "https://t.me/funnel_1",
    "https://t.me/TGDronova",
    "https://t.me/gabany",
    "https://t.me/spy_marketing",
    "https://t.me/profkopiraiter",
    "https://t.me/digital_storage",
    "https://t.me/ivanischev_producer",
    "https://t.me/alimov_marketing",
    "https://t.me/getcourse_official",
    "https://t.me/iliaibd",
    "https://t.me/lovemoneyexpertise",
    "https://t.me/zverinfo",
    "https://t.me/zolotov_sprints",
    "https://t.me/potok_ads",
    "https://t.me/dsadykov_ru",
    "https://t.me/Infobiznow",
    "https://t.me/artemsenatorov",
    "https://t.me/cilinskey_notes",
    "https://t.me/bolshie_4eki",
    "https://t.me/dashkiev",
    "https://t.me/dnative",
    "https://t.me/sdelaem_agency",
    "https://t.me/zapusk_eksperta",
    "https://t.me/Semyannikov",
    "https://t.me/trandford",
    "https://t.me/komyag",
    "https://t.me/evgenia_li_kanal",
    "https://t.me/iramotivation",
    "https://t.me/voinpr",
    "https://t.me/maria_volshebnica1",
    "https://t.me/likeisstrong",
    "https://t.me/dmdobro",
    "https://t.me/aschepkovpro",
    "https://t.me/likecentre_live"
]

session_files = ['data/telethon_sessions/+7 993 911 5398.session']  # Имена файлов сессий
#'data/telethon_sessions/+7 993 624 1435.session',
grecs_urls = [
        "https://t.me/morozmillion",
    "https://t.me/guzelsafinaa",
    "https://t.me/housesmm",
    "https://t.me/udodmaksim",
    "https://t.me/Mikhailova_OV",
    "https://t.me/pisarevblog",
    "https://t.me/juliessosays",
    "https://t.me/ab_chat",
    "https://t.me/anyaalbertovnaa",
    "https://t.me/tg_rylit",
    "https://t.me/nastyathecoach",
    "https://t.me/ayaz_protiv",
    "https://t.me/polyaprodazhi",
    "https://t.me/July_Teta",
    "https://t.me/karinapronastavnichestvo",
    "https://t.me/Nadezhdapronas",
    "https://t.me/tanyapromarketing",
    "https://t.me/liya_story",
    "https://t.me/ContentbyN",
    "https://t.me/anastyv1",
    "https://t.me/matvienkoeffect",
    "https://t.me/realitiprolubov",
    "https://t.me/pavel_mind",
    "https://t.me/cumom_irina",
    "https://t.me/MDmitryGolovanich",
    "https://t.me/dubenskaia",
    "https://t.me/yakuban",
    "https://t.me/valeriavgp",
    "https://t.me/tanmil_iya",
    "https://t.me/dashanofilter",
    "https://t.me/pomogatiprodavat",
    "https://t.me/klienti_vtg",
    "https://t.me/nastya_prodai",
    "https://t.me/gereeva_reality",
    "https://t.me/yana_offeristka",
    "https://t.me/alfiyagazizovaa",
    "https://t.me/alexandraminakova",
    "https://t.me/adelprolubov",
    "https://t.me/alenagereeva",
    "https://t.me/bymatvienko",
    "https://t.me/pavelshiriaev",
    "https://t.me/berezanskaya_oksana",
    "https://t.me/sbitneva_nastia",
    "https://t.me/vasyutta",
    "https://t.me/infohilights",
    "https://t.me/tm_producer",
    "https://t.me/denamir1",
    "https://t.me/lazyproducer",
    "https://t.me/gordovbiz",
    "https://t.me/ElizavetaGolovinskaya",
    "https://t.me/antonov_launch",
    "https://t.me/timeartem",
    "https://t.me/billions_mate",
    "https://t.me/epsteinblog",
    "https://t.me/engageforsales",
    "https://t.me/glavsasha",
    "https://t.me/turchinovich",
    "https://t.me/grebenukm",
    "https://t.me/dimgavrilov_blog",
    "https://t.me/irina_trafik",
    "https://t.me/camilla_business",
    "https://t.me/vgavrilov_online",
    "https://t.me/dymshakovmethod",
    "https://t.me/daria_kicheva",
    "https://t.me/infogleb",
    "https://t.me/nastavnik_scvortcov",
    "https://t.me/bymorozov1",
    "https://t.me/MaximKruchkov",
    "https://t.me/mari_zapuski",
    "https://t.me/academyzapuskov",
    "https://t.me/egorpyrikov",
    "https://t.me/DmitryLedovskih",
    "https://t.me/alenatsel_proprodazhi",
    "https://t.me/infobiz_roma",
    "https://t.me/reklamaa_v_telegram",
    "https://t.me/expertpromotion",
    "https://t.me/TorbosovLife",
    "https://t.me/zagorodnikovnews",
    "https://t.me/perkulimov",
    "https://t.me/volkovsky_zero",
    "https://t.me/arikovapro",
    "https://t.me/artemamazur",
    "https://t.me/mitroshinablogging",
    "https://t.me/milasya_ts",
    "https://t.me/wolfmarketer",
    "https://t.me/frolova_i_experty",
    "https://t.me/mmargosavchuk",
    "https://t.me/partners_zapuski_muraveva",
    "https://t.me/mari_vse",
    "https://t.me/davaizapuskai",
    "https://t.me/durovs_mate",
    "https://t.me/infomem",
    "https://t.me/mullanur_target",
    "https://t.me/ainfobis",
    "https://t.me/anika_tg",
    "https://t.me/fogel_biz",
    "https://t.me/Tanya_rylit",
    "https://t.me/fishkiprodaj",
    "https://t.me/elenasolzhnews",
    "https://t.me/dma_pro",
    "https://t.me/mlnza3dny",
]

# Не забудьте заменить `api_id` и `api_hash` на актуальные значения
api_id = env('API_ID')
api_hash = env('API_HASH')

# Запуск асинхронной обработки
# asyncio.run(process_channels(session_files, channel_urls))
table_name = input("Введите название для таблицы Excel: ")
asyncio.run(process_get_recs(session_files, grecs_urls))
