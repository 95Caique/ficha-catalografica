from io import BytesIO


from .forms import FichaForm


from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


from reportlab.rl_config import defaultPageSize
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

largura_pagina = defaultPageSize[0]
altura_pagina = defaultPageSize[1]

linhas = []
topo_res = 13
passada_vert = 0.45

esquerda = 6
recuo = 0

assuntos = []


def index_ficha(request):
    if request.method != 'POST':
        form = FichaForm()
    else:
        form = FichaForm(request.POST)
        if form.is_valid():
            nova_ficha = form.save(commit=False)
            request = salvaInformacoes(request, nova_ficha)
            return HttpResponseRedirect('/ficha/')

    context = {'form': form}
    return render(request, 'index.html', context)


def salvaInformacoes(request, nova_ficha):
    """Salva as informações do formulário para serem impressas na ficha"""
    request.session['nome'] = getattr(nova_ficha, 'nome', '') or ''
    request.session['sobrenome'] = getattr(nova_ficha, 'sobrenome', '') or ''
    request.session['cutter'] = getattr(nova_ficha, 'cutter', '') or ''
    request.session['titulo'] = getattr(nova_ficha, 'titulo', '') or ''
    request.session['sub_titulo'] = getattr(nova_ficha, 'sub_titulo', None)
    request.session['curso'] = getattr(nova_ficha, 'curso', '') or ''
    request.session['instituicao'] = getattr(nova_ficha, 'instituicao', '') or ''
    request.session['cidade'] = getattr(nova_ficha, 'cidade', '') or ''
    request.session['ano'] = getattr(nova_ficha, 'ano', '') or ''

    request.session['folhas'] = getattr(nova_ficha, 'folhas', '') or ''
    request.session['figuras'] = getattr(nova_ficha, 'figuras', '') or ''
    request.session['encardenacao'] = getattr(nova_ficha, 'encardenacao', '') or ''

    request.session['orientador'] = getattr(nova_ficha, 'orientador', '') or ''
    request.session['genero_orientador'] = getattr(nova_ficha, 'genero_orientador', '') or ''
    request.session['titulo_orientador'] = getattr(nova_ficha, 'titulo_orientador', '') or ''
    request.session['coorientador'] = getattr(nova_ficha, 'coorientador', None)
    request.session['genero_coorientador'] = getattr(nova_ficha, 'genero_coorientador', None)
    request.session['titulo_coorientador'] = getattr(nova_ficha, 'titulo_coorientador', None)

    request.session['referencias'] = getattr(nova_ficha, 'referencias', '') or ''
    request.session['anexos'] = getattr(nova_ficha, 'anexos', '') or ''

    for i in range(1, 6):
        request.session[f'assunto{i}'] = getattr(nova_ficha, f'assunto{i}', None)

    request.session['tipo_trabalho'] = getattr(nova_ficha, 'tipo_trabalho', '') or ''
    request.session['titulo_obtido'] = getattr(nova_ficha, 'titulo_obtido', '') or ''
    request.session['fonte'] = getattr(nova_ficha, 'fonte', 'Helvetica') or 'Helvetica'
    if request.session['fonte'].lower() == 'arial':
        request.session['fonte'] = 'Helvetica'
        request.session['tamanho_fonte'] = 10
    else:
        request.session['tamanho_fonte'] = 11 if request.session['fonte'].lower() != 'arial' else 10

    return request


