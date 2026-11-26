"""Prepara os dados do survey e gera as evidências da coleta (Parte 2).

Lê as exportações brutas do Google Forms guardadas em ``privado/`` (pasta fora
do git, com e-mails) e gera, sem nenhum dado pessoal:

* docs/dados/respostas_pseudonimizadas.csv  base de análise (e-mail -> R001...)
* docs/dados/preteste_pseudonimizado.csv    respostas do pré-teste (PT1...)
* docs/dados/dicionario_dados.md            coluna -> item do protocolo
* docs/evidencias/exportacao_bruta_mascarada.csv  exportação com e-mail mascarado
* docs/evidencias/respostas_brutas.csv.sha256      hash do arquivo bruto
* docs/evidencias/relatorio_coleta.md       linha do tempo, contagens e descartes

Uso (na raiz do repositório):  python scripts/preparar_dados.py
Só usa a biblioteca padrão do Python.
"""

from __future__ import annotations

import csv
import hashlib
import math
import re
import subprocess
import sys
import unicodedata
from collections import Counter, OrderedDict
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRIVADO = RAIZ / "privado"
BRUTO = PRIVADO / "respostas_brutas.csv"
PRETESTE = PRIVADO / "preTeste.csv"
TERMOS_REDACAO = PRIVADO / "termos_redacao.txt"
DADOS = RAIZ / "docs" / "dados"
EVID = RAIZ / "docs" / "evidencias"
PROTOCOLO = "docs/Protocolo_Survey_IA_fora_de_TI.pdf"

# Item do protocolo -> trecho do cabeçalho exportado pelo Forms + escala.
ITENS = [
    ("timestamp", "carimbo de data/hora", "—"),
    ("email", "e-mail", "—"),
    ("C1", "li o termo", "Nominal"),
    ("T1", "18 anos", "Nominal"),
    ("T2", "atividade profissional", "Nominal"),
    ("T3", "area de ti?", "Nominal"),
    ("T4", "aluno(a) da disciplina", "Nominal"),
    ("P1", "area de atuacao principal", "Nominal"),
    ("P2", "tempo de experiencia", "Ordinal"),
    ("P3", "faixa etaria", "Ordinal"),
    ("P4", "escolaridade", "Ordinal"),
    ("P5", "vinculo de trabalho", "Nominal"),
    ("P6", "quantas pessoas trabalham", "Ordinal"),
    ("P7", "como voce chegou", "Nominal"),
    ("U1", "com que frequencia", "Ordinal"),
    ("U2", "quais ferramentas", "Nominal"),
    ("U3", "em quais tarefas", "Nominal"),
    ("U4", "ha quantos meses", "Razão"),
    ("U5", "quantas horas por semana", "Razão"),
    ("PP1", "[a ia me ajuda a concluir", "Ordinal"),
    ("PP2", "[com a ia, entrego", "Ordinal"),
    ("PP3", "[a ia reduz o esforco", "Ordinal"),
    ("PP4", "[usar ia no trabalho me faz perder", "Ordinal (inv.)"),
    ("CF1", "[confio nas informacoes", "Ordinal"),
    ("CF2", "[consigo usar as respostas", "Ordinal"),
    ("CF3", "[tenho receio", "Ordinal (inv.)"),
    ("N1", "por que voce nao usa", "Nominal"),
    ("N2", "pretendo usar ia", "Ordinal"),
    ("PR1", "[preocupo-me com a exposicao", "Ordinal"),
    ("PR2", "[preocupo-me que erros", "Ordinal"),
    ("PR3", "[preocupo-me com questoes eticas", "Ordinal"),
    ("AT1", "[para mostrar que esta lendo", "Ordinal"),
    ("PR4", "[considero seguro", "Ordinal (inv.)"),
    ("O1", "orientacao ou treinamento", "Nominal"),
    ("O2", "posicao da sua organizacao", "Nominal"),
    ("A1", "de um exemplo", "Nominal (codificada)"),
    ("A2", "quer comentar algo", "Nominal (codificada)"),
]
LIKERT_D5 = ["PP1", "PP2", "PP3", "PP4", "CF1", "CF2", "CF3", "PR1", "PR2", "PR3", "PR4"]
ABERTAS = ["A1", "A2"]

