"""Limpeza, tratamento e padronizacao das leituras da camada bronze."""

from pathlib import Path
from typing import Dict, Optional

import pandas as pd


CONFIGURACAO_SENSORES: Dict[str, Dict[str, str]] = {
    "leituras_temperatura_10k.csv": {
        "sensor": "temperatura",
        "coluna_valor": "temperatura",
        "unidade": "graus_celsius",
    },
    "leituras_oxigenio_10k.csv": {
        "sensor": "oxigenio",
        "coluna_valor": "spo2",
        "unidade": "percentual",
    },
    "leituras_frequencia_cardiaca_10k.csv": {
        "sensor": "frequencia_cardiaca",
        "coluna_valor": "bpm",
        "unidade": "bpm",
    },
    "leituras_umidade_10k.csv": {
        "sensor": "umidade",
        "coluna_valor": "umidade",
        "unidade": "percentual",
    },
    "leituras_ruido_10k.csv": {
        "sensor": "ruido",
        "coluna_valor": "db",
        "unidade": "decibeis",
    },
}


def localizar_projeto() -> Path:
    """Localiza a raiz do projeto a partir do diretorio atual."""
    candidatos = [Path.cwd(), Path.cwd().parent]
    for candidato in candidatos:
        if (candidato / "bronze" / "dados").is_dir():
            return candidato
    raise FileNotFoundError(
        "Nao foi possivel localizar a pasta bronze/dados a partir do diretorio atual."
    )


def tratar_arquivo(caminho: Path, configuracao: Dict[str, str]) -> pd.DataFrame:
    """Le e padroniza um arquivo de sensor."""
    dados = pd.read_csv(caminho)
    colunas_esperadas = {"numero", "data_hora", configuracao["coluna_valor"]}
    colunas_ausentes = colunas_esperadas.difference(dados.columns)
    if colunas_ausentes:
        raise ValueError(
            f"{caminho.name}: colunas ausentes: {sorted(colunas_ausentes)}"
        )

    dados = dados.rename(
        columns={
            "numero": "id_leitura",
            configuracao["coluna_valor"]: "valor",
        }
    )
    if "classificacao" not in dados.columns:
        dados["classificacao"] = pd.NA

    dados["id_leitura"] = pd.to_numeric(dados["id_leitura"], errors="coerce")
    dados["data_hora"] = pd.to_datetime(dados["data_hora"], errors="coerce")
    dados["valor"] = pd.to_numeric(dados["valor"], errors="coerce")
    dados["classificacao"] = dados["classificacao"].astype("string").str.strip()

    dados = dados.dropna(subset=["id_leitura", "data_hora", "valor"])
    dados = dados.drop_duplicates()
    dados["id_leitura"] = dados["id_leitura"].astype("int64")
    dados["sensor"] = configuracao["sensor"]
    dados["unidade"] = configuracao["unidade"]

    return dados[
        [
            "id_leitura",
            "data_hora",
            "sensor",
            "valor",
            "unidade",
            "classificacao",
        ]
    ].sort_values(["data_hora", "id_leitura"])


def processar_dados(
    pasta_bronze: Optional[Path] = None, pasta_silver: Optional[Path] = None
) -> pd.DataFrame:
    """Processa os sensores e grava arquivos individuais e consolidados."""
    raiz = localizar_projeto()
    pasta_bronze = pasta_bronze or raiz / "bronze" / "dados"
    pasta_silver = pasta_silver or raiz / "silver"
    pasta_silver.mkdir(parents=True, exist_ok=True)

    leituras = []
    for nome_arquivo, configuracao in CONFIGURACAO_SENSORES.items():
        caminho = pasta_bronze / nome_arquivo
        if not caminho.is_file():
            raise FileNotFoundError(f"Arquivo esperado nao encontrado: {caminho}")

        dados = tratar_arquivo(caminho, configuracao)
        dados.to_csv(
            pasta_silver / f"{configuracao['sensor']}.csv",
            index=False,
            date_format="%Y-%m-%d %H:%M:%S",
        )
        leituras.append(dados)

    consolidado = pd.concat(leituras, ignore_index=True).sort_values(
        ["data_hora", "sensor", "id_leitura"]
    )
    consolidado.to_csv(
        pasta_silver / "leituras_sensores.csv",
        index=False,
        date_format="%Y-%m-%d %H:%M:%S",
    )
    return consolidado


if __name__ == "__main__":
    resultado = processar_dados()
    print(f"{len(resultado)} leituras tratadas.")
    print("Arquivo consolidado: silver/leituras_sensores.csv")
