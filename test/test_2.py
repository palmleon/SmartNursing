import pytest
import asyncio
import testcontainers.compose
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom.message import Message
import requests

api_id = 11840848
api_hash = "d9386c4f83eb6844dddb1a35243734d3"
session_str = "1BJWap1wBu1X3OAz67m2f0PrKgPaq0s1g8Av_SiGHX42nCbIhJZoJADif7OM2_LRocLT5bYzuL3U0v7MRTo_WRk1v0WdT7g2obWIyLPXC3vgGuYem9hZUDoL_XzTLc-kuswnk_PClEGImI0a6RBgVUGaona3JShn6lLVZzGH4zp4oGJnEmPHNaLqB7zY6P3O_KEZ9k2tOfr1Y4_2qhHoHShbIZEt0ezN3MSw5iPK-oLNS8-wpsOb8JZ0K2iPWgGpLtYkWhxq6ALwk83PpgXeRx_Yfax0GnpSLZgUDwiSmCpfF4f4QdnAXRzuAADTAqe5cXkWC5Td38U08VlG1Rnmq1mpeEPbrJHU="

@pytest.fixture(scope="session")
async def client() -> TelegramClient:
    client = TelegramClient(
        StringSession(session_str), api_id, api_hash,
        sequential_updates=True
    )
    # Connect to the server
    await client.connect()
    # Issue a high level command to start receiving message
    await client.get_me()
    # Fill the entity cache
    await client.get_dialogs()

    yield client

    await client.disconnect()
    await client.disconnected

#def test():
#    with testcontainers.compose.DockerCompose(filepath="../",
#                   compose_file_name=["docker-compose.yml"]) as compose:
#        host = compose.get_service_host("cdrsi", 8080)
#        port = compose.get_service_port("cdrsi", 8080)

        
#        print('host: %s' % host)
#        print('port: %s' % port)

#        host_base = "http://" + host + ":8080/catalog"
#        compose.wait_for(host_base)
        
#        response = requests.get(host_base + "/telegram-user-id-list")

#        assert response.status_code == requests.codes.ok

#        print(response.json())

@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()

@pytest.mark.asyncio
async def test_2(client: TelegramClient):
    with testcontainers.compose.DockerCompose(filepath="../",
                   compose_file_name=["docker-compose.yml"]) as compose:
        async with client.conversation("@SmartClinicProjectBot", timeout=5) as conv:
            # User > /start
            await conv.send_message("/start")
            resp: Message = await conv.get_response()
            # Make assertions
            print(resp.raw_text)
  
    


