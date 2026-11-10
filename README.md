# 📊 Diagnóstico Aprofundado da Base PRF (2017–2025)
## Módulo de Ingestão, Cardinalidade e Tratamento de Ausências (Blocos 1 e 2)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.2%2B-150458?logo=pandas)
![PyArrow](https://img.shields.io/badge/PyArrow-Parquet-FF6F00)
![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen)

Documentação técnica do script programático de ingestão, auditoria relacional e higienização de dados referentes à **Atividade 2 (Diagnóstico Base PRF 2017–2025)** da disciplina de Estatística (UniFAP).

---

## 📌 Identificação do Desenvolvedor & Equipe

* **Equipe:** Data Mappers
* **Desenvolvedor Responsável:** David Watylla Tavares de Oliveira
* **Matrícula:** `20251180322`
* **Papel no Projeto:** Infraestrutura de Código, Pipeline de Ingestão e Tratamento Programático (Blocos 1 e 2)
* **Líder do Projeto:** Pedro Lino Paldini Alves
* **Analista:** José Guilherme de Souza Pereira
* **Pesquisadora:** Iany Alves Marques

---

## 🎯 Objetivos do Módulo

1. **Bloco 1 (Estrutura e Unidade de Análise):**
   * Realizar a ingestão automatizada e reprodutível dos 9 arquivos anuais intactos da PRF (2017 a 2025).
   * Contabilizar o volume bruto de linhas, acidentes únicos (`id`), veículos e pessoas/vítimas.
   * Testar computacionalmente a regra matemática de cardinalidade relacional:
     $$\text{Total de Pessoas (Linhas)} \ge \text{Total de Veículos Únicos} \ge \text{Total de Acidentes Únicos}$$

2. **Bloco 2 (Completude e Padronização de Nulos):**
   * Mapear e quantificar ausências explícitas (`NaN`) e mascaramentos implícitos (`"Ignorado"`, `"Não Informado"`, `"(null)"`, `"-"`, etc.).
   * Substituir todas as categorias de ausência mascarada por `np.nan` em uma cópia sanitizada do dataset.
   * Gerar o arquivo otimizado colunar (`.parquet`) para *handover* com a equipe de análise.

---

## 📂 Arquitetura de Diretórios do Projeto

```text
.
├── dados_prf_brutos/               # [Entrada] Arquivos CSV originais da PRF (2017 a 2025)
│   ├── acidentes2017_todas_causas_tipos.csv
│   ├── acidentes2018_todas_causas_tipos.csv
│   └── ... (até 2025)
├── relatorios_entregaveis/          # [Saída] Artefatos gerados pelo script
│   ├── bloco1_cardinalidade_metricas.csv
│   ├── bloco2_diagnostico_completude_bruta.csv
│   └── base_prf_2017_2025_nulos_padronizados.parquet
├── script_bloco1_2.py              # Pipeline principal em Python (Blocos 1 e 2)
├── organizar_zips.py               # Script utilitário para descompactação e organização
├── requirements.txt                # Dependências do ambiente Python
└── README.md                       # Documentação técnica do módulo
