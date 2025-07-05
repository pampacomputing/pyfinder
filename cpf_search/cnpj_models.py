from django.db import models

class Empresas(models.Model):
    cnpj = models.TextField(primary_key=True)
    razao_social = models.TextField(blank=True, null=True)
    nome_fantasia = models.TextField(blank=True, null=True)
    situacao_cadastral = models.TextField(blank=True, null=True)
    data_situacao_cadastral = models.TextField(blank=True, null=True)
    motivo_situacao_cadastral = models.TextField(blank=True, null=True)
    cod_nat_juridica = models.TextField(blank=True, null=True)
    data_inicio_ativ = models.TextField(blank=True, null=True)
    cnae_fiscal = models.TextField(blank=True, null=True)
    tipo_logradouro = models.TextField(blank=True, null=True)
    logradouro = models.TextField(blank=True, null=True)
    numero = models.TextField(blank=True, null=True)
    complemento = models.TextField(blank=True, null=True)
    bairro = models.TextField(blank=True, null=True)
    cep = models.TextField(blank=True, null=True)
    uf = models.TextField(blank=True, null=True)
    cod_municipio = models.TextField(blank=True, null=True)
    municipio = models.TextField(blank=True, null=True)
    ddd_1 = models.TextField(blank=True, null=True)
    telefone_1 = models.TextField(blank=True, null=True)
    ddd_2 = models.TextField(blank=True, null=True)
    telefone_2 = models.TextField(blank=True, null=True)
    ddd_fax = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    qualif_resp = models.TextField(blank=True, null=True)
    capital_social = models.TextField(blank=True, null=True)
    porte = models.TextField(blank=True, null=True)
    opc_simples = models.TextField(blank=True, null=True)
    data_opc_simples = models.TextField(blank=True, null=True)
    data_exc_simples = models.TextField(blank=True, null=True)
    opc_mei = models.TextField(blank=True, null=True)
    situacao_especial = models.TextField(blank=True, null=True)
    data_sit_especial = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empresas'


class Socios(models.Model):
    cnpj_basico = models.TextField(blank=True, null=True)
    id_socio = models.TextField(blank=True, null=True)
    nome_socio = models.TextField(blank=True, null=True)
    cpf_cnpj_socio = models.TextField(primary_key=True)
    cod_qualif_socio = models.TextField(blank=True, null=True)
    data_entrada_sociedade = models.TextField(blank=True, null=True)
    pais = models.TextField(blank=True, null=True)
    repr_legal = models.TextField(blank=True, null=True)
    nome_repr = models.TextField(blank=True, null=True)
    cod_qualif_repr_legal = models.TextField(blank=True, null=True)
    faixa_etaria = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'socios'
