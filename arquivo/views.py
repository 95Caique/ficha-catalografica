from django.urls import reverse
from reportlab.rl_config import defaultPageSize



largura_pagina = defaultPageSize[0]
altura_pagina = defaultPageSize[1]

linhas = []
topo_res = 12
passada_vert = 0.45

esquerda = 6
recuo = 0

assuntos = []


def index_ficha(request):
    """A página inicial do app Fichas Catalográficas"""
    if request.method != 'POST':
        # Requisição GET: abre formulário em branco
        form = FichaForm()
    else:
        # Requisição POST: Dados do formulário são processados
        form = FichaForm(request.POST)
        if form.is_valid():
            nova_ficha = form.save(commit=False)
            request = salvaInformacoes(request, nova_ficha)
            return HttpResponseRedirect(reverse('fichas:ficha'))

    context = {'form': form}
    return render(request, 'index.html', context)


def salvaInformacoes(request, nova_ficha):
    """Salva as informações do formulário para serem impressas na ficha"""
    request.session['nome'] = nova_ficha.nome
    request.session['sobrenome'] = nova_ficha.sobrenome
    request.session['cutter'] = nova_ficha.cutter
    request.session['titulo'] = nova_ficha.titulo
    request.session['sub_titulo'] = nova_ficha.sub_titulo
    request.session['curso'] = nova_ficha.curso
    request.session['instituicao'] = nova_ficha.instituicao
    request.session['cidade'] = nova_ficha.cidade
    request.session['ano'] = nova_ficha.ano

    request.session['folhas'] = nova_ficha.folhas
    request.session['figuras'] = nova_ficha.figuras
    # request.session['encardenacao'] = nova_ficha.encardenacao

    request.session['orientador'] = nova_ficha.orientador
    request.session['genero_orientador'] = nova_ficha.genero_orientador
    request.session['titulo_orientador'] = nova_ficha.titulo_orientador
    request.session['coorientador'] = nova_ficha.coorientador
    request.session['genero_coorientador'] = nova_ficha.genero_coorientador
    request.session['titulo_coorientador'] = nova_ficha.titulo_coorientador

    # request.session['referencias'] = nova_ficha.referencias
    # request.session['anexos'] = nova_ficha.anexos

    request.session['assunto1'] = nova_ficha.assunto1
    request.session['assunto2'] = nova_ficha.assunto2
    request.session['assunto3'] = nova_ficha.assunto3
    request.session['assunto4'] = nova_ficha.assunto4
    request.session['assunto5'] = nova_ficha.assunto5

    request.session['tipo_trabalho'] = nova_ficha.tipo_trabalho
    request.session['titulo_obtido'] = nova_ficha.titulo_obtido
    request.session['fonte'] = nova_ficha.fonte
    if nova_ficha.fonte == 'Arial':
        request.session['tamanho_fonte'] = 10
    else:
        request.session['tamanho_fonte'] = 11

    return request


