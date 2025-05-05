import csv
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

    def write_csv(
        self, filename: str, data: List[Union[Dict, List]], headers: Optional[List[str]] = None
    ) -> None:
        """Escreve dados em um arquivo CSV.

        Args:
            filename: Nome do arquivo CSV.
            data: Lista de dicionários ou listas com os dados.
            headers: Lista com os cabeçalhos (opcional).
        """
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            if headers:
                writer = csv.DictWriter(file, fieldnames=headers, dialect=self.dialect)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            else:
                writer = csv.writer(file, dialect=self.dialect)
                for row in data:
                    writer.writerow(row)

    def read_csv(self, filename: str, as_dict: bool = False) -> List[Union[Dict, List]]:
        """Lê dados de um arquivo CSV.

        Args:
            filename: Nome do arquivo CSV.
            as_dict: Se True, retorna como lista de dicionários.

        Returns:
            Lista de linhas (ou dicionários, se as_dict=True).
        """
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            if as_dict:
                reader = csv.DictReader(file, dialect=self.dialect)
            else:
                reader = csv.reader(file, dialect=self.dialect)
            return list(reader)
        return []


# Exemplo de uso
if __name__ == "__main__":
    # Instancia a classe com configurações padrão
    csv_handler = CSVHandler()

    # Dados de exemplo
    data = [
        {"nome": "João", "idade": 30, "cidade": "São Paulo"},
        {"nome": "Maria", "idade": 25, "cidade": "Rio de Janeiro"},
    ]
    headers = ["nome", "idade", "cidade"]

    # Escreve no arquivo CSV
    csv_handler.write_csv("exemplo.csv", data, headers)

    # Lê como lista de dicionários
    content_dict = csv_handler.read_csv("exemplo.csv", as_dict=True)
    print("\nConteúdo lido (dicionários):")
    for row in content_dict:
        print(row)

    # Lê como lista de listas
    content_list = csv_handler.read_csv("exemplo.csv", as_dict=False)
    print("\nConteúdo lido (listas):")
    for row in content_list:
        print(row)