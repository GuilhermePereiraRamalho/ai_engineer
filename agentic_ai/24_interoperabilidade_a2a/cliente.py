import asyncio
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types import Message, Part, Role, SendMessageRequest


async def main():
    async with httpx.AsyncClient(timeout=10, trust_env=False) as http:
        cartao = await A2ACardResolver(http, "http://127.0.0.1:8024").get_agent_card()
        print("Agente encontrado:", cartao.name)
        print("Capacidades:", [skill.name for skill in cartao.skills])
        fabrica = ClientFactory(ClientConfig(httpx_client=http, streaming=False))
        async with fabrica.create(cartao) as cliente:
            pedido = "Qual é a política de reembolso da escola?"
            print("Pedido enviado:", pedido)
            mensagem = Message(
                message_id=str(uuid4()), role=Role.ROLE_USER, parts=[Part(text=pedido)]
            )
            async for evento in cliente.send_message(
                SendMessageRequest(message=mensagem)
            ):
                if evento.HasField("message"):
                    print(
                        "Resposta:",
                        "\n".join(parte.text for parte in evento.message.parts),
                    )


if __name__ == "__main__":
    asyncio.run(main())
