"""Triagem determinística de propostas de crédito rural."""

from triagem_proposta.engine import triar_proposta
from triagem_proposta.models import Parecer, Proposta, ResultadoTriagem

__all__ = [
    "Parecer",
    "Proposta",
    "ResultadoTriagem",
    "triar_proposta",
]

__version__ = "1.0.0"
