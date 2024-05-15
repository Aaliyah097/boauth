import json
from io import BytesIO
import aiofiles
from src.cache import RedisConnector
from src import api_requests
from src import utils


STARS_KEY = 'stars'
PHOTO_KEY = 'link'
RESULT_STAR_KEY = 'star_%s_%s'
RESULT_FRIEND_KEY = "friend_%s"


async def preload_stars():
    stars = await api_requests.get_stars_accounts()
    async with RedisConnector() as r:
        await r.set(STARS_KEY, json.dumps({STARS_KEY: [s.serialize() for s in stars]}))


async def preload_stars_photos():
    stars = await api_requests.get_stars_accounts()
    async with RedisConnector() as r:
        for star in stars:
            if not await r.get(star.photo):
                photo = await utils.download_photo(star.photo)
                await r.set(star.photo, json.dumps({PHOTO_KEY: photo.decode('utf-8')}))


async def preload_stars_k_results():
    stars = await api_requests.get_stars_accounts()
    async with RedisConnector() as r:
        for star in stars:
            for k in range(10, 100):
                if not await r.get(RESULT_STAR_KEY % (str(k), str(star.id_tg))):
                    picture = await utils.make_star_k_picture(k, star)
                    picture.seek(0)
                    await r.set(RESULT_STAR_KEY % (str(k), str(star.id_tg)), picture.getvalue())


async def preload_friends_k_results():
    async with RedisConnector() as r:
        for k in range(10, 100):
            if not await r.get(RESULT_FRIEND_KEY % str(k)):
                picture = await utils.make_friend_k_picture(k)
                picture.seek(0)
                await r.set(RESULT_FRIEND_KEY % str(k), picture.getvalue())
