"""
===============================================================================
TDE ESTATÍSTICA - DIAGNÓSTICO APROFUNDADO DA BASE PRF (2017–2025)
===============================================================================
Perfil: Desenvolvedor (David Watylla Tavares de Oliveira - Matrícula: 20251180322)
Escopo: 
  - Bloco 1: Ingestão programática dos 9 arquivos, contagens brutas e teste 
             matemático de cardinalidade.
  - Bloco 2: Mapeamento e padronização de strings de ausência/nulos.
===============================================================================
"""

import os
import glob
import logging
from typing import Dict, Tuple, List
import pandas as pd
import numpy as np

# Configuração de Logging para reprodutibilidade e rastreabilidade
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# -----------------------------------------------------------------------------
# 1. MAPEAMENTO DE PADRÕES E CONFIGURAÇÕES
# -----------------------------------------------------------------------------

MISSING_STRINGS: List[str] = [
    "", " ", "  ", "ignorado", "não informado", "nao informado",
    "null", "(null)", "n/a", "na", "-", "--", "undefined"
]

POSSIBLE_ENCODINGS: List[str] = ["latin1", "iso-8859-1", "utf-8", "cp1252"]
POSSIBLE_DELIMITERS: List[str] = [";", ","]


# -----------------------------------------------------------------------------
# 2. BLOCO 1: FUNÇÕES DE INGESTÃO E CARDINALIDADE
# -----------------------------------------------------------------------------

def carregar_arquivo_prf(caminho_arquivo: str) -> pd.DataFrame:
    """
    Carrega um arquivo CSV da PRF tratando automaticamente codificações
    e delimitadores variáveis entre anos.
    """
    logging.info(f"Carregando: {os.path.basename(caminho_arquivo)}")
    
    for encoding in POSSIBLE_ENCODINGS:
        for sep in POSSIBLE_DELIMITERS:
            try:
                df = pd.read_csv(
                    caminho_arquivo,
                    sep=sep,
                    encoding=encoding,
                    low_memory=False,
                    dtype=str
                )
                if df.shape[1] > 1:
                    logging.info(
                        f"  -> Sucesso: {df.shape[0]} linhas, {df.shape[1]} colunas "
                        f"[Enc: {encoding} | Sep: '{sep}']"
                    )
                    return df
            except Exception:
                continue
                
    raise ValueError(f"Não foi possível ler o arquivo {caminho_arquivo} com os encodings/separadores testados.")


def carregar_base_completa(diretorio_dados: str) -> pd.DataFrame:
    """
    Consolida os 9 arquivos anuais (2017 a 2025) em um único DataFrame compilado.
    """
    padroes_busca = [
        os.path.join(diretorio_dados, "*.csv"),
        os.path.join(diretorio_dados, "datatran*.csv")
    ]
    
    arquivos = []
    for p in padroes_busca:
        arquivos.extend(glob.glob(p))
    arquivos = sorted(list(set(arquivos)))
    
    if len(arquivos) < 9:
        logging.warning(
            f"Encontrados {len(arquivos)} arquivos. O esperado são 9 arquivos (2017 a 2025)."
        )
    
    dfs = [carregar_arquivo_prf(f) for f in arquivos]
    df_bruto = pd.concat(dfs, ignore_index=True)
    
    logging.info(f"Consolidação concluída! Total bruto acumulado: {df_bruto.shape[0]} registros.")
    return df_bruto


def analisar_cardinalidade(df: pd.DataFrame) -> Dict[str, int]:
    """
    Bloco 1: Calcula contagens brutas e testa a regra matemática de cardinalidade:
    Total de Pessoas >= Total de Veículos >= Total de Acidentes Únicos (IDs).
    """
    total_linhas = len(df)
    
    col_id = next((c for c in df.columns if c.lower() in ['id', 'id_acidente']), None)
    col_veiculo = next((c for c in df.columns if c.lower() in ['id_veiculo', 'id_veiculo_prf', 'veiculo_id']), None)
    col_pessoa = next((c for c in df.columns if c.lower() in ['id_pessoa', 'id_pessoa_prf', 'pessoa_id']), None)
    
    unidade_analise = "Desconhecida"
    acidentes_unicos = df[col_id].nunique() if col_id else total_linhas
    veiculos_unicos = df[col_veiculo].nunique() if col_veiculo else 0
    pessoas_unicas = df[col_pessoa].nunique() if col_pessoa else total_linhas
    
    if col_pessoa and pessoas_unicas > 0:
        unidade_analise = "Pessoa por Acidente"
    elif col_veiculo and veiculos_unicos > 0:
        unidade_analise = "Veículo por Acidente"
    else:
        unidade_analise = "Acidente (Ocorrência Singular)"

    cardinalidade_valida = (pessoas_unicas >= veiculos_unicos >= acidentes_unicos) if (col_pessoa and col_veiculo) else True

    metricas = {
        "total_linhas_brutas": total_linhas,
        "acidentes_unicos": acidentes_unicos,
        "veiculos_unicos": veiculos_unicos,
        "pessoas_unicas": pessoas_unicas,
        "unidade_analise_detectada": unidade_analise,
        "regra_cardinalidade_valida": cardinalidade_valida
    }
    
    print("\n" + "="*70)
    print("RELATÓRIO DO BLOCO 1: ESTRUTURA E CARDINALIDADE BRUTA")
    print("="*70)
    print(f"• Total de Linhas Brutas:         {metricas['total_linhas_brutas']:,}")
    print(f"• Acidentes Únicos (ID Ocorrência): {metricas['acidentes_unicos']:,}")
    print(f"• Veículos Únicos Identificados:  {metricas['veiculos_unicos']:,}")
    print(f"• Pessoas/Vítimas Registradas:     {metricas['pessoas_unicas']:,}")
    print(f"• Unidade de Análise da Base:     {metricas['unidade_analise_detectada']}")
    print(f"• Regra N_Pessoas >= N_Veículos >= N_Acidentes: {'VALIDADA [OK]' if cardinalidade_valida else 'VIOLADA [ALERTA]'}")
    print("="*70 + "\n")
    
    return metricas


