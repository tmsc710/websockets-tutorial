#!/usr/bin/env python

import asyncio
import json
import logging

import websockets

from connect4 import Connect4, PLAYER1, PLAYER2

logging.basicConfig(format="%(message)s", level=logging.DEBUG)


# async def handler(websocket):
#     while True:
#         try:
#             message = await websocket.recv()
#         except websockets.ConnectionClosedOK:
#             break
#         print(message)
# EQUIVALENT TO:
# async def handler(websocket):
#     async for message in websocket:
#         print(message)


async def handler(websocket):
    # Initialize a Connect Four game.
    game = Connect4()

    async for message in websocket:
        # Parse a "play" event from the UI.
        event = json.loads(message)
        assert event["type"] == "play"
        column = event["column"]

        try:
            # Players take alternate turns, using the same browser.
            player = PLAYER1 if game.last_player == PLAYER2 else PLAYER2
            # Play the move.
            row_landed = game.play(player, column)
        except RuntimeError as exc:
            # Send an "error" event if the move was illegal.
            event = {"type": "error", "message": str(exc)}
            await websocket.send(json.dumps(event))
        else:
            # Send a "play" event to update the UI.
            event = {"type": "play", "player": game.last_player, "column": column, "row": row_landed}
            await websocket.send(json.dumps(event))

            # If move is winning, send a "win" event.
            if game.winner:
                event = {"type": "win", "player": game.winner}
                await websocket.send(json.dumps(event))


async def main():
    async with websockets.serve(handler, "", 8008):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
