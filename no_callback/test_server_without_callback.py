
async def test_websocket(websocket_session):

    async with websocket_session() as ws:
        await ws.send_str('keep')

        assert await ws.receive_str() == 'keep/answer'

        await ws.send_str('close')

        assert await ws.receive_str() == 'closing'

