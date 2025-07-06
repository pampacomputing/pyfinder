from django.db import models

class Empresas(models.Model):
    cnpj_basico = models.TextField(primary_key=True)
    razao_social = models.TextField(blank=True, null=True)
    natureza_juridica = models.TextField(blank=True, null=True)
    qualificacao_responsavel = models.TextField(blank=True, null=True)
    porte_empresa = models.TextField(blank=True, null=True)
    ente_federativo_responsavel = models.TextField(blank=True, null=True)
    capital_social = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empresas'


class Socios(models.Model):
    cnpj = models.TextField(blank=True, null=True)
    cnpj_basico = models.TextField(blank=True, null=True)
    identificador_de_socio = models.TextField(blank=True, null=True)
    nome_socio = models.TextField(blank=True, null=True)
    cnpj_cpf_socio = models.TextField(primary_key=True)
    qualificacao_socio = models.TextField(blank=True, null=True)
    data_entrada_sociedade = models.TextField(blank=True, null=True)
    pais = models.TextField(blank=True, null=True)
    representante_legal = models.TextField(blank=True, null=True)
    nome_representante = models.TextField(blank=True, null=True)
    qualificacao_representante_legal = models.TextField(blank=True, null=True)
    faixa_etaria = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'socios'
