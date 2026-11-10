"""Regula de business folosita la testele unitare din Modulul 8."""
import math


def clasifica_temperatura(temperatura):
    """Temperaturi >30°C primesc status ALERTA; restul OK."""
    if isinstance(temperatura, bool) or not isinstance(temperatura, (int, float)):
        raise ValueError("Temperatura trebuie sa fie numerica")
    if not math.isfinite(temperatura):
        raise ValueError("Temperatura trebuie sa fie finita")
    return "ALERTA" if temperatura > 30 else "OK"
