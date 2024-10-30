# combustiveis/services.py
import pandas as pd
import unicodedata
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut

def normalizar_nome_coluna(nome):
    # Remove acentos e caracteres especiais e converte para ASCII "cru"
    nome = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode('utf-8')
    # Substitui caracteres não alfanuméricos por underscore (_)
    nome = re.sub(r'\W+', '_', nome)
    return nome.lower()

def tratar_dados_excel(file_path, limite=30):
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

        # Adiciona as colunas `longitude` e `latitude` vazias, se não existirem
        if 'longitude' not in df.columns:
            df['longitude'] = None
        if 'latitude' not in df.columns:
            df['latitude'] = None

        # Configuração do geocodificador com timeout e rate limit
        geolocator = Nominatim(user_agent="combustiveis_map")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2, max_retries=3, error_wait_seconds=10)

        # Loop para preencher as colunas `longitude` e `latitude` até o limite
        linhas_processadas = 0
        for idx, row in df.iterrows():
            if linhas_processadas >= limite:
                break  # Interrompe o loop quando o limite é atingido

            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                # Monta o endereço completo
                endereco_completo = f"{row['endereco']}, {row['numero']}, {row['bairro']}, {row['cep']}, {row['municipio']}, {row['estado']}"
                coordenadas = None

                # Tentativa 1: Endereço completo
                try:
                    coordenadas = geocode(endereco_completo, timeout=10)
                    if coordenadas:
                        print(f"Endereço completo: {endereco_completo}")
                        print(f"Coordenadas: Latitude = {coordenadas.latitude}, Longitude = {coordenadas.longitude}")
                except GeocoderTimedOut:
                    print(f"Timeout ao processar o endereço completo: {endereco_completo}")

                # Tentativa 2: Somente município e estado
                if not coordenadas:
                    endereco_alternativo = f"{row['municipio']}, {row['estado']}"
                    try:
                        coordenadas = geocode(endereco_alternativo, timeout=10)
                        if coordenadas:
                            print(f"Endereço alternativo: {endereco_alternativo}")
                            print(f"Coordenadas: Latitude = {coordenadas.latitude}, Longitude = {coordenadas.longitude}")
                    except GeocoderTimedOut:
                        print(f"Timeout ao processar o endereço alternativo: {endereco_alternativo}")

                # Tentativa 3: Somente CEP
                if not coordenadas and pd.notna(row['cep']):
                    endereco_cep = f"{row['cep']}, {row['estado']}"
                    try:
                        coordenadas = geocode(endereco_cep, timeout=10)
                        if coordenadas:
                            print(f"Endereço via CEP: {endereco_cep}")
                            print(f"Coordenadas: Latitude = {coordenadas.latitude}, Longitude = {coordenadas.longitude}")
                    except GeocoderTimedOut:
                        print(f"Timeout ao processar o CEP: {endereco_cep}")

                # Atualiza o DataFrame se as coordenadas foram obtidas
                if coordenadas:
                    df.at[idx, 'latitude'] = coordenadas.latitude
                    df.at[idx, 'longitude'] = coordenadas.longitude
                    linhas_processadas += 1
                else:
                    print(f"Coordenadas não encontradas para o endereço: {endereco_completo}")

        # Ordena o DataFrame para que as linhas com coordenadas preenchidas venham primeiro
        df = df.sort_values(by=['latitude', 'longitude'], ascending=[False, False])

        # Salva o DataFrame atualizado de volta no Excel com as coordenadas preenchidas
        df.to_excel(file_path, index=False)

        return True, f"Arquivo processado com sucesso. Coordenadas preenchidas em até {limite} linhas."

    except Exception as e:
        return False, str(e)
