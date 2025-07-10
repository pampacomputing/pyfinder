from django.db import models


class Cpf(models.Model):
    cpf = models.CharField(
        max_length=14, primary_key=True, db_index=True
    )  # CPF with formatting
    nome = models.CharField(max_length=255, db_index=True)  # Name
    nasc = models.DateField(null=True, blank=True)  # Birth date
    sexo = models.CharField(max_length=1, null=True, blank=True)  # Gender

    class Meta:
        managed = False
        db_table = "cpf"
        app_label = "cpf_search"  # Use existing table name

    def __str__(self):
        return f"{self.nome} - {self.cpf}"
