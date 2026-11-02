# Análise e tratamento de dados de sensores neonatais

Projeto de análise de dados simulados de sensores utilizados em incubadoras e dispositivos de monitoramento neonatal. O objetivo é organizar os dados em camadas, aplicar limpeza e padronização e disponibilizar visões de negócio para apoiar o trabalho da equipe assistencial e da gestão hospitalar.

## Público e personas

As visões foram pensadas para:

- **Mariana, enfermeira da UTI Neonatal:** precisa acompanhar rapidamente as leituras recentes, identificar alterações e priorizar alertas.
- **Dr. Rafael, neonatologista:** precisa analisar históricos, tendências e possíveis relações entre os parâmetros monitorados.
- **Alice, gestora hospitalar:** precisa acompanhar indicadores operacionais, volume de leituras e frequência de alertas.

## Arquitetura de dados

O repositório utiliza uma organização em camadas:

```text
bronze/   Dados brutos simulados dos sensores
silver/   Dados limpos, tratados e padronizados
gold/     Visões de negócio, indicadores e gráficos
```

### Bronze

A pasta [`bronze/dados`](./bronze/dados) contém cinco arquivos CSV simulados, com 10.000 leituras cada:

- Temperatura;
- Oxigênio (`SpO2`);
- Frequência cardíaca;
- Umidade;
- Ruído.

### Silver

O script [`silver/processar_sensores.py`](./silver/processar_sensores.py) utiliza `pandas` para:

- Ler os arquivos da camada Bronze;
- Validar as colunas esperadas;
- Converter identificadores, datas e valores para tipos consistentes;
- Remover registros inválidos;
- Remover duplicidades exatas;
- Padronizar as colunas;
- Adicionar sensor e unidade de medida;
- Gerar arquivos individuais e um arquivo consolidado.

O notebook [`silver/script_silver.ipynb`](./silver/script_silver.ipynb) documenta e executa esse processo.

O arquivo consolidado [`silver/leituras_sensores.csv`](./silver/leituras_sensores.csv) possui o seguinte esquema:

| Coluna | Descrição |
|---|---|
| `id_leitura` | Identificador da leitura no sensor |
| `data_hora` | Data e hora da medição |
| `sensor` | Tipo de sensor |
| `valor` | Valor numérico medido |
| `unidade` | Unidade de medida |
| `classificacao` | Classificação original, quando disponível |

### Gold

O notebook [`gold/script_gold.ipynb`](./gold/script_gold.ipynb) consome a Silver e cria:

- Última leitura por sensor para triagem da enfermagem;
- Alertas operacionais classificados por prioridade;
- Histórico horário dos parâmetros;
- Correlações temporais exploratórias entre sensores;
- Indicadores de volume, faixa de valores e quantidade de alertas;
- Gráficos para as três personas.

As tabelas de negócio estão em [`gold`](./gold):

- [`visao_enfermeira_ultima_leitura.csv`](./gold/visao_enfermeira_ultima_leitura.csv);
- [`alertas_operacionais.csv`](./gold/alertas_operacionais.csv);
- [`historico_horario_sensores.csv`](./gold/historico_horario_sensores.csv);
- [`correlacoes_temporais_sensores.csv`](./gold/correlacoes_temporais_sensores.csv);
- [`indicadores_gestao.csv`](./gold/indicadores_gestao.csv);
- [`resumo_execucao_gold.csv`](./gold/resumo_execucao_gold.csv).

Os gráficos exportados estão em [`gold/graficos`](./gold/graficos):

- `mariana_ultima_leitura.png`;
- `mariana_alertas_por_sensor.png`;
- `rafael_tendencias_horarias.png`;
- `rafael_correlacao_temporal.png`;
- `alice_indicadores_operacionais.png`.

## Como executar

### Pré-requisitos

- Python 3;
- `pandas`;
- `matplotlib` para gerar os gráficos;
- Jupyter Notebook ou JupyterLab, caso os notebooks sejam executados interativamente.

Instalação das bibliotecas:

```powershell
python -m pip install pandas matplotlib
```

### Executar a camada Silver

Na raiz do repositório:

```powershell
python .\silver\processar_sensores.py
```

### Executar a camada Gold

Abra [`gold/script_gold.ipynb`](./gold/script_gold.ipynb) no Jupyter ou no VS Code e execute as células em ordem. O notebook lê `silver/leituras_sensores.csv` e grava as tabelas e os gráficos na pasta `gold`.

## Regras de alerta

As faixas utilizadas no notebook Gold são regras operacionais demonstrativas e estão definidas na variável `FAIXAS_OPERACIONAIS`. Elas devem ser revisadas e substituídas pelos limites institucionais aprovados antes de qualquer uso real.

As regras atuais consideram:

- Temperatura: de 20 a 30 graus Celsius;
- Oxigênio: de 92% a 100%;
- Frequência cardíaca: de 60 a 100 bpm;
- Umidade: de 40% a 80%;
- Ruído: acima de 15 dB gera alerta médio e acima de 20 dB gera alerta alto.

## Limitações e próximos passos

Os dados disponíveis são simulados e não possuem:

- Identificador do paciente;
- Identificador da incubadora ou dispositivo;
- Associação entre uma leitura e um recém-nascido específico;
- Registro de abertura, atendimento e encerramento de alertas;
- Protocolo clínico institucional;
- Dados suficientes para calcular tempo real de resposta.

Por isso, as visões atuais não devem ser utilizadas para decisões clínicas reais. Como próximos passos, recomenda-se incluir identificadores anonimizados de paciente e equipamento, eventos de atendimento, regras clínicas aprovadas e controles de acesso aos dados.

## Status da execução

O processamento atual gera 50.000 leituras tratadas, distribuídas entre cinco sensores, além das tabelas e visualizações da camada Gold.
