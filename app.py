import requests
import json
import urllib3
import math

# Suprimir o aviso de InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Consulta:
    def __init__(self, event_type, source, destination):
        self.base_url = "http://monipe-central.rnp.br"
        self.url = "http://monipe-central.rnp.br/esmond/perfsonar/archive/"
        self.parametros = {
            'source': source,
            'destination': destination,
            'event-type': event_type,
            'time-range': 86400
        }

    def get(self):
        resposta = requests.get(self.url, params=self.parametros, verify=False)
        if resposta.status_code != 200:
            print(f"Erro na consulta: {resposta.status_code}")
            return None
        else:
            data = resposta.json()
            return data

class Analise(Consulta):
    def __init__(self, event_type, source, destination):
        super().__init__(event_type, source, destination)
        self.dados = self.get()
        if self.dados:
            self.analisar()

    def analisar(self):
        if not self.dados:
            print("Nenhum dado disponível para análise.")
            return

        #print("Dados retornados:")
        for item in self.dados:
            event_types = item.get('event-types', [])
            for event in event_types:
                if event['event-type'] == self.parametros['event-type']:
                    self.analisar_histogram(event)

    def analisar_histogram(self, event):
        summaries = event.get('summaries', [])
        for summary in summaries:
            if summary['summary-type'] == 'statistics' and summary['summary-window'] == '0':
                uri = summary['uri']
                print(f"\nAnalisando dados do URI: {self.base_url}{uri}")
                self.analisar_dados(uri)

    def analisar_dados(self, uri):
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

class Menu:
    def __init__(self):
        self.loop = True
        self.nodes = self.get_nodes()
        self.event_types = self.get_event_types()
        self.source = None
        self.destination = None
        self.event_type = None
        self.run()

    def get_nodes(self):
        return [
            "monipe-ac-atraso.rnp.br", "monipe-al-atraso.rnp.br","monipe-am-atraso.rnp.br",
            "monipe-ap-atraso.rnp.br","monipe-ba-atraso.rnp.br","monipe-ce-atraso.rnp.br",
            "monipe-df-atraso.rnp.br","monipe-es-atraso.rnp.br","monipe-go-atraso.rnp.br",
            "monipe-ma-atraso.rnp.br","monipe-mg-atraso.rnp.br","monipe-ms-atraso.rnp.br",
            "monipe-mt-atraso.rnp.br","monipe-pa-atraso.rnp.br","monipe-pb-atraso.rnp.br",
            "monipe-pe-atraso.rnp.br","monipe-pi-atraso.rnp.br","monipe-pr-atraso.rnp.br",
            "monipe-rj-atraso.rnp.br","monipe-rn-atraso.rnp.br","monipe-ro-atraso.rnp.br",
            "monipe-rr-atraso.rnp.br","monipe-rs-atraso.rnp.br","monipe-sc-atraso.rnp.br",
            "monipe-se-atraso.rnp.br","monipe-sp-atraso.rnp.br","monipe-to-atraso.rnp.br"
        ]

    def get_event_types(self):
        return ["histogram-owdelay", "histogram-rtt"]

    def display_options(self, options, prompt):
        for i, option in enumerate(options):
            print(f"{i + 1}. {option}")
        choice = int(input(prompt)) - 1
        return options[choice]

    def select_source(self):
        print("\nSelecione a fonte:")
        self.source = self.display_options(self.nodes, "Escolha a fonte: ")

    def select_destination(self):
        print("\nSelecione o destino:")
        node_names = [node for node in self.nodes if node != self.source]
        self.destination = self.display_options(node_names, "Escolha o destino: ")

    def select_event_type(self):
        print("\nSelecione o evento:")
        self.event_type = self.display_options(self.event_types, "Escolha o evento: ")

    def run(self):
        while self.loop:
            try:
                self.select_source()
                self.select_destination()
                self.select_event_type()

                print(f"\nFonte selecionada: {self.source}")
                print(f"Destino selecionado: {self.destination}")
                print(f"Evento selecionado: {self.event_type}")

                analise = Analise(self.event_type, self.source, self.destination)

                if input('\nDigite y para continuar, ou qualquer coisa para sair: ' ) != 'y':
                    break
            except:
                print('Opções inválidas, tente novamente.')



# Executar o menu
Menu()




