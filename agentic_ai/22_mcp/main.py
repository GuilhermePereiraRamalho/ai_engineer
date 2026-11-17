from mcp.server.mcpserver import MCPServer
import asyncio
import sys
from pathlib import Path
from mcp import Client, StdioServerParameters

servidor = MCPServer("Escola fictícia")


@servidor.tool()
def matricula(codigo: str) -> str:
    """Consulta uma matrícula fictícia."""
    return {"M001": "ativa", "M002": "cancelada"}.get(codigo, "não encontrada")


@servidor.resource("escola://politicas/cancelamento")
def politica() -> str:
    return (
        "Cancelamento em até 7 dias permite análise. Reembolsos exigem aprovação "
        "humana."
    )


async def demonstrar():
    parametros = StdioServerParameters(
        command=sys.executable, args=[str(Path(__file__).resolve()), "--servidor"]
    )
    async with Client(parametros) as cliente:
        ferramentas = await cliente.list_tools()
        print("Ferramentas:", ferramentas)
        print("Recursos:", await cliente.list_resources())
        resultado = await cliente.call_tool("matricula", {"codigo": "M001"})
        print("Consulta:", resultado)
        print(
            "Política:", await cliente.read_resource("escola://politicas/cancelamento")
        )


if __name__ == "__main__":
    if "--servidor" in sys.argv:
        servidor.run(transport="stdio")
    else:
        asyncio.run(demonstrar())
