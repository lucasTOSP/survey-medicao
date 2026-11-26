# Relatório de evidências da coleta

Gerado por `scripts/preparar_dados.py` a partir da exportação bruta do Google Forms. Nenhum dado pessoal aparece aqui: os respondentes são identificados por código (R001…).

## 1. Linha do tempo

| Evento | Data e hora (GMT-3) | Prova |
|---|---|---|
| Registro do protocolo (Parte 1) | 12/11/2026 10:27:22 -0300 | commit `7ffa000` (`7ffa0005a191282caf54b6134d6fade0d4ed6051`) que adicionou `docs/Protocolo_Survey_IA_fora_de_TI.pdf` |
| Pré-teste (4 pessoas) | 11/11/2026 10:58:27 a 11/11/2026 11:50:16 | `docs/dados/preteste_pseudonimizado.csv` |
| Primeira resposta da coleta | 13/11/2026 10:17:24 | `exportacao_bruta_mascarada.csv`, linha 2 |
| Última resposta da coleta | 18/11/2026 19:28:37 | `exportacao_bruta_mascarada.csv` |

O protocolo foi registrado **antes** da primeira resposta, com 23,8 horas de antecedência. A data do commit também aparece no histórico do GitHub.

Período planejado no protocolo (seção 8): 13/11/2026 a 23/11/2026.

## 2. Integridade da exportação bruta

- Arquivo bruto (privado, fora do git): `privado/respostas_brutas.csv`, 62 respostas e 37 colunas.
- SHA-256: `f41207aa6e790efe86069542daa53b9f778bc2f80c995a84f1f8787e8c148192`
- O mesmo hash está em `respostas_brutas.csv.sha256`. Para conferir na apresentação: `cd privado && sha256sum -c ../docs/evidencias/respostas_brutas.csv.sha256` (Git Bash) ou `Get-FileHash privado/respostas_brutas.csv` (PowerShell).
- `exportacao_bruta_mascarada.csv` tem as mesmas linhas, colunas, datas e horas do arquivo bruto. Só muda o e-mail, que aparece mascarado (ex.: j•••@g•••.com), como prevê a seção 6 do protocolo.

## 3. Respostas por dia

| Dia | Respostas |
|---|---|
| 13/11/2026 | 33 |
| 14/11/2026 | 4 |
| 15/11/2026 | 4 |
| 16/11/2026 | 18 |
| 18/11/2026 | 3 |
| **Total** | **62** |

## 4. Canal de chegada (P7)

| Canal | Respostas |
|---|---|
| Whatsapp | 27 |
| Indicação pessoal | 25 |
| Outro | 1 |

Respostas encerradas na triagem não chegam à pergunta P7.

## 5. Descartes (protocolo, seção 5.1)

| Código | Motivo | Qtde. | Respostas |
|---|---|---|---|
| D1 | Sem consentimento (C1) | 0 | — |
| D2 | Não elegível na triagem (T1–T4) | 9 | R006 (sem atividade profissional), R025 (sem atividade profissional), R037 (atua em TI), R040 (sem atividade profissional), R041 (sem atividade profissional), R048 (sem atividade profissional), R055 (sem atividade profissional), R058 (atua em TI), R061 (menor de 18 anos) |
| D3 | Errou a pergunta de atenção (AT1 ≠ “Discordo totalmente”) | 0 | — |
| D4 | Duplicidade (mesmo e-mail; fica a primeira resposta) | 0 | — |
| D5 | Mesma resposta em todos os itens Likert | 2 | R009 (11 itens = “Concordo”), R027 (11 itens = “Nem concordo nem discordo”) |
| — | **Respostas válidas** | **51** | |

- Recebidas: 62 · descartadas: 11 · válidas: 51.
- Margem de erro com n = 51 (95%, p = 0,5): ±13,7 pp.

### Respostas válidas por área (P1)

| Área informada | Válidas |
|---|---|
| Comercial, vendas e marketing | 12 |
| Contabilidade, finanças e auditoria | 8 |
| Saúde | 8 |
| Agronegócio e meio ambiente | 6 |
| Engenharia, indústria e construção | 6 |
| Comunicação, design e artes | 3 |
| Administração, RH e gestão | 3 |
| Trabalho com contabilidade e estudo eng quimica | 1 |
| Serviço público | 1 |
| Projetos | 1 |
| Educação | 1 |
| Jurídico | 1 |

## 6. Desvios e pontos de atenção

- **Participantes do pré-teste na amostra:** 2 resposta(s) da coleta vieram de quem fez o pré-teste (R016, R026). O protocolo (seção 4) previa que essas pessoas não entrariam na amostra final, mas o professor autorizou que respondessem à pesquisa final. As respostas foram mantidas. A resposta do pré-teste continua fora da base, e a da coleta foi dada ao questionário já revisado.
- **Respostas abertas editadas:** 1 célula(s) com nome de empresa, e-mail ou telefone foram trocadas por marcadores como [empresa] (R020 (A1)), conforme a seção 6 do protocolo.
- Última resposta em 18/11/2026; o protocolo previa coleta até 23/11/2026.

## 7. Outras evidências

- [x] Capturas de tela datadas da divulgação, em `docs/evidencias/capturas/` (2 arquivo(s)):
  - [`2026-11-13_whatsapp-celular_lucas.png`](capturas/2026-11-13_whatsapp-celular_lucas.png)
  - [`2026-11-13_whatsapp-web_lucas.png`](capturas/2026-11-13_whatsapp-web_lucas.png)
- [ ] Painel de respostas do Google Forms aberto ao vivo na apresentação, mostrando só a contagem e os gráficos, sem a lista de e-mails.
- [ ] Comprovante de envio do protocolo no Canvas (opcional, reforça a data do commit).

