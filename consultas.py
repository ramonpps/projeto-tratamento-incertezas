# consultas.py
import requests
import urllib3

# Suprimir o aviso de InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Consulta:
    def __init__(self, event_type, test_type, source, destination):
        self.base_url = "http://monipe-central.rnp.br"
        self.url = "http://monipe-central.rnp.br/esmond/perfsonar/archive/"
        self.parametros = {
            'source': source,
            'destination': destination,
            'event-type': event_type,
            'time-range': 86400
        }

    def get_data(self):
        try:
            resposta = requests.get(self.url, params=self.parametros, verify=False)
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException as e:
            print(f"Erro na consulta: {e}")
            return None