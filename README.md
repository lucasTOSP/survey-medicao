# Uso de IA por profissionais de áreas fora de TI: survey pré-registrado

Trabalho final de **Medição e Experimentação em Engenharia de Software** (PUC Minas, 2º/2026).
O survey investiga com que frequência, com quais ferramentas e para quais tarefas profissionais de fora de TI usam IA generativa no trabalho, e como avaliam produtividade, confiança e riscos.

**Integrantes:** Arthur Candian, Arthur Henrique Santana Pedra, Cauê Afonso Moraes, Lucas Ferreira Ribeiro e Vitor Veiga Silva.

## Dashboard

- [Dashboard no Looker Studio](https://datastudio.google.com/reporting/1509ac7f-8190-41c0-b292-4dbf4369ae7b/page/p_lklrnc0m9d/edit)
- [`index.html`](index.html): página que incorpora o dashboard em tela cheia.

## Linha do tempo

| Etapa | Data | Evidência |
|---|---|---|
| Pré-teste com 4 pessoas | 11/11/2026 | [`docs/dados/preteste_pseudonimizado.csv`](docs/dados/preteste_pseudonimizado.csv) |
| Registro do protocolo (Parte 1) | 12/11/2026 10:27 | commit [`7ffa000`](https://github.com/lucasTOSP/survey-medicao/commit/7ffa0005a191282caf54b6134d6fade0d4ed6051) |
| Primeira resposta | 13/11/2026 10:17 | [`docs/evidencias/exportacao_bruta_mascarada.csv`](docs/evidencias/exportacao_bruta_mascarada.csv) |
| Última resposta | 18/11/2026 19:28 | mesmo arquivo |

O protocolo foi publicado cerca de 24 horas antes da primeira resposta.

## Situação da coleta

| | |
|---|---|
| Respostas recebidas | 62 |
| Descartadas | 11: 9 na triagem (D2) e 2 com a mesma resposta em todos os itens Likert (D5) |
| **Válidas** | **51** (margem de erro de ±13,7 pp com 95% de confiança) |

Os descartes estão detalhados por código e motivo no [relatório de evidências](docs/evidencias/relatorio_coleta.md).

## Evidências da coleta (Parte 2)

| O que o enunciado pede | Onde está |
|---|---|
| Protocolo registrado antes da coleta, com data comprovada | [`docs/Protocolo_Survey_IA_fora_de_TI.pdf`](docs/Protocolo_Survey_IA_fora_de_TI.pdf) e commit `7ffa000` |
| Exportação bruta com data e hora de cada resposta | [`docs/evidencias/exportacao_bruta_mascarada.csv`](docs/evidencias/exportacao_bruta_mascarada.csv): mesmas linhas e horários do export do Google Forms, com o e-mail mascarado (ex.: `j•••@g•••.com`) |
| Prova de que o export não foi alterado | [`docs/evidencias/respostas_brutas.csv.sha256`](docs/evidencias/respostas_brutas.csv.sha256): SHA-256 do arquivo bruto original, que pode ser conferido ao vivo |
| Capturas datadas dos canais de divulgação | [`docs/evidencias/capturas/`](docs/evidencias/capturas/README.md): prints do WhatsApp de 13/11/2026 com a mensagem-padrão e o link (nomes de terceiros cobertos) |
| Painel do formulário durante a apresentação | Google Forms, aba Respostas, mostrando só os resumos (sem a lista de e-mails) |
| Descartes e motivos | [`docs/evidencias/relatorio_coleta.md`](docs/evidencias/relatorio_coleta.md) e coluna `Descarte` da base |

Nenhum arquivo do repositório contém e-mail completo ou outro dado pessoal dos respondentes.

## Estrutura

```
docs/
  Protocolo_Survey_IA_fora_de_TI.pdf   protocolo da Parte 1 (pré-registro)
  dados/
    respostas_pseudonimizadas.csv      base de análise: e-mail trocado por R001…, coluna Descarte
    preteste_pseudonimizado.csv        respostas do pré-teste (PT1–PT4), fora da amostra
    dicionario_dados.md                coluna -> item do questionário (C1, T1, PP1…) e escala
  evidencias/
    relatorio_coleta.md                linha do tempo, respostas por dia, canais, descartes, desvios
    exportacao_bruta_mascarada.csv     export do Forms com e-mail mascarado
    respostas_brutas.csv.sha256        hash do export original
    capturas/                          prints datados da divulgação
scripts/
  preparar_dados.py                    gera todos os arquivos de docs/dados e docs/evidencias
index.html                             dashboard incorporado
privado/                               (fora do git) exports originais com e-mails
```

## Como regenerar os dados

1. Exporte as respostas do Google Forms em CSV e salve como `privado/respostas_brutas.csv`. A pasta `privado/` está no `.gitignore`.
2. Opcional: coloque o export do pré-teste em `privado/preTeste.csv` e, em `privado/termos_redacao.txt`, os nomes de empresas a remover das respostas abertas (um por linha).
3. Na raiz do repositório, rode:

   ```bash
   python scripts/preparar_dados.py
   ```

O script usa só a biblioteca padrão do Python 3. Ele aplica os descartes D1–D5 do protocolo (seção 5.1) e reescreve os arquivos de `docs/dados/` e `docs/evidencias/`.

Para conferir se o arquivo bruto é o mesmo que gerou as evidências:

```bash
cd privado && sha256sum -c ../docs/evidencias/respostas_brutas.csv.sha256
```

## Desvios em relação ao protocolo

- **Participantes do pré-teste na amostra:** o protocolo (seção 4) dizia que quem fez o pré-teste não entraria na amostra final. Duas dessas pessoas também responderam à coleta, com autorização do professor, e foram mantidas. As respostas do pré-teste continuam fora da base.
- **Amostra abaixo da meta:** são 51 respostas válidas, acima do mínimo de 50 do enunciado, mas abaixo da meta de 100 do protocolo. Por isso a margem de erro é de ±13,7 pp, e não de ±9,8 pp.
- **Coleta encerrada antes do previsto:** a última resposta chegou em 18/11, e o protocolo previa coleta até 23/11.

## Privacidade (LGPD)

A tabela que liga cada código ao e-mail fica fora do repositório, com acesso restrito, e será apagada em até 30 dias após o fim da disciplina (protocolo, seção 6).
Nomes de empresas citados nas respostas abertas são trocados por `[empresa]`.

## Licença

[MIT](LICENSE)
