                                                  Avaliação de Desempenho 2024.1
                          Tratamento de incertezas - Projeto Avaliação de Dados de Medições em Redes
                                                              
                                                  1. Ramon Pedro Pereira Santos
                                                  2. Maria Julia Amancio Galiza

A proposta escolhida para a execução desse projeto foi a análise dos dados da RNP para modelagem em uma fila M/M/1.

Para executar o código, primeiro instale as dependências:

Python: 3.10.9

``pip install -r requirements.txt``

Depois, execute a função main:

``python main.py``

OBS: Nos eventos "failures" e "path-mtu", não consegui encontrar uma combinação de source-destination que me fornecesse um objeto não nulo. Dessa forma, não consegui processar os dados e realizar a modelagem.
