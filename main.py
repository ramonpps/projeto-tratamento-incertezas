from modulos.analise import Analise

class Menu:
    def __init__(self):
        """
        Inicializa o menu de seleção de testes de rede.
        """
        self.loop = True
        self.test_types = self.get_tests()
        self.nodes_delay = self.get_nodes_delay()
        self.nodes_bandwidth = self.get_nodes_bandwidth()
        self.source = None
        self.test_type = None
        self.destination = None
        self.event_type = None
        self.run()

    def get_tests(self):
        """
        Define os tipos de testes disponíveis e seus eventos associados.
        """
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

    def get_nodes_delay(self):
        """
        Retorna os nós disponíveis para testes de atraso.
        """
        return [
            "monipe-rj-atraso.rnp.br", "monipe-sp-atraso.rnp.br", "monipe-df-atraso.rnp.br",
            "monipe-ba-atraso.rnp.br", "monipe-es-atraso.rnp.br", "monipe-rs-atraso.rnp.br"
        ]

    def get_nodes_bandwidth(self):
        """
        Retorna os nós disponíveis para testes de largura de banda.
        """
        return [
            "monipe-rj-banda.rnp.br", "monipe-sp-banda.rnp.br", "monipe-df-banda.rnp.br",
            "monipe-ba-banda.rnp.br", "monipe-es-banda.rnp.br", "monipe-rs-banda.rnp.br"
        ]

    def display_options(self, options, prompt):
        """
        Exibe as opções disponíveis e solicita ao usuário que selecione uma delas.

        Args:
        - options: Lista de opções disponíveis.
        - prompt: Mensagem para solicitar a escolha do usuário.

        Returns:
        - A opção selecionada pelo usuário.
        """
        for i, option in enumerate(options):
            print(f"{i + 1}. {option}")
        choice = int(input(prompt)) - 1
        if 0 <= choice < len(options):
            return options[choice]
        else:
            raise ValueError("Escolha inválida, fora do intervalo.")

    def select_test(self):
        """
        Solicita ao usuário que selecione o tipo de teste a ser realizado.
        """
        print("\nSelecione o teste:")
        self.test_type = self.display_options(list(self.test_types.keys()), "Escolha o teste: ")

    def select_source(self):
        """
        Solicita ao usuário que selecione a fonte do teste com base no tipo selecionado.
        """
        print("Selecione a fonte:")
        if self.test_type == 'Banda (BBR)' or self.test_type == 'Banda (CUBIC)':
            self.source = self.display_options(self.nodes_bandwidth, "Escolha a fonte: ")
        else:
            self.source = self.display_options(self.nodes_delay, "Escolha a fonte: ")

    def select_destination(self):
        """
        Solicita ao usuário que selecione o destino do teste com base na fonte selecionada.
        """
        print("\nSelecione o destino:")
        if self.test_type == 'Banda (BBR)' or self.test_type == 'Banda (CUBIC)':
            node_names = [node for node in self.nodes_bandwidth if node != self.source]
        else:
            node_names = [node for node in self.nodes_delay if node != self.source]
        self.destination = self.display_options(node_names, "Escolha o destino: ")

    def select_event_type(self):
        """
        Solicita ao usuário que selecione o evento a ser analisado.
        """
        print("\nSelecione o evento:")
        available_events = self.test_types[self.test_type]
        self.event_type = self.display_options(available_events, "Escolha o evento: ")

    def run(self):
        """
        Executa o loop principal do menu até que o usuário opte por sair.
        """
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

                bandwidth = 10000000000 if self.test_type == 'Banda (BBR)' else 9999999999

                Analise(self.test_type, self.event_type, self.source, self.destination, bandwidth)

                if input('\nDigite y para continuar, ou qualquer coisa para sair: ' ) != 'y':
                    break
            except Exception as e:
                print(f'Erro inesperado: {e}')
                if input('\nDigite y para continuar, ou qualquer coisa para sair: ' ) != 'y':
                    exit()
                else:
                    self.run()

if __name__ == "__main__":
    Menu()