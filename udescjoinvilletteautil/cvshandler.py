import csv
import os
from udescjoinvilletteamodel.player import Player
from typing import List, Dict, Optional, Union


class CSVHandler:
    """Classe para manipulação de arquivos CSV com dialeto personalizado."""

    def __init__(
        self,
        dialect: str = "excel",
        delimiter: str = ";",
        quotechar: str = '"',
        doublequote: bool = True,
        skipinitialspace: bool = True,
        lineterminator: str = "\n",
        quoting: int = csv.QUOTE_MINIMAL,
    ) -> None:
        """Inicializa a classe com configurações de dialeto CSV.

        Args:
            dialect: Dialeto CSV (padrão: 'excel').
            delimiter: Caractere delimitador (padrão: ';').
            quotechar: Caractere de citação (padrão: '"').
            doublequote: Escapa citação duplicando (padrão: True).
            skipinitialspace: Ignora espaços após delimitadores (padrão: True).
            lineterminator: Caractere de terminação de linha (padrão: '\n').
            quoting: Estilo de citação (padrão: csv.QUOTE_MINIMAL).
        """
        csv.register_dialect(
            dialect,
            delimiter=delimiter,
            quotechar=quotechar,
            doublequote=doublequote,
            skipinitialspace=skipinitialspace,
            lineterminator=lineterminator,
            quoting=quoting,
        )
        self.dialect = dialect

    def write_csv(self, filename, data):  
        
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            
            if data != []: 
                header = list(data[0].keys())
                w = csv.DictWriter(file, fieldnames= header)
                w.writeheader()
                w.writerows(data)


    def get_last_serial(self, dir_path):
        

        print(dir_path)
        archives = os.listdir(dir_path)  

        if archives == []: 
            return 0; 

        else: 
            last_elem = archives[-1].split("_")
            return (int(last_elem[0])+1)  


    def read_csv(self, filename: str, as_dict: bool = False):

        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            if as_dict:
                reader = csv.DictReader(file, dialect=self.dialect)
            else:
                reader = csv.reader(file, dialect=self.dialect)
            return list(reader)
        return []






    
        