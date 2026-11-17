from uuid import uuid4
import uvicorn
from starlette.applications import Starlette
from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentInterface,
    AgentSkill,
    Message,
    Part,
    Role,
)


class Financeiro(AgentExecutor):
    async def execute(self, context, event_queue):
        print("Pedido recebido:", context.get_user_input())
        texto = (
            "Pedidos em até 7 dias podem ser analisados. Todo reembolso exige aprovação"
            " humana."
        )
        resposta = Message(
            message_id=str(uuid4()), role=Role.ROLE_AGENT, parts=[Part(text=texto)]
        )
        await event_queue.enqueue_event(resposta)

    async def cancel(self, context, event_queue):
        raise NotImplementedError(
            "O exemplo responde imediatamente, sem tarefas canceláveis."
        )


cartao = AgentCard(
    name="Financeiro da escola",
    description="Informa a política fictícia de reembolso.",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    supported_interfaces=[
        AgentInterface(
            url="http://127.0.0.1:8024/",
            protocol_binding="JSONRPC",
            protocol_version="1.0",
        )
    ],
    skills=[
        AgentSkill(
            id="reembolso",
            name="Política de reembolso",
            description="Retorna a política de reembolso.",
            tags=["financeiro"],
        )
    ],
)

handler = DefaultRequestHandler(
    agent_executor=Financeiro(), task_store=InMemoryTaskStore(), agent_card=cartao
)
app = Starlette(
    routes=create_agent_card_routes(cartao) + create_jsonrpc_routes(handler, "/")
)

if __name__ == "__main__":
    print("Servidor financeiro: http://127.0.0.1:8024 — encerre com Ctrl+C.")
    uvicorn.run(app, host="127.0.0.1", port=8024, log_level="warning")
