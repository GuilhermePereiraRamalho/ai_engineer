import json
import sys
from pathlib import Path
from dotenv import dotenv_values
from openai import OpenAI
import yaml

RAIZ = Path(__file__).resolve().parents[1]
PEDIDO = "Quero cancelar minha matrícula M001, feita há 3 dias."


def gerar_proposta(pedido):
    ambiente = dotenv_values(RAIZ / ".env")
    perfis = yaml.safe_load((RAIZ / "config/models.yaml").read_text(encoding="utf-8"))
    perfil = perfis[ambiente.get("PERFIL_MODELO", "fast")]
    cliente = OpenAI(
        api_key=ambiente.get("OPENAI_API_KEY", ""), timeout=30, max_retries=0
    )
    resposta = cliente.responses.create(
        model=perfil["model"],
        reasoning={"effort": perfil["reasoning_effort"]},
        max_output_tokens=1200,
        store=False,
        instructions=(
            "Prepare uma resposta curta em português para revisão humana antes do "
            "envio. Política fictícia: até 7 dias permite análise de reembolso; "
            "todo reembolso exige aprovação humana. "
            "Não afirme ter cancelado a matrícula nem realizado pagamentos."
        ),
        input=pedido,
    )
    proposta = resposta.output_text.strip()
    if not proposta:
        raise ValueError("O modelo não retornou uma proposta de texto.")
    return proposta


def main():
    caminho = Path(__file__).parent / "saida" / "proposta.json"
    caminho.parent.mkdir(exist_ok=True)

    if not caminho.exists():
        print("Gerando proposta com o LLM...")
        tarefa = {
            "pedido": PEDIDO,
            "proposta": gerar_proposta(PEDIDO),
            "estado": "aguardando_aprovacao",
        }
        print("Revise a proposta e execute novamente com --aprovar.")
    else:
        tarefa = json.loads(caminho.read_text(encoding="utf-8"))
        print("Proposta recuperada do arquivo, sem chamar o LLM.")
        if tarefa["estado"] == "concluida":
            print("Entrega fictícia já registrada. Nada será repetido.")
        elif "--aprovar" in sys.argv:
            tarefa["estado"] = "concluida"
            print("Proposta aprovada. Registrando entrega fictícia.")
        else:
            print("Ainda aguardando aprovação. Use --aprovar após revisar.")

    caminho.write_text(
        json.dumps(tarefa, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Arquivo:", caminho)
    print(caminho.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