# -----------------------------------------------------------------------------
# 3. BLOCO 2: MAPEAMENTO E PADRONIZAÇÃO DE COMPLETUDE (NULOS)
# -----------------------------------------------------------------------------

def mapear_strings_ausencia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapeia todas as variantes de strings que indicam ausência de dados
    e contabiliza a frequência de ocorrência em cada coluna.
    """
    relatorio_ausencias = []
    
    for col in df.columns:
        serie_lower = df[col].astype(str).str.strip().str.lower()
        
        nulos_implicitos = serie_lower.isin(MISSING_STRINGS).sum()
        nulos_explicitos = df[col].isna().sum()
        
        total_nulos = nulos_implicitos + nulos_explicitos
        pct_nulos = (total_nulos / len(df)) * 100
        
        relatorio_ausencias.append({
            "coluna": col,
            "nulos_explicitos_np": nulos_explicitos,
            "nulos_implicitos_str": nulos_implicitos,
            "total_ausencias": total_nulos,
            "percentual_ausencia": round(pct_nulos, 2)
        })
        
    df_diagnostico = pd.DataFrame(relatorio_ausencias).sort_values(
        by="percentual_ausencia", ascending=False
    )
    return df_diagnostico


def padronizar_ausencias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bloco 2: Substitui todas as strings mascaradas de ausência por np.nan
    em uma cópia limpa da base de testes.
    """
    logging.info("Iniciando unificação e substituição de strings de ausência por np.nan...")
    df_clean = df.copy()
    
    for col in df_clean.select_dtypes(include=['object']):
        df_clean[col] = df_clean[col].astype(str).str.strip()
    
    padrao_regex = r'^(?i:' + '|'.join([r'\s*', 'ignorado', 'não informado', 'nao informado', 'null', r'\(null\)', 'n/a', 'na', '-', '--']) + r')$'
    
    df_clean = df_clean.replace(to_replace=padrao_regex, value=np.nan, regex=True)
    df_clean = df_clean.replace(to_replace=r'^\s*$', value=np.nan, regex=True)
    
    logging.info("Padronização de ausências finalizada com sucesso.")
    return df_clean


# -----------------------------------------------------------------------------
# 4. EXECUÇÃO PRINCIPAL E REPRODUTIBILIDADE
# -----------------------------------------------------------------------------

def executar_pipeline_desenvolvedor(diretorio_dados: str, diretorio_saida: str):
    """
    Executa o pipeline completo do Desenvolvedor (Blocos 1 e 2)
    e exporta as evidências para o relatório final.
    """
    os.makedirs(diretorio_saida, exist_ok=True)
    
    # 1. Carga dos dados (2017-2025)
    df_bruto = carregar_base_completa(diretorio_dados)
    
    # 2. Execução do Bloco 1 (Estrutura e Cardinalidade)
    metricas_cardinalidade = analisar_cardinalidade(df_bruto)
    pd.DataFrame([metricas_cardinalidade]).to_csv(
        os.path.join(diretorio_saida, "bloco1_cardinalidade_metricas.csv"), index=False
    )
    
    # 3. Execução do Bloco 2 - Mapeamento de Ausências
    df_diagnostico_nulos = mapear_strings_ausencia(df_bruto)
    df_diagnostico_nulos.to_csv(
        os.path.join(diretorio_saida, "bloco2_diagnostico_completude_bruta.csv"), index=False
    )
    
    print("="*70)
    print("RELATÓRIO DO BLOCO 2: DIAGNÓSTICO DE COMPLETUDE (TOP 10 COLUNAS COM MAIS AUSÊNCIAS)")
    print("="*70)
    print(df_diagnostico_nulos.head(10).to_string(index=False))
    print("="*70 + "\n")
    
    # 4. Execução do Bloco 2 - Gerar Base Tratada com Nulos Padronizados
    df_tratado = padronizar_ausencias(df_bruto)
    
    caminho_parquet = os.path.join(diretorio_saida, "base_prf_2017_2025_nulos_padronizados.parquet")
    try:
        df_tratado.to_parquet(caminho_parquet, index=False)
        logging.info(f"Base tratada com nulos padronizados salva em: {caminho_parquet}")
    except Exception:
        caminho_csv = os.path.join(diretorio_saida, "base_prf_2017_2025_nulos_padronizados.csv")
        df_tratado.to_csv(caminho_csv, index=False, sep=";")
        logging.info(f"Base tratada salva em CSV fallback em: {caminho_csv}")

    logging.info("Processamento do Desenvolvedor concluído com sucesso!")


if __name__ == "__main__":
    DIR_DADOS = "./dados_prf_brutos"
    DIR_SAIDA = "./relatorios_entregaveis"
    
    executar_pipeline_desenvolvedor(DIR_DADOS, DIR_SAIDA)