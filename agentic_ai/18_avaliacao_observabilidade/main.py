import json
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI, OpenAIError
import yaml

RAIZ = Path(__file__).resolve().parents[1]
INSTRUCOES = (
    "Responda em português, de forma breve, usando apenas este catálogo fictício: "
    "Python tem 20 horas; Dados tem 30 horas. Preços não informados. "
    "Admita informações ausentes e peça esclarecimento quando necessário."
)
CASOS = [
    ("duracao", "Quanto dura o curso de Python?", "Informar 20 horas."),
    ("preco", "Qual é o preço de Python?", "Reconhecer que o preço não foi informado."),
    (
        "ambiguo",
        "Quanto dura o curso?",
        "Perguntar qual curso, ou apresentar as duas durações com seus nomes.",
    ),
]


def conectar():
    ambiente = dotenv_values(RAIZ / ".env")
    perfis = yaml.safe_load((RAIZ / "config/models.yaml").read_text(encoding="utf-8"))
    perfil = perfis[ambiente.get("PERFIL_MODELO", "fast")]
    cliente = OpenAI(
        api_key=ambiente.get("OPENAI_API_KEY", ""), timeout=30, max_retries=0
    )
    parametros = {
        "model": perfil["model"],
        "reasoning": {"effort": perfil["reasoning_effort"]},
        "max_output_tokens": 1200,
        "store": False,
    }
    return cliente, parametros


def main():
    cliente, parametros = conectar()
    caminho = Path(__file__).parent / "saida" / "eventos.jsonl"
    caminho.parent.mkdir(exist_ok=True)
    execucao = datetime.now(timezone.utc).isoformat()

    for caso, pergunta, criterio in CASOS:
        evento = {
            "execucao": execucao,
            "caso": caso,
            "parametros": parametros,
            "instrucoes": INSTRUCOES,
            "pergunta": pergunta,
            "criterio": criterio,
            "resposta": None,
            "erro": None,
            "tokens_entrada": None,
            "tokens_saida": None,
        }
        inicio = time.perf_counter()
        try:
            resposta = cliente.responses.create(
                **parametros, instructions=INSTRUCOES, input=pergunta
            )
            evento["resposta"] = resposta.output_text
            evento["tokens_entrada"] = resposta.usage.input_tokens
            evento["tokens_saida"] = resposta.usage.output_tokens
        except OpenAIError as erro:
            evento["erro"] = type(erro).__name__
        evento["segundos"] = round(time.perf_counter() - inicio, 3)

        with caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(evento, ensure_ascii=False) + "\n")
        print("\nCaso:", caso, "| Pergunta:", pergunta)
        print("Resposta:", evento["resposta"])
        print("Segundos:", evento["segundos"])
        print(
            "Tokens entrada/saída:",
            evento["tokens_entrada"],
            "/",
            evento["tokens_saida"],
        )
        print("Erro:", evento["erro"])
        print("Critério para revisão humana:", criterio)

    print("\nEventos salvos em:", caminho)


if __name__ == "__main__":
    main()
