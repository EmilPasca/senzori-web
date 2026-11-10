import pytest
from logic import clasifica_temperatura


@pytest.mark.parametrize('valoare,asteptat', [
    (-5, 'OK'), (30, 'OK'), (30.1, 'ALERTA'), (45, 'ALERTA')
])
def test_clasificare_temperatura(valoare, asteptat):
    assert clasifica_temperatura(valoare) == asteptat


@pytest.mark.parametrize('valoare', [None, '31', True, float('nan')])
def test_respingere_temperatura_invalida(valoare):
    with pytest.raises(ValueError):
        clasifica_temperatura(valoare)
