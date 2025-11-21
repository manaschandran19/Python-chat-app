#!/usr/bin/env python3
"""Simple WebSocket smoke test: open two clients, exchange messages, verify broadcast."""
import asyncio
import time
import websockets

HOST = "127.0.0.1"
PORT = 8000

async def run_smoke():
    user1 = "alice"
    user2 = "bob"
    uri1 = f"ws://{HOST}:{PORT}/ws/{user1}"
    uri2 = f"ws://{HOST}:{PORT}/ws/{user2}"

    print("Connecting both clients...")
    origin = f"http://{HOST}:8000"
    ws1 = await websockets.connect(uri1, origin=origin)
    ws2 = await websockets.connect(uri2, origin=origin)

    try:
        # send private message from alice to bob
        print("alice -> bob (private)")
        await ws1.send('{"to": "bob", "message": "hello bob"}')
        msg = await asyncio.wait_for(ws2.recv(), timeout=3)
        print("bob received:", msg)

        # send private message from bob to alice
        print("bob -> alice (private)")
        await ws2.send('{"to": "alice", "message": "hi alice"}')
        msg = await asyncio.wait_for(ws1.recv(), timeout=3)
        print("alice received:", msg)

        # broadcast from alice
        print("alice -> all (broadcast)")
        await ws1.send('{"message": "hello everyone"}')
        # both should receive the broadcast (we'll read one)
        msg = await asyncio.wait_for(ws2.recv(), timeout=3)
        print("bob received broadcast:", msg)

        print("Smoke test succeeded")
    except Exception as e:
        print("Smoke test failed:", e)
        raise
    finally:
        await ws1.close()
        await ws2.close()

if __name__ == "__main__":
    asyncio.run(run_smoke())
