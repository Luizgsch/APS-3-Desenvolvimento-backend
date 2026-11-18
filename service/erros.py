class CapacidadeInsuficienteError(Exception):
    """A capacidade solicitada é menor que a quantidade atual de inscritos."""


class EmailDuplicadoError(Exception):
    """Já existe um participante com o e-mail informado."""