MOTIVOS = OrderedDict([
    ("D1", "Sem consentimento (C1)"),
    ("D2", "Não elegível na triagem (T1–T4)"),
    ("D3", "Errou a pergunta de atenção (AT1 ≠ “Discordo totalmente”)"),
    ("D4", "Duplicidade (mesmo e-mail; fica a primeira resposta)"),
    ("D5", "Mesma resposta em todos os itens Likert"),
])
TRIAGEM_TXT = {"T1": "menor de 18 anos", "T2": "sem atividade profissional",
               "T3": "atua em TI", "T4": "aluno da disciplina"}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(texto.lower().split())


def mapear_colunas(cabecalho: list[str]) -> dict[str, int]:
    norm = [normalizar(h) for h in cabecalho]
    mapa: dict[str, int] = {}
    for item, trecho, _ in ITENS:
        achados = [i for i, h in enumerate(norm) if trecho in h]
        if item == "email" and not achados:  # pré-teste usou "Nome de usuário"
            achados = [i for i, h in enumerate(norm) if "nome de usuario" in h]
        if len(achados) > 1:
            sys.exit(f"Cabeçalho ambíguo para {item}: {achados}")
        if achados:
            mapa[item] = achados[0]
    return mapa


def ler_csv(caminho: Path) -> tuple[list[str], list[list[str]]]:
    with caminho.open(encoding="utf-8-sig", newline="") as f:
        linhas = list(csv.reader(f))
    return linhas[0], linhas[1:]


