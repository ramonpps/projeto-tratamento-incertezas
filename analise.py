# analise.py
import math
from consultas import Consulta
import requests

class Analise(Consulta):
    def __init__(self, test_type, event_type, source, destination):
        super().__init__(event_type, source, destination)
        self.dados = self.get_data()
        if self.dados:
            self.analisar()
        else:
            print("Dados vazios.")

    def analisar(self):
        if not self.dados:
            print("Nenhum dado disponível para análise.")
            return
        for item in self.dados:
            event_types = item.get('event-types', [])
            for event in event_types:
                if event['event-type'] == self.parametros['event-type']:
                    self.escolher(event)

    def escolher(self,event):
        if self.parametros['event-type'] == 'histogram-owdelay' or self.parametros['event-type'] == 'histogram-rtt':
            self.analisar_histogram(event)
        
    #region Histogram
    def analisar_histogram(self, event):
        summaries = event.get('summaries', [])
        for summary in summaries:
            if summary['summary-type'] == 'statistics' and summary['summary-window'] == '0':
                uri = summary['uri']
                print(f"\nAnalisando dados do URI: {self.base_url}{uri}")
                self.analisar_dados_histograma(uri)

    def analisar_dados_histograma(self, uri):
        try:
            resposta = requests.get(self.base_url + uri, verify=False)
            resposta.raise_for_status()
            dados = resposta.json()
        except requests.RequestException as e:
            print(f"Erro na consulta do URI {uri}: {e}")
            return

        values = [entry['val']['mean'] for entry in dados if 'val' in entry and 'mean' in entry['val']]
        if values:
            num_events = len(values)
            total_value = sum(values)
            mean_value = total_value / num_events
            variance_value = sum((x - mean_value) ** 2 for x in values) / num_events
            std_dev_value = math.sqrt(variance_value)

            print(f"Total de entradas: {num_events}")
            print(f"\nMenor valor: {min(values)} ms")
            print(f"Maior valor: {max(values)} ms")
            print(f"Média dos valores: {mean_value} ms")
            print(f"Variância dos valores: {variance_value} ms²")
            print(f"Desvio padrão dos valores: {std_dev_value} ms")

            lambda_rate = num_events / (86400)  # taxa média de chegada em eventos por segundo
            mu_rate = 1 / (mean_value / 1000)  # taxa média de serviço em eventos por segundo
            rho = lambda_rate / mu_rate  # utilização do sistema

            if rho < 1:
                Wq = rho / (mu_rate * (1 - rho))  # tempo médio de espera na fila (segundos)
                W = 1 / (mu_rate * (1 - rho))  # tempo médio de espera no sistema (segundos)
                Lq = (rho ** 2) / (1 - rho)  # número médio de eventos na fila
                L = rho / (1 - rho)  # número médio de eventos no sistema

                print(f"\nTaxa média de chegada (λ): {lambda_rate:.6f} eventos/segundo")
                print(f"Taxa média de serviço (μ): {mu_rate:.6f} eventos/segundo")
                print(f"Utilização do sistema (ρ): {rho:.6f}")
                print(f"Tempo médio de espera na fila (Wq): {Wq:.6f} segundos")
                print(f"Tempo médio de espera no sistema (W): {W:.6f} segundos")
                print(f"Número médio de eventos na fila (Lq): {Lq:.6f} eventos")
                print(f"Número médio de eventos no sistema (L): {L:.6f} eventos")
            else:
                print("Utilização do sistema é 1 (ou maior), o que indica que o sistema está saturado.")
                print("Não é possível calcular o tempo de espera na fila e no sistema para um sistema saturado.")
        else:
            print("\nNenhum dado disponível.")
    #endregion

