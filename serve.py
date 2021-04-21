#!/usr/bin/env python3
import logging
import asyncio
import sys
from aiohttp import web

@web.middleware
async def default_middleware(request, handler):
    if request.method == 'POST':
        return web.Response(text='{}')
    try:
        response = await handler(request)
        if request.path.startswith('/database/') or request.path.startswith('/api/'):
            response.content_type = 'application/json'
        if response.status != 404 and response.status != 403:
            return response
    except web.HTTPException as ex:
        if ex.status != 404 and ex.status != 403:
            raise
    return web.FileResponse('./index.html')

async def stream_data(request):
    resp = web.StreamResponse()
    resp.content_type = 'text/event-stream'
    resp.charset = 'utf-8'

    writer = await resp.prepare(request)

    with open('./events/streamData', 'rb') as event:
        await resp.write(event.read())
        await resp.write(b'\n')
        await writer.drain()

    await asyncio.sleep(30)

    await resp.write_eof()

    return resp

app = web.Application(middlewares=[default_middleware])

app.add_routes([web.get('/events/streamData', stream_data), web.static('/', '.')])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    web.run_app(app)