def escrever_csv(caminho: Path, cabecalho: list[str], linhas: list[list[str]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows([cabecalho, *linhas])


def mascarar_email(email: str) -> str:
    email = email.strip()
    if "@" not in email:
        return ""
    local, dominio = email.split("@", 1)
    nome, _, resto = dominio.partition(".")
    return f"{local[:1]}•••@{nome[:1]}•••" + (f".{resto}" if resto else "")


def preparar_redacao():
    termos = []
    if TERMOS_REDACAO.exists():
        termos = [t.strip() for t in TERMOS_REDACAO.read_text(encoding="utf-8").splitlines() if t.strip()]
    padroes = [(re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[e-mail]"),
               (re.compile(r"(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}"), "[telefone]")]
    padroes += [(re.compile(rf"\b{re.escape(t)}\b", re.IGNORECASE), "[empresa]") for t in termos]

    def redigir(texto: str) -> str:
        for padrao, troca in padroes:
            texto = padrao.sub(troca, texto)
        return texto
    return redigir


def parse_data(texto: str) -> datetime:
    for fmt in ("%d/%m/%Y %H:%M:%S", "%Y/%m/%d %I:%M:%S %p GMT-3"):
        try:
            return datetime.strptime(texto.strip(), fmt)
        except ValueError:
            pass
    sys.exit(f"Data em formato inesperado: {texto!r}")


def commit_do_protocolo() -> tuple[str, str]:
    try:
        saida = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H|%ad", "--date=format:%d/%m/%Y %H:%M:%S %z",
             "--", PROTOCOLO], cwd=RAIZ, capture_output=True, text=True, check=True).stdout.strip()
        sha, data = saida.splitlines()[-1].split("|")
        return sha, data
    except Exception:  # noqa: BLE001 - relatório continua sem a linha do git
        return "", ""


def br(x: float, casas: int = 1) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def margem(n: int) -> float:
    return 1.96 * math.sqrt(0.25 / n) * 100 if n else float("nan")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not BRUTO.exists():
        sys.exit(f"Arquivo bruto não encontrado: {BRUTO.relative_to(RAIZ)}. "
                 "Copie a exportação do Google Forms para lá (pasta fora do git).")

    redigir = preparar_redacao()
    cab, linhas = ler_csv(BRUTO)
    col = mapear_colunas(cab)
    faltando = [i for i, *_ in ITENS if i not in col]
    if faltando:
        sys.exit(f"Colunas não encontradas na exportação: {faltando}")

    def v(linha: list[str], item: str) -> str:
        return linha[col[item]].strip() if item in col else ""

    # Pré-teste: só para pseudonimizar e cruzar participantes.
    emails_preteste: set[str] = set()
    pt_linhas_saida, pt_cab_saida, pt_datas = [], [], []
    if PRETESTE.exists():
        pt_cab, pt_linhas = ler_csv(PRETESTE)
        pt_col = mapear_colunas(pt_cab)
        pt_cab_saida = list(pt_cab)
        pt_cab_saida[pt_col["email"]] = "ID"
        for n, linha in enumerate(pt_linhas, 1):
            emails_preteste.add(linha[pt_col["email"]].strip().lower())
            pt_datas.append(parse_data(linha[pt_col["timestamp"]]))
            nova = list(linha)
            nova[pt_col["email"]] = f"PT{n}"
            for item in ABERTAS:
                if item in pt_col:
                    nova[pt_col[item]] = redigir(nova[pt_col[item]])
            pt_linhas_saida.append(nova)

    vistos: set[str] = set()
    registros = []  # (id, linha, motivo, detalhe)
    redigidas: list[str] = []
    veio_do_preteste: list[str] = []
    for n, linha in enumerate(linhas, 1):
        rid = f"R{n:03d}"
        email = v(linha, "email").lower()
        motivo, detalhe = "", ""
        if v(linha, "C1") != "Concordo":
            motivo = "D1"
        else:
            falhas = [t for t, ok in (("T1", v(linha, "T1") == "Sim"), ("T2", v(linha, "T2") == "Sim"),
                                      ("T3", v(linha, "T3") == "Não"), ("T4", v(linha, "T4") != "Sim")) if not ok]
            if falhas:
                motivo, detalhe = "D2", TRIAGEM_TXT[falhas[0]]
            elif v(linha, "AT1") != "Discordo totalmente":
                motivo = "D3"
            elif email in vistos:
                motivo = "D4"
            else:
                respostas = [v(linha, i) for i in LIKERT_D5 if v(linha, i)]
                if len(respostas) > 1 and len(set(respostas)) == 1:
                    motivo, detalhe = "D5", f"{len(respostas)} itens = “{respostas[0]}”"
        if email in emails_preteste:
            # Mantidos na amostra com autorização do professor (desvio do protocolo, seção 4).
            veio_do_preteste.append(rid + ("" if not motivo else f" (descartada por {motivo})"))
        vistos.add(email)
        for item in ABERTAS:
            original = linha[col[item]]
            limpo = redigir(original)
            if limpo != original:
                redigidas.append(f"{rid} ({item})")
            linha[col[item]] = limpo
        registros.append((rid, linha, motivo, detalhe))

    # --- Saídas de dados -------------------------------------------------
    cab_pseudo = list(cab)
    cab_pseudo[col["email"]] = "ID"
    cab_pseudo.append("Descarte")
    saida_pseudo = []
    saida_mascarada = []
    for rid, linha, motivo, _ in registros:
        p = list(linha)
        p[col["email"]] = rid
        saida_pseudo.append(p + [motivo])
        m = list(linha)
        m[col["email"]] = mascarar_email(linha[col["email"]])
        saida_mascarada.append(m)
    escrever_csv(DADOS / "respostas_pseudonimizadas.csv", cab_pseudo, saida_pseudo)
    escrever_csv(EVID / "exportacao_bruta_mascarada.csv", cab, saida_mascarada)
    if pt_linhas_saida:
        escrever_csv(DADOS / "preteste_pseudonimizado.csv", pt_cab_saida, pt_linhas_saida)

    sha = hashlib.sha256(BRUTO.read_bytes()).hexdigest()
    (EVID / "respostas_brutas.csv.sha256").write_text(f"{sha}  respostas_brutas.csv\n", encoding="utf-8", newline="\n")

    dic =["# Dicionário de dados", "",
           "Colunas de `respostas_pseudonimizadas.csv`, na ordem do arquivo, com o item correspondente "
           "na tabela de rastreabilidade do [protocolo](../Protocolo_Survey_IA_fora_de_TI.pdf) (seção 3).", "",
           "| # | Item | Escala | Cabeçalho exportado pelo Forms |", "|---|---|---|---|"]
    escalas = {i: e for i, _, e in ITENS}
    item_por_col = {c: i for i, c in col.items()}
    for c, h in enumerate(cab_pseudo):
        item = item_por_col.get(c, "—")
        if item == "email":
            item, h = "ID", "ID (código R001… no lugar do e-mail)"
        if h == "Descarte":
            item, h = "Descarte", "Descarte: código D1–D5 (vazio = resposta válida); coluna criada pelo script"
        dic.append(f"| {c + 1} | {item} | {escalas.get(item, '—')} | {' '.join(h.split())} |")
    (DADOS / "dicionario_dados.md").write_text("\n".join(dic) + "\n", encoding="utf-8", newline="\n")

    # --- Relatório -------------------------------------------------------
    datas = [parse_data(v(l, "timestamp")) for _, l, _, _ in registros]
    primeira, ultima = min(datas), max(datas)
    sha_prot, data_prot = commit_do_protocolo()
    contagem = Counter(m for _, _, m, _ in registros)
    validas = contagem.get("", 0)
    por_dia = Counter(d.strftime("%d/%m/%Y") for d in datas)
    canais = Counter(v(l, "P7") for _, l, _, _ in registros if v(l, "P7"))
    validos_ids = {rid for rid, _, m, _ in registros if not m}
    macro = Counter(v(l, "P1") for rid, l, _, _ in registros if rid in validos_ids)

    r = ["# Relatório de evidências da coleta", "",
         "Gerado por `scripts/preparar_dados.py` a partir da exportação bruta do Google Forms. "
         "Nenhum dado pessoal aparece aqui: os respondentes são identificados por código (R001…).", ""]

    r += ["## 1. Linha do tempo", "", "| Evento | Data e hora (GMT-3) | Prova |", "|---|---|---|"]
    if sha_prot:
        r.append(f"| Registro do protocolo (Parte 1) | {data_prot} | commit `{sha_prot[:7]}` "
                 f"(`{sha_prot}`) que adicionou `{PROTOCOLO}` |")
    if pt_datas:
        r.append(f"| Pré-teste ({len(pt_datas)} pessoas) | {min(pt_datas):%d/%m/%Y %H:%M:%S} a "
                 f"{max(pt_datas):%d/%m/%Y %H:%M:%S} | `docs/dados/preteste_pseudonimizado.csv` |")
    r.append(f"| Primeira resposta da coleta | {primeira:%d/%m/%Y %H:%M:%S} | "
             f"`exportacao_bruta_mascarada.csv`, linha 2 |")
    r.append(f"| Última resposta da coleta | {ultima:%d/%m/%Y %H:%M:%S} | `exportacao_bruta_mascarada.csv` |")
    if sha_prot:
        prot_dt = datetime.strptime(data_prot[:19], "%d/%m/%Y %H:%M:%S")
        horas = (primeira - prot_dt).total_seconds() / 3600
        situacao = "**antes**" if horas > 0 else "**DEPOIS (verificar!)**"
        r += ["", f"O protocolo foi registrado {situacao} da primeira resposta, com {br(abs(horas))} horas de "
              "antecedência. A data do commit também aparece no histórico do GitHub."]
    r += ["", "Período planejado no protocolo (seção 8): 13/11/2026 a 23/11/2026.", ""]

    r += ["## 2. Integridade da exportação bruta", "",
          f"- Arquivo bruto (privado, fora do git): `privado/respostas_brutas.csv`, "
          f"{len(registros)} respostas e {len(cab)} colunas.",
          f"- SHA-256: `{sha}`",
          "- O mesmo hash está em `respostas_brutas.csv.sha256`. Para conferir na apresentação: "
          "`cd privado && sha256sum -c ../docs/evidencias/respostas_brutas.csv.sha256` (Git Bash) ou "
          "`Get-FileHash privado/respostas_brutas.csv` (PowerShell).",
          "- `exportacao_bruta_mascarada.csv` tem as mesmas linhas, colunas, datas e horas do arquivo bruto. "
          "Só muda o e-mail, que aparece mascarado (ex.: j•••@g•••.com), como prevê a seção 6 do protocolo.", ""]

    r += ["## 3. Respostas por dia", "", "| Dia | Respostas |", "|---|---|"]
    r += [f"| {d} | {n} |" for d, n in sorted(por_dia.items(), key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"))]
    r += [f"| **Total** | **{len(registros)}** |", ""]

    r += ["## 4. Canal de chegada (P7)", "", "| Canal | Respostas |", "|---|---|"]
    r += [f"| {c} | {n} |" for c, n in canais.most_common()]
    r += ["", "Respostas encerradas na triagem não chegam à pergunta P7.", ""]

    r += ["## 5. Descartes (protocolo, seção 5.1)", "", "| Código | Motivo | Qtde. | Respostas |", "|---|---|---|---|"]
    for cod, txt in MOTIVOS.items():
        ids = [f"{rid}" + (f" ({d})" if d else "") for rid, _, m, d in registros if m == cod]
        r.append(f"| {cod} | {txt} | {len(ids)} | {', '.join(ids) or '—'} |")
    r += [f"| — | **Respostas válidas** | **{validas}** | |", "",
          f"- Recebidas: {len(registros)} · descartadas: {len(registros) - validas} · válidas: {validas}.",
          f"- Margem de erro com n = {validas} (95%, p = 0,5): ±{br(margem(validas))} pp.", ""]

    r += ["### Respostas válidas por área (P1)", "", "| Área informada | Válidas |", "|---|---|"]
    r += [f"| {a} | {n} |" for a, n in macro.most_common()]
    r.append("")

    r += ["## 6. Desvios e pontos de atenção", ""]
    if validas < 50:
        r.append(f"- **Mínimo não atingido:** {validas} respostas válidas, abaixo das 50 exigidas pelo enunciado "
                 "e da meta de 100 do protocolo.")
    if veio_do_preteste:
        r.append(f"- **Participantes do pré-teste na amostra:** {len(veio_do_preteste)} resposta(s) da coleta "
                 f"vieram de quem fez o pré-teste ({', '.join(veio_do_preteste)}). O protocolo (seção 4) previa "
                 "que essas pessoas não entrariam na amostra final, mas o professor autorizou que respondessem à "
                 "pesquisa final. As respostas foram mantidas. A resposta do pré-teste continua fora da base, e a "
                 "da coleta foi dada ao questionário já revisado.")
    if redigidas:
        r.append(f"- **Respostas abertas editadas:** {len(redigidas)} célula(s) com nome de empresa, e-mail ou "
                 f"telefone foram trocadas por marcadores como [empresa] ({', '.join(redigidas)}), "
                 "conforme a seção 6 do protocolo.")
    r.append(f"- Última resposta em {ultima:%d/%m/%Y}; o protocolo previa coleta até 23/11/2026.")
    r.append("")

    capturas = sorted(p.name for p in (EVID / "capturas").glob("*")
                      if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
    r += ["## 7. Outras evidências", "",
          f"- [{'x' if capturas else ' '}] Capturas de tela datadas da divulgação, em `docs/evidencias/capturas/` "
          f"({len(capturas)} arquivo(s)):"]
    r += [f"  - [`{c}`](capturas/{c})" for c in capturas]
    r += [
          "- [ ] Painel de respostas do Google Forms aberto ao vivo na apresentação, mostrando só a contagem e "
          "os gráficos, sem a lista de e-mails.",
          "- [ ] Comprovante de envio do protocolo no Canvas (opcional, reforça a data do commit).", ""]
    (EVID / "relatorio_coleta.md").write_text("\n".join(r) + "\n", encoding="utf-8", newline="\n")

    print(f"{len(registros)} respostas lidas; {validas} válidas; descartes: "
          + ", ".join(f"{k}={n}" for k, n in sorted(contagem.items()) if k))
    print(f"SHA-256 do bruto: {sha}")


if __name__ == "__main__":
    main()