def ficha(request):
    """Página onde o documento em pdf é gerado"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(largura_pagina, altura_pagina))

    # define fonte e salva nome real da fonte usada na sessão
    p = defineFonte(request, p)
    p = desenhaRetangulo(request, p)
    p = criaFicha(request, p)

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="ficha-catalografica.pdf"'
    return response


def defineFonte(request, draw_canvas):
    fonte = request.session.get('fonte', 'Helvetica') or 'Helvetica'
    tamanho = request.session.get('tamanho_fonte', 10) or 10

    fonte_lower = fonte.lower()
    if fonte_lower.startswith('times'):
        nome_font = "Times-Roman"
    elif fonte_lower.startswith('courier'):
        nome_font = "Courier"
    else:
        nome_font = "Helvetica"

    try:
        draw_canvas.setFont(nome_font, tamanho)
    except Exception:
        # fallback seguro
        nome_font = "Helvetica"
        draw_canvas.setFont(nome_font, tamanho)

    request.session['fonte_usada'] = nome_font
    request.session['tamanho_fonte'] = tamanho
    return draw_canvas


def desenhaRetangulo(request, draw_canvas):
    """Desenha o aquele retângulo padrão de ficha catalográfica"""
    draw_canvas.setLineWidth(0.1)
    draw_canvas.rect(4 * cm, 5.5 * cm, 13.5 * cm, 7.5 * cm, stroke=1, fill=False)
    return draw_canvas


def criaFicha(request, draw_canvas):
    """Realiza os passos necessários para construir a ficha catalográfica."""
    # Limpa a lista de linhas
    linhas.clear()

    nome = processaNome(request)
    pista = processaPista(request)
    cutter = processaCutter(request)
    titulo = processaTitulo(request)
    trabalho = processaTrabalho(request)
    orientacao = processaOrientacao(request)
    coorientacao = processaCoorientacao(request)

    linhas.append(nome)
    linhas.append(titulo)
    linhas.append(trabalho)
    linhas.append(orientacao)

    if coorientacao:
        linhas.append(coorientacao)

    tipo_trabalho_info = (
        f"{request.session.get('tipo_trabalho','')} ({request.session.get('titulo_obtido','')}) - "
        f"{request.session.get('instituicao','')}, curso de {request.session.get('curso','')}."
    )
    linhas.append(tipo_trabalho_info)

    linhas.append(f"Referências bibliográficas: f.{request.session.get('referencias','')}")
    linhas.append(f"Anexos: f.{request.session.get('anexos','')}")
    linhas.append(pista)

    draw_canvas = escreveCabecalho(draw_canvas, request)
    draw_canvas = escreveRodape(draw_canvas, request)
    draw_canvas = escreveCutter(draw_canvas, cutter)

    global topo_res
    topo_res = 12.3

    for i in range(len(linhas)):
        bloco = selecionaBloco(i, request)
        draw_canvas = escreveInformacoes(draw_canvas, bloco, i)

    topo_res = 12

    return draw_canvas


def processaNome(request):
    nome = f"{request.session.get('sobrenome','')}, {request.session.get('nome','')}"
    global recuo
    # usa pdfmetrics.stringWidth e o nome da fonte real (fonte_usada) para calcular pra não dar conflito na hora de escrever os dados na ficha
    fontname = request.session.get('fonte_usada', request.session.get('fonte', 'Helvetica'))
    fontsize = request.session.get('tamanho_fonte', 10) or 10
    largura_prefixo = pdfmetrics.stringWidth(nome[:4], fontname, fontsize)
    recuo = largura_prefixo / (cm)
    return nome


def processaPista(request):
    """Arruma o bloco de assuntos antes de imprimir na ficha"""
    pista = ""
    for i in range(1, 6):
        assunto = request.session.get(f'assunto{i}')
        if not assunto:
            break
        pista += str(i) + ". " + str(assunto) + ". "
    pista += "I. Título."
    return pista


def processaCutter(request):
    return request.session.get('cutter', '')


def selecionaCutter(nome, lista, i):
    nova_lista = []

    for tupla in lista:
        if i >= len(nome):
            return int(lista[0][1])

        if i >= len(tupla[0]):
            continue

        if nome[i] == tupla[0][i]:
            nova_lista.append(tupla)

    if nova_lista:
        return selecionaCutter(nome, nova_lista, i + 1)
    else:
        return lista[-1][1]


def processaTitulo(request):
    """Arruma o bloco de titulo antes de imprimir na ficha"""
    if not request.session.get('sub_titulo'):
        titulo = (
            f"{request.session.get('titulo','')} / "
            f"{request.session.get('nome','')} {request.session.get('sobrenome','')}. "
            f"{request.session.get('cidade','')} {request.session.get('ano','')}."
        )
    else:
        titulo = (
            f"{request.session.get('titulo','')}: {request.session.get('sub_titulo','')} / "
            f"{request.session.get('nome','')} {request.session.get('sobrenome','')}. "
            f"{request.session.get('cidade','')} {request.session.get('ano','')}."
        )
    return titulo


def processaTrabalho(request):
    """Define se existe ou não figuras antes de imprimir na ficha"""
    folhas = str(request.session.get('folhas', ''))
    texto = folhas + "f."
    if request.session.get('figuras') == 'Sim':
        texto += " il. "
    enc = request.session.get('encardenacao', '')
    if enc:
        texto += 'enc.' + enc.lower() + '. capa dura'
    else:
        texto += 'enc.'
    return texto


def processaOrientacao(request):
    """Processa as informações do orientador"""
    titulo = defineTitulo(request.session.get('titulo_orientador', ''), request.session.get('genero_orientador', ''))
    orientador_nome = request.session.get('orientador', '')
    if request.session.get('genero_orientador', '').lower() == 'masculino':
        orientacao = f"Orientador: Prof. {titulo} {orientador_nome}."
    else:
        orientacao = f"Orientadora: Profª. {titulo} {orientador_nome}."
    return orientacao


def processaCoorientacao(request):
    """Processa as informações do coorientador"""
    if not request.session.get('coorientador'):
        return ""

    titulo = defineTitulo(request.session.get('titulo_coorientador', ''), request.session.get('genero_coorientador', ''))
    coorientador_nome = request.session.get('coorientador', '')
    if request.session.get('genero_coorientador', '').lower() == 'masculino':
        return f"Coorientador: Prof. {titulo} {coorientador_nome}."
    else:
        return f"Coorientadora: Profª. {titulo} {coorientador_nome}."


def defineTitulo(titulo, genero):
    abreviacao = ""
    if titulo == 'Especialista':
        abreviacao = 'Esp.'
    elif titulo == 'Mestre':
        if genero == 'Masculino':
            abreviacao = 'Me.'
        else:
            abreviacao = 'Ma.'
    else:
        if genero == 'Masculino':
            abreviacao = 'Dr.'
        else:
            abreviacao = 'Dra.'
    return abreviacao


def selecionaBloco(index, request):
    """Seleciona o bloco de linhas correspondente"""
    linha = linhas[index]
    bloco = []
    para_prox_linha = ""
    linha_formatada = ""

    fontname = request.session.get('fonte_usada', request.session.get('fonte', 'Helvetica'))
    fontsize = request.session.get('tamanho_fonte', 10) or 10

    for i in range(0, len(linha)):
        linha_formatada += para_prox_linha
        para_prox_linha = ""
        linha_formatada += linha[i]
        largura = pdfmetrics.stringWidth(linha_formatada, fontname, fontsize) / cm
        if (largura >= 10.2):
            for j in range(len(linha_formatada) - 1, 0, -1):
                if linha_formatada[j] != ' ':
                    para_prox_linha = linha_formatada[j] + para_prox_linha
                    linha_formatada = linha_formatada[:-1]
                else:
                    break
            bloco.append(linha_formatada)
            linha_formatada = ""

    if linha_formatada is not None and linha_formatada != "":
        bloco.append(linha_formatada)

    return bloco


def escreveCabecalho(draw_canvas, request):
    """Escreve o cabeçalho da ficha"""
    font_base = request.session.get('fonte_usada', 'Helvetica')
    fontsize = request.session.get('tamanho_fonte', 10) or 10
    bold_candidate = font_base + '-Bold' if not font_base.endswith('-Bold') else font_base
    try:
        draw_canvas.setFont(bold_candidate, fontsize)
        font_to_use = bold_candidate
    except Exception:
        draw_canvas.setFont(font_base, fontsize)
        font_to_use = font_base

    cabecalho1 = "Ficha de identificação da obra elaborada pelo autor, através do"
    cabecalho2 = "Programa de Geração Automática do Sistema de Ficha Catalográfica"
    largura1 = pdfmetrics.stringWidth(cabecalho1, font_to_use, fontsize)
    largura2 = pdfmetrics.stringWidth(cabecalho2, font_to_use, fontsize)
    draw_canvas.drawString((largura_pagina - largura1) / 2, (topo_res + 2) * cm, cabecalho1)
    draw_canvas.drawString((largura_pagina - largura2) / 2, (topo_res + 1.5) * cm, cabecalho2)
    draw_canvas.setFont(font_base, fontsize)
    return draw_canvas


def escreveRodape(draw_canvas, request):
    """Escreve o rodapé da ficha caso tenha assuntos"""
    global assuntos
    reducao = 7.2
    passo = 0.5

    rodape = ""
    draw_canvas.drawString((esquerda - 1.5) * cm, (topo_res - reducao) * cm, rodape)
    assuntos = retornaAssuntos(request) if 'retornaAssuntos' in globals() else []
    reducao += passo
    return draw_canvas


def escreveCutter(draw_canvas, cutter_val):
    fontname = request_fontname_for_canvas(draw_canvas)
    fontsize = 10
    draw_canvas.setFont(fontname, fontsize)
    draw_canvas.drawString((esquerda) * cm, (topo_res - 0.5) * cm, str(cutter_val or ''))
    return draw_canvas


def escreveInformacoes(draw_canvas, bloco, index):
    fontname = request_fontname_for_canvas(draw_canvas)
    fontsize = 10
    draw_canvas.setFont(fontname, fontsize)


    global topo_res
    y = (topo_res - 3.5) * cm - index * (passada_vert * cm)
    if isinstance(bloco, list):
        for i, linha in enumerate(bloco):
            draw_canvas.drawString(esquerda * cm, y - i * (passada_vert * cm), linha)
    else:
        draw_canvas.drawString(esquerda * cm, y, str(bloco))
    return draw_canvas


def retornaAssuntos(request):
    ass = []
    for i in range(1, 6):
        val = request.session.get(f'assunto{i}')
        if val:
            ass.append(val)
    return ass


def request_fontname_for_canvas(draw_canvas):
    try:
        return draw_canvas._fontname
    except Exception:
        return 'Helvetica'
