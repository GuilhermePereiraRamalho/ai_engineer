from pathlib import Path
from dotenv import dotenv_values
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import yaml

RAIZ = Path(__file__).resolve().parents[1]


def conectar():
    ambiente = dotenv_values(RAIZ / ".env")
    perfis = yaml.safe_load((RAIZ / "config/models.yaml").read_text(encoding="utf-8"))
    perfil = perfis[ambiente.get("PERFIL_MODELO", "fast")]
    return ChatOpenAI(
        api_key=ambiente.get("OPENAI_API_KEY", ""),
        model=perfil["model"],
        reasoning={"effort": perfil["reasoning_effort"]},
        max_tokens=1200,
        store=False,
        use_responses_api=True,
        timeout=30,
        max_retries=0,
    )


def consultar_matricula(matricula: str) -> dict:
    """Consulta o status de uma matrícula pelo código, como M001."""
    resultado = {
        "status": {"M001": "ativa", "M002": "cancelada"}.get(
            matricula, "não encontrada"
        )
    }
    print(
        "Ferramenta: consultar_matricula | Matrícula:",
        matricula,
        "| Resultado:",
        resultado,
    )
    return resultado


def consultar_curso(curso: str) -> dict:
    """Consulta a duração de um curso pelo nome, como Python ou Dados."""
    resultado = {"duracao_horas": "20"}
    print("Ferramenta: consultar_curso | Curso:", curso, "| Resultado:", resultado)
    return resultado


def main():
    pergunta = "Quanto dura o curso de Python e qual é a situação da matrícula M001?"
    agente = create_agent(
        model=conectar(), tools=[consultar_matricula, consultar_curso]
    )
    resultado = agente.invoke(
        {"messages": [{"role": "user", "content": pergunta}]},
        config={"recursion_limit": 10},
    )
    print("Resposta:", resultado["messages"][-1].text)


if __name__ == "__main__":
    main()
