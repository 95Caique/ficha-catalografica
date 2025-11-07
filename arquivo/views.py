from io import BytesIO


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


from .forms import FichaForm

from reportlab.rl_config import defaultPageSize
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Frame


largura_pagina = defaultPageSize[0]
altura_pagina = defaultPageSize[1]


RECT_X_CM = 4.0
RECT_Y_CM = 5.5
RECT_W_CM = 13.5
RECT_H_CM = 7.5

# ATENÇÃO AQUI NESSE PONTO ELE QUE CONTROLA O QUADRADO DO PDF

CUTTER_OFFSET_CM = 0.6    # distância do topo do retângulo para o codigo cutter
INNER_H_PADDING_CM = 0.8  # aumentando esse campo ele move o texto da ficha para a direita
INNER_V_PADDING_CM = 1.2 # distancia entra o texto e o codigo cutter, se aumentar ele vai para baixo
DEFAULT_FONT = "Helvetica"

# ATENÇÃO AQUI NESSE PONTO ELE QUE CONTROLA O QUADRADO DO PDF



def index_ficha(request):
    if request.method != 'POST':
        form = FichaForm()
    else:
        form = FichaForm(request.POST)
        if form.is_valid():
            nova_ficha = form.save(commit=False)
            request = salvaInformacoes(request, nova_ficha)
            return HttpResponseRedirect('/ficha/')

    return render(request, 'index.html', {'form': form})


def salvaInformacoes(request, nova_ficha):
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
    request.session['fonte'] = getattr(nova_ficha, 'fonte', DEFAULT_FONT) or DEFAULT_FONT
    if request.session['fonte'].lower() == 'arial':
        request.session['fonte'] = 'Helvetica'
        request.session['tamanho_fonte'] = 10
    else:
        request.session['tamanho_fonte'] = 11 if request.session['fonte'].lower() != 'arial' else 10
    return request


def ficha(request):
    """
    Gera o PDF:
     - escreve cabeçalho acima do retângulo
     - desenha retângulo
     - escreve cutter
     - coloca conteúdo no Frame dentro do retângulo (Paragraphs)
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(largura_pagina, altura_pagina))

    p = escreveCabecalho(p, request)

    p.setLineWidth(0.1)
    p.rect(RECT_X_CM * cm, RECT_Y_CM * cm, RECT_W_CM * cm, RECT_H_CM * cm, stroke=1, fill=False)

    cutter_text = request.session.get('cutter', '') or ''
    cutter_x = (RECT_X_CM + 0.3) * cm
    cutter_y = (RECT_Y_CM + RECT_H_CM - CUTTER_OFFSET_CM) * cm
    fontname = request.session.get('fonte_usada', request.session.get('fonte', DEFAULT_FONT))
    fontsize = request.session.get('tamanho_fonte', 10)
    try:
        p.setFont(fontname, fontsize)
    except Exception:
        p.setFont(DEFAULT_FONT, fontsize)
        fontname = DEFAULT_FONT
    p.drawString(cutter_x, cutter_y, str(cutter_text))

    nome = processaNome(request)
    titulo = processaTitulo(request)
    trabalho = processaTrabalho(request)
    orientacao = processaOrientacao(request)
    coorientacao = processaCoorientacao(request)
    pista = processaPista(request)

    tipo_trabalho_info = (
        f"{request.session.get('tipo_trabalho','')} ({request.session.get('titulo_obtido','')}) - "
        f"{request.session.get('instituicao','')}, curso de {request.session.get('curso','')}."
    )
    referencias = f"Referências bibliográficas: f.{request.session.get('referencias','')}"
    anexos = f"Anexos: f.{request.session.get('anexos','')}"

    styles = getSampleStyleSheet()
    normal = ParagraphStyle(
        'FichaNormal',
        parent=styles['Normal'],
        fontName=fontname,
        fontSize=fontsize,
        leading=max(fontsize * 1.25, fontsize + 2),
        spaceAfter=4,
    )

    story = []
    story.append(Paragraph(nome, normal))
    story.append(Paragraph(titulo, normal))
    story.append(Paragraph(trabalho, normal))
    story.append(Paragraph(orientacao, normal))
    if coorientacao:
        story.append(Paragraph(coorientacao, normal))
    story.append(Paragraph(tipo_trabalho_info, normal))
    story.append(Paragraph(referencias, normal))
    story.append(Paragraph(anexos, normal))
    story.append(Paragraph(pista, normal))

    frame_x = (RECT_X_CM + INNER_H_PADDING_CM) * cm
    frame_y = (RECT_Y_CM + INNER_V_PADDING_CM) * cm
    frame_w = (RECT_W_CM - 2 * INNER_H_PADDING_CM) * cm
    frame_h = (RECT_H_CM - 2 * INNER_V_PADDING_CM) * cm

    frame = Frame(frame_x, frame_y, frame_w, frame_h, showBoundary=0)
    frame.addFromList(story, p)

    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="ficha-catalografica.pdf"'
    return response

from reportlab.pdfbase.ttfonts import TTFont

def processaNome(request):
    nome = f"{request.session.get('sobrenome','')}, {request.session.get('nome','')}"
    fontname = request.session.get('fonte_usada', request.session.get('fonte', DEFAULT_FONT))
    fontsize = request.session.get('tamanho_fonte', 10) or 10
    try:
        prefix_w = pdfmetrics.stringWidth(nome[:4], fontname, fontsize)
        global recuo
        recuo = prefix_w / cm
    except Exception:
        recuo = 0
    return nome


def processaTitulo(request):
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



def escreveCabecalho(draw_canvas, request):

    font_base = request.session.get('fonte_usada', request.session.get('fonte', DEFAULT_FONT))
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

    top_of_rect_y = (RECT_Y_CM + RECT_H_CM) * cm
    gap_above_rect = 1.0 * cm
    y1 = top_of_rect_y + gap_above_rect
    y2 = y1 - (fontsize * 1.1)

    x1 = (largura_pagina - largura1) / 2.0
    x2 = (largura_pagina - largura2) / 2.0

    draw_canvas.drawString(x1, y1, cabecalho1)
    draw_canvas.drawString(x2, y2, cabecalho2)

    try:
        draw_canvas.setFont(font_base, fontsize)
    except Exception:
        draw_canvas.setFont(DEFAULT_FONT, fontsize)

    return draw_canvas



def processaOrientacao(request):
    titulo = defineTitulo(request.session.get('titulo_orientador', ''), request.session.get('genero_orientador', ''))
    orientador_nome = request.session.get('orientador', '')
    if request.session.get('genero_orientador', '').lower() == 'masculino':
        orientacao = f"Orientador: Prof. {titulo} {orientador_nome}."
    else:
        orientacao = f"Orientadora: Profª. {titulo} {orientador_nome}."
    return orientacao


def processaCoorientacao(request):
    if not request.session.get('coorientador'):
        return ""
    titulo = defineTitulo(request.session.get('titulo_coorientador', ''), request.session.get('genero_coorientador', ''))
    coorientador_nome = request.session.get('coorientador', '')
    if request.session.get('genero_coorientador', '').lower() == 'masculino':
        return f"Coorientador: Prof. {titulo} {coorientador_nome}."
    else:
        return f"Coorientadora: Profª. {titulo} {coorientador_nome}."


def processaPista(request):
    pista = ""
    for i in range(1, 6):
        assunto = request.session.get(f'assunto{i}')
        if not assunto:
            break
        pista += str(i) + ". " + str(assunto) + ". "
    pista += "I. Título."
    return pista


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
