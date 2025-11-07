from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Ficha(models.Model):

    FONTE = (
        ('Arial', 'Arial'),
        ('Times', 'Times New Roman'),
    )

    TIPO_TRABALHO = (
        ('Monografia', 'Monografia'),
        ('Dissertação', 'Dissertação'),
        ('Tese', 'Tese'),
        ('Tcc', 'TCC'),
        ('Produto Educacional', 'Produto Educacional'),
    )

    TEM_FIGURAS = (
   	    ('Sim', 'Sim'),
   	    ('Nao', 'Não'),
    )

    TITULO_OBTIDO = (
        ('Especialista', 'Especialista'),
        ('Bacharel', 'Bacharel'),
        ('Mestre', 'Mestre'),
        ('Doutor', 'Doutor'),
    )

    GENERO = (
        ('Masculino', 'Masculino'),
        ('Feminino', 'Feminino'),
    )

    TITULO_ORIENTADOR = (
        ('Especialista', 'Especialista'),
        ('Mestre', 'Mestre'),
        ('Doutor', 'Doutor'),
    )

    ENCARDENACAO = (
        ('Brochura', 'Brochura'),
        ('Espiral', 'Espiral'),
    )

    # Campos do modelo
    nome = models.CharField(max_length=300, default='')
    sobrenome = models.CharField(max_length=200, default='')
    cutter = models.CharField(max_length=20,default='',help_text='Clique no <a href="https://www.tabelacutter.com" t'
     'arget="_blank">link da Tabela Cutter</a> para gerar o Cutter e insira o valor gerado neste campo.')
    titulo = models.CharField(max_length=300, default='')
    sub_titulo = models.CharField(max_length=300, default='', blank=True, null=True)
    curso = models.CharField(max_length=300, default='')
    campus = models.CharField(max_length=300, default='')
    # Em Curso, tem que trazer o curso vinculado ao campus. Curso campus do suap, seguindo o template de exemplo https://fichacatalografica.ifmt.edu.br/
    instituicao = models.CharField(max_length=300,default='',verbose_name='Instituição')
    cidade = models.CharField(max_length=100, default='')
    ano = models.PositiveIntegerField(default='')
    folhas = models.PositiveIntegerField(default=1)
    figuras = models.CharField(max_length=20, choices=TEM_FIGURAS, default='Sim')
    referencias = models.PositiveIntegerField(default=1)
    anexos = models.PositiveIntegerField(default=1, blank=True, null=True)
    encardenacao = models.CharField(max_length=20, choices=ENCARDENACAO, default='Brochura')
    orientador = models.CharField(max_length=200, default='')
    genero_orientador = models.CharField(max_length=20, choices=GENERO, default='Masculino')
    titulo_orientador = models.CharField(max_length=50, choices=TITULO_ORIENTADOR, default='Mestre')
    coorientador = models.CharField(max_length=200, default='', blank=True, null=True)
    genero_coorientador = models.CharField(max_length=20, choices=GENERO, blank=True, null=True)
    titulo_coorientador = models.CharField(max_length=50, choices=TITULO_ORIENTADOR, blank=True, null=True)
    tipo_trabalho = models.CharField(max_length=19, choices=TIPO_TRABALHO, default='Monografia', verbose_name='Tipo do Trabalho' )
    titulo_obtido = models.CharField(max_length=15, choices=TITULO_OBTIDO, default='Bacharelado')
    assunto1 = models.CharField(max_length=100, default='Curso X',)
    assunto2 = models.CharField(max_length=100, default='', blank=True, null=True)
    assunto3 = models.CharField(max_length=100, default='', blank=True, null=True)
    assunto4 = models.CharField(max_length=100, default='', blank=True, null=True)
    assunto5 = models.CharField(max_length=100, default='', blank=True, null=True)
    fonte = models.CharField(max_length=15, choices=FONTE, default='Times')
    tamanho_fonte = models.PositiveIntegerField(validators=[MaxValueValidator(14), MinValueValidator(9)], default=11)
    # created_at = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return f'{self.titulo} - {self.nome} {self.sobrenome}'

