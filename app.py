#!/usr/bin/env python3

import asyncio
import ujson
import aioredis
from aiohttp import web


async def on_config_update(app, key):
    try:
        con = await aioredis.create_redis(('localhost', 6379))
        val: str = await con.get(key)
        if val:
            app['c1_config'][key] = val
    except asyncio.CancelledError:
        print('cancelled')
    except Exception as e:
        print(e)
    finally:
        await con.quit()


async def listen_to_redis(app):
    try:
        con = await aioredis.create_redis(('localhost', 6379))
        ch, *_ = await con.subscribe('news')
        async for key in ch.iter(encoding='utf-8'):
            await on_config_update(app, key)
    except asyncio.CancelledError:
        print('cancelled')
    finally:
        await con.unsubscribe(ch.name)
        await con.quit()


async def start_background_tasks(app: web.Application):
    app['redis_listener'] = asyncio.create_task(listen_to_redis(app))
    

async def cleanup_background_tasks(app):
    app['redis_listener'].cancel()
    await app['redis_listener']


async def get_config(request):
    return web.Response(text=ujson.dumps(request.app['c1_config']))


async def app():
    app = web.Application()
    app['c1_config'] = {'api_security': {'active': True}}
    app.router.add_route("GET", "/config", get_config)
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    return app
    
if __name__ == "__main__":
    web.run_app(app())
    
