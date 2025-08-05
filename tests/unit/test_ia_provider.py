# tests/test_ia_provider.py
from app.utils.ia_provider import IAProviderExemplo

def test_make_response():
    provedor = IAProviderExemplo()
    mensagem = "Olá, IA!"
    resposta = provedor.make_response(mensagem)
    assert resposta == "Resposta gerada para: Olá, IA!"
