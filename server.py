import asyncio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

async def index(request):
    content = open("index.html", "r").read()
    return web.Response(content_type="text/html", text=content)

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pc.addTrack(MediaPlayer("/dev/video0"))
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.json_response({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

async def on_shutdown(app):
    for ws in app["websockets"]:
        await ws.close(code=1001, reason="Server shutdown")

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    request.app["websockets"].add(ws)
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            await ws.send_str(msg.data)
        elif msg.type == web.WSMsgType.ERROR:
            break
    request.app["websockets"].remove(ws)
    return ws

async def main():
    app = web.Application()
    app["websockets"] = set()
    app.router.add_get("/", index)
    app.router.add_post("/offer", offer)
    app.router.add_get("/ws", websocket_handler)
    app.on_shutdown.append(on_shutdown)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Server started at http://localhost:8080")
    await asyncio.sleep(100*3600)

if __name__ == "__main__":
    asyncio.run(main())
