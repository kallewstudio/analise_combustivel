import pandas as pd
import os
from django.conf import settings
from pandas.core.interchange.dataframe_protocol import DataFrame


class Combustiveis:
    def __init__(self, combustivel):
        self.combustivel = combustivel

    def read_data(self):
        caminho_do_arquivo =  os.path.join(settings.BASE_DIR, 'combustiveis', 'db', 'revendas_lpc_2024-10-20_2024-10-26.xlsx')
        data = pd.read_excel(
            caminho_do_arquivo,
            skiprows=9,
                             )
        return data