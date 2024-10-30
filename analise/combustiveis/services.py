# combustiveis/services.py
import pandas as pd
import unicodedata
import re

def normalizar_nome_coluna(nome):
    # Remove acentos e caracteres especiais e converte para ASCII "cru"
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    # Substitui caracteres não alfanuméricos por underscore (_)
    nome = re.sub(r'\W+', '_', nome)
    return nome.lower()

def tratar_dados_excel(file_path):
    try:
        # Carrega o arquivo sem definir uma linha de cabeçalho
        df = pd.read_excel(file_path, header=None)

        # Identifica a linha correta com o cabeçalho
        colunas_alvo = [
            "CNPJ", "RAZÃO", "FANTASIA", "ENDEREÇO", "NÚMERO", "COMPLEMENTO", "BAIRRO",
            "CEP", "MUNICÍPIO", "ESTADO", "BANDEIRA", "PRODUTO",
            "UNIDADE DE MEDIDA", "PREÇO DE REVENDA", "DATA DA COLETA"
        ]
        linha_cabecalho = None
        for i, row in df.iterrows():
            if all(coluna in row.values for coluna in colunas_alvo):
                linha_cabecalho = i
                break

        if linha_cabecalho is None:
            return False, "Cabeçalho não encontrado no arquivo."

        # Define a linha correta como cabeçalho
        df = pd.read_excel(file_path, header=linha_cabecalho)

        # Normaliza os nomes das colunas
        df.columns = [normalizar_nome_coluna(col) for col in df.columns]

        # Salva o arquivo tratado na pasta final
        df.to_excel(file_path, index=False)

        return True, "Arquivo processado com sucesso."

    except Exception as e:
        return False, str(e)
