import os
import pandas as pd
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from django.conf import settings
import unicodedata
import re
from openpyxl import load_workbook


def normalizar_nome_coluna(nome):
    # Converte qualquer valor não string para uma string vazia
    if not isinstance(nome, str):
        nome = ""
    # Remove acentos e caracteres especiais
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    # Substitui caracteres não alfanuméricos por underscore (_)
    nome = re.sub(r'\W+', '_', nome)
    return nome.lower()  # Converte para minúsculas para manter a consistência


def obter_coordenadas_e_atualizar_excel(arquivo_excel, endereco_cols):
    caminho_arquivo = os.path.join(settings.BASE_DIR, arquivo_excel)

    # Carrega o arquivo Excel
    df = pd.read_excel(caminho_arquivo, nrows=10, skiprows=9)

    # Normaliza os nomes das colunas
    df.columns = [normalizar_nome_coluna(col) for col in df.columns]

    # Imprime os nomes das colunas para depuração
    print("Colunas normalizadas:", df.columns)

    # Normaliza as colunas de endereço para garantir correspondência com df.columns
    endereco_cols = [normalizar_nome_coluna(col) for col in endereco_cols]
    print("Colunas de endereço normalizadas:", endereco_cols)

    # Resto do código permanece igual
    if 'latitude' not in df.columns:
        df['latitude'] = None
    if 'longitude' not in df.columns:
        df['longitude'] = None

    geolocator = Nominatim(user_agent="combustiveis_map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2, max_retries=3, error_wait_seconds=10)

    for idx, row in df.iterrows():
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            endereco = ", ".join(str(row[col]) for col in endereco_cols if col in row and pd.notna(row[col]))
            try:
                location = geocode(endereco, timeout=10)
                if location:
                    df.at[idx, 'latitude'] = location.latitude
                    df.at[idx, 'longitude'] = location.longitude
            except GeocoderTimedOut:
                print(f"Timeout ao processar o endereço: {endereco}. Tentando novamente...")
                continue

    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        sheet_name = writer.book.sheetnames[0]
        df.to_excel(writer, index=False, sheet_name=sheet_name)


class Combustiveis:
    @staticmethod
    def read_data():
        caminho_do_arquivo = os.path.join(settings.BASE_DIR, 'combustiveis', 'db',
                                          'revendas_lpc_2024-10-20_2024-10-26.xlsx')
        data = pd.read_excel(
            caminho_do_arquivo,
            skiprows=9,
            nrows=100,
        )
        return data
