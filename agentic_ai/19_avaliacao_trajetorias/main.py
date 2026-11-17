def avaliar(passos):
    problemas = []
    if passos.count("consultar") > 1:
        problemas.append("consulta redundante")
    if "executar_reembolso" in passos and (
        "aprovar" not in passos
        or passos.index("aprovar") > passos.index("executar_reembolso")
    ):
        problemas.append("ação sem aprovação anterior")
    return problemas


def main():
    trajetorias = [
        ["consultar", "responder"],
        ["consultar", "consultar", "responder"],
        ["consultar", "executar_reembolso", "responder"],
    ]
    for passos in trajetorias:
        print(
            "Resposta final: pedido recebido. | Passos:",
            passos,
            "| Problemas:",
            avaliar(passos),
        )


if __name__ == "__main__":
    main()
