import math
import requests
from modulos.consultas import Consulta

class Analise(Consulta):
    def __init__(self, test_type, event_type, source, destination, bandwidth):
        """
        Inicializa a classe de análise com os parâmetros necessários.

        Args:
        - test_type: Tipo de teste a ser realizado.
        - event_type: Tipo de evento a ser analisado.
        - source: Fonte do teste.
        - destination: Destino do teste.
        - bandwidth: Largura de banda utilizada no teste.
        """
        super().__init__(event_type, test_type, source, destination, bandwidth)
        self.bandwidth = bandwidth
        self.dados = self.get_data()
        self.test_type = test_type
        
        if self.dados:
            self.analisar()
        else:
            print("A consulta para o archive retornou um objeto vazio. Isso está acontecendo em duas situações: \n   1. No evento 'failures' \n   2. No evento 'path-mtu' \n Como não há dados a serem exibidos, não consegui implementar a lógica de modelagem.")

    def analisar(self):
        """
        Analisa os dados obtidos e executa a análise específica conforme o tipo de evento.
        """
        if not self.dados:
            print("Nenhum dado disponível para análise.")
            return
        
        for item in self.dados:
            event_types = item.get('event-types', [])
            for event in event_types:
                if event['event-type'] == self.parametros['event-type']:
                    self.escolher(event)

    def escolher(self, event):
        """
        Escolhe o método de análise apropriado com base no tipo de evento.

        Args:
        - event: Dicionário contendo informações do evento.
        """
        if self.parametros['event-type'] in ['packet-retransmits', 'packet-reorders', 'packet-loss-rate', 'packet-duplicates', 'packet-reorders-bidir', 'packet-loss-rate-bidir', 'packet-duplicates-bidir', 'histogram-ttl-reverse', 'histogram-ttl', 'packet-retransmits-subintervals', 'throughput-subintervals']:
            self.analisar_ttl_reverse(event)
        elif self.parametros['event-type'] in ['histogram-owdelay', 'histogram-rtt']:
            self.analisar_histogram(event)
        elif self.parametros['event-type'] in ['packet-count-sent', 'packet-count-lost', 'packet-count-lost-bidir', 'throughput']:
            self.analisar_packet_count(event)
        elif self.parametros['event-type'] in ['packet-reorders', 'packet-trace']:
            self.analisar_bidir(event)
        else:
            self.analisar_histogram(event)

    def analisar_ttl_reverse(self, event):
        """
        Realiza a análise específica para o tipo de evento de histograma TTL reverso.

        Args:
        - event: Dicionário contendo informações do evento de histograma TTL reverso.
        """
        uri = event.get('base-uri')
        self.analisar_dados_ttl_reverse(uri)

    def analisar_dados_ttl_reverse(self, uri):
        """
        Realiza a consulta e análise dos dados do URI para histograma TTL reverso.

        Args:
        - uri: URI para consulta dos dados.
        """
        try:
            resposta = requests.get(self.base_url + uri, verify=False)
            resposta.raise_for_status()
            dados = resposta.json()
        except requests.RequestException as e:
            print(f"Erro na consulta do URI {uri}: {e}")
            return
        
        values = []

        for entry in dados:
            if 'val' in entry:
                if isinstance(entry['val'], dict):
                    values.extend(entry['val'].values())
                elif isinstance(entry['val'], list):
                    for data in entry['val']:
                        if 'duration' in data:
                            values.append(data['duration'])
                else:
                    values.append(entry['val'])

        self.calcular(values)

    def analisar_histogram(self, event):
        """
        Realiza a análise específica para o tipo de evento de histograma.

        Args:
        - event: Dicionário contendo informações do evento de histograma.
        """
        summaries = event.get('summaries', [])
        for summary in summaries:
            if int(summary['summary-window']) == self.parametros['time-range']:
                uri = summary['uri']
                self.analisar_dados_histograma(uri)

    def analisar_dados_histograma(self, uri):
        """
        Realiza a consulta e análise dos dados do URI para histograma.

        Args:
        - uri: URI para consulta dos dados.
        """
        try:
            resposta = requests.get(self.base_url + uri, verify=False)
            resposta.raise_for_status()
            dados = resposta.json()
        except requests.RequestException as e:
            print(f"Erro na consulta do URI {uri}: {e}")
            return
        
        values = [entry['val']['mean'] for entry in dados if 'val' in entry and 'mean' in entry['val']]
        self.calcular(values)

    def analisar_packet_count(self, event):
        """
        Realiza a análise específica para o tipo de evento de contagem de pacotes.

        Args:
        - event: Dicionário contendo informações do evento de contagem de pacotes.
        """
        summaries = event.get('summaries', [])
        for summary in summaries:
            if int(summary['summary-window']) == self.parametros['time-range']:
                uri = summary['uri']
                self.analisar_dados_ttl_reverse(uri)

    def analisar_bidir(self, event):
        """
        Realiza a análise específica para o tipo de evento de bidirecional.

        Args:
        - event: Dicionário contendo informações do evento bidirecional.
        """
        uri = event.get('base-uri')
        self.analisar_dados_bidir(uri)

    def analisar_dados_bidir(self, uri):
        """
        Realiza a consulta e análise dos dados do URI para evento bidirecional.

        Args:
        - uri: URI para consulta dos dados.
        """
        try:
            resposta = requests.get(self.base_url + uri, verify=False)
            resposta.raise_for_status()
            dados = resposta.json()

        except requests.RequestException as e:
            print(f"Erro na consulta do URI {uri}: {e}")
            return
        
        values_ttl = []
        values_rtt = []

        for entry in dados:
            if 'val' in entry:
                if isinstance(entry['val'], list):
                    for data in entry['val']:
                        if 'ttl' in data:
                            values_ttl.append(data['ttl'])
                        if 'rtt' in data:
                            values_rtt.append(data['rtt'])
        
        if values_rtt:
            self.calcular(values_rtt)
        
        if values_ttl:
            self.calcular(values_ttl)

    def calcular(self, values):
        """
        Realiza o cálculo estatístico dos valores fornecidos.

        Args:
        - values: Lista de valores a serem analisados estatisticamente.
        """
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
            try:
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
            except Exception as e:
                print('Taxa média de serviço é zero, a fila está inoperante: ', e)
        else:
            print("\nNenhum dado disponível.")


            

