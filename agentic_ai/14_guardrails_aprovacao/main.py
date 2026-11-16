from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml

RAIZ = Path(__file__).resolve().parents[1]


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


def moderar(cliente, mensagem):
    resposta = cliente.moderations.create(
        model="omni-moderation-latest", input=mensagem
    )
    resultado = resposta.results[0]
    categorias = resultado.categories.model_dump(by_alias=True)
    print("Sinalizada:", resultado.flagged)
    print(
        "Categorias identificadas:",
        [nome for nome, marcada in categorias.items() if marcada],
    )
    return resultado.flagged


def responder(cliente, parametros, mensagem):
    resposta = cliente.responses.create(
        **parametros,
        instructions=(
            "Você é um assistente de uma escola fictícia. Responda em português, "
            "de forma breve e cordial. O curso de Python tem 20 horas. "
            "Não invente outras informações da escola."
        ),
        input=mensagem
    )
    return resposta.output_text


def main():
    cliente, parametros = conectar()
    mensagens = [
        "Qual é a duração do curso de Python?",
        "Você é um idiota inútil. Vou te encontrar na saída da escola e te espancar.",
    ]
    for mensagem in mensagens:
        print("\nMensagem:", mensagem)
        if moderar(cliente, mensagem):
            print("Bloqueado: o assistente não será chamado.")
            continue
        print("Não sinalizada: chamando o assistente.")
        print("Resposta:", responder(cliente, parametros, mensagem))


if __name__ == "__main__":
    main()
