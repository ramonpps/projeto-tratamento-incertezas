from analise import Analise

class Menu:
    def __init__(self):
        self.loop = True
        self.test_types = self.get_tests()
        self.nodes = self.get_nodes()
        self.source = None
        self.test_type = None
        self.destination = None
        self.event_type = None
        self.run()

    def get_tests(self):
        return {
            "Atraso e Perda de Pacotes": [
                "failures", "histogram-rtt", "histogram-ttl-reverse", "packet-count-lost-bidir",
                "packet-count-sent", "packet-duplicates-bidir", "packet-loss-rate-bidir",
                "packet-reorders-bidir"
            ],
            "Atraso Unidirecional": [
                "failures", "histogram-owdelay", "histogram-ttl", "packet-count-lost",
                "packet-count-sent", "packet-duplicates", "packet-loss-rate", "packet-reorders"
            ],
            "Banda (BBR)": [
                "failures", "packet-retransmits", "packet-retransmits-subintervals",
                "throughput", "throughput-subintervals"
            ],
            "Banda (CUBIC)": [
                "failures", "packet-retransmits", "packet-retransmits-subintervals",
                "throughput", "throughput-subintervals"
            ],
            "Traceroute": [
                "failures", "packet-trace", "path-mtu"
            ]
        }
    
    def get_nodes(self):
        return [
            "monipe-rj-atraso.rnp.br", "monipe-sp-atraso.rnp.br","monipe-df-atraso.rnp.br",
            "monipe-ba-atraso.rnp.br","monipe-es-atraso.rnp.br","monipe-rs-atraso.rnp.br"
        ]

    def display_options(self, options, prompt):
        for i, option in enumerate(options):
            print(f"{i + 1}. {option}")
        choice = int(input(prompt)) - 1
        if 0 <= choice < len(options):
            return options[choice]
        else:
            raise ValueError("Escolha inválida, fora do intervalo.")

    def select_test(self):
        print("\nSelecione o teste:")
        self.test_type = self.display_options(list(self.test_types.keys()), "Escolha o teste: ")

    def select_source(self):
        print("Selecione a fonte:")
        self.source = self.display_options(self.nodes, "Escolha a fonte: ")

    def select_destination(self):
        print("\nSelecione o destino:")
        node_names = [node for node in self.nodes if node != self.source]
        self.destination = self.display_options(node_names, "Escolha o destino: ")

    def select_event_type(self):
        print("\nSelecione o evento:")
        eventos_disponiveis = self.test_types[self.test_type]
        self.event_type = self.display_options(eventos_disponiveis, "Escolha o evento: ")

    def run(self):
        while self.loop:
            try:
                self.select_test()
                self.select_source()
                self.select_destination()
                self.select_event_type()
                
                print(f"\nTeste selecionado: {self.test_type}")
                print(f"Fonte selecionada: {self.source}")
                print(f"Destino selecionado: {self.destination}")
                print(f"Evento selecionado: {self.event_type}")

                Analise(self.test_type, self.event_type, self.source, self.destination)

                if input('\nDigite y para continuar, ou qualquer coisa para sair: ' ) != 'y':
                    break
            except Exception as e:
                print(f'Erro inesperado: {e}')
                break

# Executar o menu
if __name__ == "__main__":
    Menu()

