def consultar_matricula(tentativa, falhas_simuladas):
    if tentativa <= falhas_simuladas:
        raise TimeoutError("O serviço não respondeu a tempo.")
    return "M001 ativa"


def consultar_com_retry(falhas_simuladas):
    for tentativa in range(1, 4):
        try:
            resultado = consultar_matricula(tentativa, falhas_simuladas)
            print(f"Tentativa {tentativa}: sucesso!")
            return resultado
        except TimeoutError as erro:
            print(f"Tentativa {tentativa}: falhou. {erro}")
    return "Fallback: atendimento manual."


def main():
    print("Cenário 1: duas falhas, depois sucesso.")
    print(consultar_com_retry(falhas_simuladas=2))
    print("\nCenário 2: três falhas, tentativas esgotadas.")
    print(consultar_com_retry(falhas_simuladas=3))


if __name__ == "__main__":
    main()
