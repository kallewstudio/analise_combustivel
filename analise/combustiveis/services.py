# combustiveis/services.py
import pandas as pd
import os
import unicodedata
import re
from django.conf import settings

def normalizar_nome_coluna(nome):
    # Remove acentos e caracteres especiais e converte para ASCII "cru"
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    nome = re.sub(r'\W+', '_', nome)
    return nome.lower()

def tratar_dados_excel(file_path):
    try:
        # Carrega o arquivo sem definir cabeçalho para identificar a linha correta
        df = pd.read_excel(file_path, header=None)

        # Colunas esperadas
        colunas_alvo = [
            "CNPJ", "RAZÃO", "FANTASIA", "ENDEREÇO", "NÚMERO", "COMPLEMENTO", "BAIRRO",
            "CEP", "MUNICÍPIO", "ESTADO", "BANDEIRA", "PRODUTO",
            "UNIDADE DE MEDIDA", "PREÇO DE REVENDA", "DATA DA COLETA"
        ]

        # Identifica a linha de cabeçalho correta
        linha_cabecalho = None
        for i, row in df.iterrows():
            if all(coluna in row.values for coluna in colunas_alvo):
                linha_cabecalho = i
                break

        if linha_cabecalho is None:
            return False, "Cabeçalho não encontrado no arquivo."

        # Recarrega o DataFrame usando a linha de cabeçalho correta
        df = pd.read_excel(file_path, header=linha_cabecalho)

        # Normaliza os nomes das colunas
        df.columns = [normalizar_nome_coluna(col) for col in df.columns]

        # Identifica as colunas `estado` e `municipio`
        estado_col = [col for col in df.columns if 'estado' in col.lower()]
        cidade_col = [col for col in df.columns if 'municipio' in col.lower() or 'cidade' in col.lower()]

        if not estado_col or not cidade_col:
            return False, "Colunas 'estado' e 'cidade/municipio' não encontradas no arquivo."

        # Obtém os valores únicos de `estado` e `cidade`
        estados = df[estado_col[0]].dropna().unique()
        cidades = df[cidade_col[0]].dropna().unique()

        return True, {"estados": estados, "cidades": cidades, "estado_col": estado_col[0], "cidade_col": cidade_col[0]}

    except Exception as e:
        return False, str(e)
