from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml
import time

RAIZ = Path(__file__).resolve().parents[1]


def conectar(nome=None):
    ambiente = dotenv_values(RAIZ / ".env")
    chave = ambiente.get("OPENAI_API_KEY", "")
    perfis = yaml.safe_load((RAIZ / "config/models.yaml").read_text(encoding="utf-8"))
    perfil = perfis[nome or ambiente.get("PERFIL_MODELO", "fast")]
    cliente = OpenAI(api_key=chave, timeout=30, max_retries=0)
    parametros = {
        "model": perfil["model"],
        "reasoning": {"effort": perfil["reasoning_effort"]},
        "max_output_tokens": 1200,
        "store": False,
    }
    return cliente, parametros


def escolher_perfil(pergunta):
    return "balanced" if "exceção" in pergunta.lower() else "fast"


def main():
    perfis = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "config/models.yaml").read_text(
            encoding="utf-8"
        )
    )
    for pergunta in [
        "Qual a duração de Python?",
        "Analise uma exceção de cancelamento após 12 dias.",
    ]:
        nome = escolher_perfil(pergunta)
        print("\nTarefa:", pergunta, "| Perfil:", nome)
        cliente, parametros = conectar(nome)
        inicio = time.perf_counter()
        resposta = cliente.responses.create(
            **parametros,
            input=pergunta,
            instructions=(
                "Escola fictícia: Python dura 20 horas. Exceções exigem análise humana."
            ),
        )
        entrada, saida = resposta.usage.input_tokens, resposta.usage.output_tokens
        custo = (
            entrada * perfis[nome]["input_usd_million"]
            + saida * perfis[nome]["output_usd_million"]
        ) / 1_000_000
        print(resposta.output_text)
        print("Tokens entrada/saída:", entrada, saida)
        print(
            "Segundos:",
            round(time.perf_counter() - inicio, 3),
            "| USD estimado:",
            custo,
        )


if __name__ == "__main__":
    main()