def ficha(request):
    """Página onde o documento em pdf é gerado"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="ficha-catalográfica.pdf"'
    print(f'request: {request} data: {request.POST}' )

    draw_canvas = canvas.Canvas(response)

    draw_canvas = defineFonte(request, draw_canvas)
    draw_canvas = desenhaRetangulo(request, draw_canvas)
    draw_canvas = criaFicha(request, draw_canvas)

    draw_canvas.showPage()
    draw_canvas.save()
    return response


def defineFonte(request, draw_canvas):
    """Define a fonte da ficha"""
    monospace_font = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
    arial_font = "/usr/share/fonts/truetype/msttcorefonts/arial.ttf"
    arial_bold_font = "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf"
    times_font = "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf"
    times_bold_font = "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman_Bold.ttf"

    pdfmetrics.registerFont(TTFont('Monospace', monospace_font))
    pdfmetrics.registerFont(TTFont('Arial', arial_font))
    pdfmetrics.registerFont(TTFont('Arial_Bold', arial_bold_font))
    pdfmetrics.registerFont(TTFont('Times', times_font))
    pdfmetrics.registerFont(TTFont('Times_Bold', times_bold_font))

    if request.session.get('fonte') == 'Times':
       draw_canvas.setFont('Times-Roman', request.session.get('tamanho_fonte', 10))
    elif request.session.get('fonte') == 'Arial':
       draw_canvas.setFont('arial', request.session.get('tamanho_fonte', 10))
    else:
       draw_canvas.setFont('Monospace', request.session.get('tamanho_fonte', 10))
    return draw_canvas


def desenhaRetangulo(request, draw_canvas):
    """Desenha o retângulo padrão de ficha catalográfica"""
    draw_canvas.setLineWidth(0.1)
    draw_canvas.rect(4 * cm, 5.5 * cm, 13.5 * cm, 7.5 * cm, stroke=1, fill=False)
    return draw_canvas


def criaFicha(request, draw_canvas):
    """Realiza os passos necessários para construir a ficha catalográfica."""
    # Limpa a lista de linhas
    linhas.clear()

    # Pré-processamento das informações
    nome = processaNome(request)
    pista = processaPista(request)
    cutter = processaCutter(request)
    titulo = processaTitulo(request)
    trabalho = processaTrabalho(request)
    orientacao = processaOrientacao(request)
    coorientacao = processaCoorientacao(request)

    # Processamento das informações
    linhas.append(nome)
    linhas.append(titulo)
    linhas.append(trabalho)
    linhas.append(orientacao)

    # Adiciona coorientação se não estiver vazia
    if coorientacao:
        linhas.append(coorientacao)

    # Monta a linha com informações sobre tipo de trabalho
    tipo_trabalho_info = (
        f"{request.session['tipo_trabalho']} ({request.session['titulo_obtido']}) - "
        f"{request.session['instituicao']}, curso de {request.session['curso']}."
    )
    linhas.append(tipo_trabalho_info)

    # Adiciona referências e anexos
    linhas.append(f"Referências bibliográficas: f.{request.session['referencias']}")
    linhas.append(f"Anexos: f.{request.session['anexos']}")
    linhas.append(pista)

    # Impressão das informações na ficha
    draw_canvas = escreveCabecalho(draw_canvas, request)
    draw_canvas = escreveRodape(draw_canvas, request)
    draw_canvas = escreveCutter(draw_canvas, cutter)

    global topo_res
    topo_res = 12.3

    for i in range(len(linhas)):
        draw_canvas = escreveInformacoes(draw_canvas, selecionaBloco(i, request), i)

    topo_res = 12

    return draw_canvas


def processaNome(request):
    """Arruma o bloco de nome antes de imprimir na ficha"""
    nome = request.session['sobrenome'] + ", " + request.session['nome']

    global recuo
    recuo = stringWidth(nome[:4], request.session['fonte'], request.session.get('tamanho_fonte', 10)) / cm
    return nome


def processaPista(request):
    """Arruma o bloco de assuntos antes de imprimir na ficha"""
    pista = ""
    for i in range(1, 6):
        if request.session['assunto' + str(i)] is None:
            break
        pista += str(i) + ". " + request.session['assunto' + str(i)] + ". "
    pista += "I. Título."
    return pista

def processaCutter(request):
    """Retorna o valor do cutter armazenado na sessão."""
    return request.session.get('cutter')

def selecionaCutter(nome, lista, i):
    """Função recursiva que seleciona o par chave - valor correto."""
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
    titulo = ""
    if request.session['sub_titulo'] is None:
        titulo = (
            request.session['titulo'] + " / " +
            request.session['nome'] + " " +
            request.session['sobrenome'] + ". " +
            request.session['cidade'] + " " +  # Adicione um espaço aqui
            str(request.session['ano']) + "."
        )
    else:
        titulo = (
            request.session['titulo'] + ": " +
            request.session['sub_titulo'] + " / " +
            request.session['nome'] + " " +
            request.session['sobrenome'] + ". " +
            request.session['cidade'] + " " +
            str(request.session['ano']) + "."
        )
    return titulo


def processaTrabalho(request):
    """Define se existe ou não figuras antes de imprimir na ficha"""
    figuras = str(request.session['folhas']) + "f."
    if request.session['figuras'] == 'Sim':
        figuras += " il. "
    figuras += 'enc.' + request.session['encardenacao'].lower() + '. capa dura'
    return figuras


def processaOrientacao(request):
    """Processa as informações do orientador"""
    orientacao = ""
    titulo = defineTitulo(request.session['titulo_orientador'], request.session['genero_orientador'])

    if request.session['genero_orientador'] == 'Masculino':
        orientacao = "Orientador: Prof. " + titulo + " " + request.session['orientador'] + "."
    else:
        orientacao = "Orientadora: Profª. " + titulo + " " + request.session['orientador'] + "."
    return orientacao


def processaCoorientacao(request):
    """Processa as informações do coorientador"""
    if request.session['coorientador'] is None:
        return ""

    coorientacao = ""
    titulo = defineTitulo(request.session['titulo_coorientador'], request.session['genero_coorientador'])

    if request.session['genero_coorientador'] == 'Masculino':
        coorientacao = "Coorientador: Prof. " + titulo + " " + request.session['coorientador'] + "."
    else:
        coorientacao = "Coorientadora: Profª. " + titulo + " " + request.session['coorientador'] + "."
    return coorientacao


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

    for i in range(0, len(linha)):
        linha_formatada += para_prox_linha
        para_prox_linha = ""
        linha_formatada += linha[i]
        largura = stringWidth(linha_formatada, request.session['fonte'], request.session.get('tamanho_fonte', 10)) / cm
        if (largura >= 10.2):
            for j in range(len(linha_formatada) - 1, 0, -1):
                if linha_formatada[j] != ' ':
                    para_prox_linha = linha_formatada[j] + para_prox_linha
                    linha_formatada = linha_formatada[:-1]
                else:
                    break
            bloco.append(linha_formatada)
            linha_formatada = ""

    if linha_formatada is not None:
        bloco.append(linha_formatada)

    return bloco


def escreveCabecalho(draw_canvas, request):
    """Escreve o cabeçalho da ficha"""
    draw_canvas.setFont(request.session['fonte'] + '_Bold', request.session.get('tamanho_fonte', 10))
    cabecalho1 = "Ficha de identificação da obra elaborada pelo autor, através do"
    cabecalho2 = "Programa de Geração Automática do Sistema Integrado de Bibliotecas do IF Goiano - SIBi"
    largura1 = stringWidth(cabecalho1, request.session['fonte'], request.session.get('tamanho_fonte', 10))
    largura2 = stringWidth(cabecalho2, request.session['fonte'], request.session.get('tamanho_fonte', 10))
    draw_canvas.drawString((largura_pagina - largura1) / 2, (topo_res + 2) * cm, cabecalho1)
    draw_canvas.drawString((largura_pagina - largura2) / 2, (topo_res + 1.5) * cm, cabecalho2)
    draw_canvas.setFont(request.session['fonte'], request.session.get('tamanho_fonte', 10))
    return draw_canvas


def escreveRodape(draw_canvas, request):
    """Escreve o rodapé da ficha"""
    global assuntos
    reducao = 7.2
    passo = 0.5

    rodape = ""
    draw_canvas.drawString((esquerda - 1.5) * cm, (topo_res - reducao) * cm, rodape)
    assuntos = retornaAssuntos(request)
    reducao += passo
