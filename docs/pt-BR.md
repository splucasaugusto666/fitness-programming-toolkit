# Fitness Programming Toolkit — validação de fichas de treino em Python

[English README](../README.md) · [API Python](API.md) · [Formato JSON](FORMAT.md)

FPTK é uma biblioteca Python e ferramenta de linha de comando open source para validar
fichas de musculação estruturadas em JSON, calcular séries e repetições planejadas
e exportar dados para CSV. Funciona offline, sem dependências de produção.

É útil para desenvolvedores de sistemas de academia, aplicativos de treino e
integrações de personal trainers que precisam conferir a estrutura de dados antes
de importá-los. Não prescreve exercícios, não avalia segurança fisiológica e não
é um sistema de prontuário. Use somente dados sintéticos em contribuições públicas.

## Instalação e exemplo reproduzível

Requer Python 3.11 ou superior. A documentação descreve a branch main,
incluindo melhorias ainda não lançadas em uma release.

```sh
git clone https://github.com/splucasaugusto666/fitness-programming-toolkit.git
cd fitness-programming-toolkit
python -m pip install -e .
fptk validate examples/ficha_treino_ptbr.json
fptk summary examples/ficha_treino_ptbr.json
fptk export-csv examples/ficha_treino_ptbr.json --output ficha.csv
```

A [ficha sintética](../examples/ficha_treino_ptbr.json) tem 1 sessão semanal,
3 séries e 28 repetições semanais. Em quatro semanas são 4 sessões, 12 séries
e 112 repetições planejadas. Os comandos não avaliam a qualidade do treino.

## Integração com software de academia

```python
from fitness_programming_toolkit import DataValidationError, read_program, summarize_program

try:
    plan = read_program("examples/ficha_treino_ptbr.json")
    print(summarize_program(plan)["planned_sets"])  # 12
except (DataValidationError, OSError) as error:
    print(f"Falha na importação: {error}")
```

Valide a estrutura com o [JSON Schema 2020-12](../schemas/program-1.0.schema.json)
e confira as [restrições adicionais](FORMAT.md#explicit-limits-of-parity).
O formato usa nomes de campos e dias da semana em inglês; títulos e nomes
de exercícios podem conter caracteres Unicode válidos, incluindo acentos.
Não há conversores diretos para formatos de terceiros nesta versão.

## Exportação CSV e desempenho

O CSV tem cabeçalho estável, UTF-8 e CRLF. A CLI grava em arquivo temporário antes
de publicar o destino; consulte os limites de filesystem em [QUICKSTART](QUICKSTART.md).
A mitigação de fórmulas em texto não é uma garantia contra todos os modos de
importação de planilhas. O [benchmark reproduzível](BENCHMARKS.md) mede a redução
de alocações Python na exportação em streaming em relação à própria versão anterior.

Para contribuir, leia [CONTRIBUTING.md](../CONTRIBUTING.md) ou
[relate um problema reproduzível](https://github.com/splucasaugusto666/fitness-programming-toolkit/issues).

## Integração com inteligência artificial

O [guia de integração com IA](AI_INTEGRATIONS.md) apresenta chamadas de ferramentas
para OpenAI, Claude, Gemini e APIs compatíveis, além do servidor MCP local opcional.
O núcleo continua offline e sem dependências obrigatórias. A validação é estrutural,
não uma prescrição de treino nem certificação clínica. As APIs comerciais podem cobrar
pelo uso dos modelos; o processamento local não precisa de chave de API.

Para facilitar a conexão com clientes MCP locais, instale o extra em um ambiente virtual e gere a configuração com `fptk-ai mcp-config claude-desktop`, `fptk-ai mcp-config cursor` ou `fptk-ai mcp-config vscode`. Mescle a entrada no cliente manualmente. O comando não altera configurações, não inicia servidores e não conecta automaticamente aplicativos hospedados na nuvem.
