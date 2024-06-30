import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Consulta:
    """
    Classe para realizar consultas aos dados de perfSONAR.

    Attributes:
    - base_url (str): URL base para as consultas.
    - url (str): URL completa para o endpoint de consulta.
    - test_type (str): Tipo de teste a ser realizado.
    - parametros (dict): Parâmetros da consulta, incluindo source, destination, event-type e time-range.
    """

    def __init__(self, event_type, test_type, source, destination, bandwidth):
        """
        Inicializa uma nova instância da classe Consulta.

        Args:
        - event_type (str): Tipo de evento a ser consultado.
        - test_type (str): Tipo de teste a ser realizado.
        - source (str): Nó de origem da consulta.
        - destination (str): Nó de destino da consulta.
        - bandwidth (int): Largura de banda para testes de Banda (BBR) ou Banda (CUBIC).
        """
        self.base_url = "http://monipe-central.rnp.br"
        self.url = f"{self.base_url}/esmond/perfsonar/archive/"
        self.test_type = test_type
        self.parametros = {
            'source': source,
            'destination': destination,
            'event-type': event_type,
            'time-range': 86400
        }

        if self.test_type == 'Banda (BBR)' or self.test_type == 'Banda (CUBIC)':
            self.parametros['bw-target-bandwidth'] = bandwidth

    def get_data(self):
        """
        Realiza a consulta aos dados de perfSONAR com base nos parâmetros definidos.

        Returns:
        - dict: Dados retornados pela consulta em formato JSON, ou None se houver erro na consulta.
        """
        try:
            resposta = requests.get(self.url, params=self.parametros, verify=False)
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException as e:
            print(f"Erro na consulta: {e}")
            return None

