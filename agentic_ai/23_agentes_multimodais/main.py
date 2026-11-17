from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml
import argparse
import base64

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


def consultar(codigo):
    matriculas = {"M001": "ativa no curso Python", "M002": "ativa no curso Dados"}
    if codigo not in matriculas:
        raise SystemExit(
            "Código extraído não corresponde a uma matrícula fictícia conhecida."
        )
    return matriculas[codigo]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imagem", type=Path, help="Imagem PNG local.")
    args = parser.parse_args()
    imagem = args.imagem or Path(__file__).with_name("matricula.png")
    cliente, parametros = conectar()
    dados = base64.b64encode(imagem.read_bytes()).decode()
    resposta = cliente.responses.create(
        **parametros,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Leia a matrícula da imagem. Responda somente M e os 3 "
                            "dígitos."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": "data:image/png;base64," + dados,
                    },
                ],
            }
        ]
    )
    codigo = resposta.output_text.strip()
    print("Código extraído:", codigo)
    print("Resultado da ferramenta:", consultar(codigo))


if __name__ == "__main__":
    main()
