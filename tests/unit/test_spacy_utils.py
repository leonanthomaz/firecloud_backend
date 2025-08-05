import json
import pytest
import os
from app.utils.spacy_utils import carregar_dados_empresa, processar_mensagem

def test_carregar_dados_empresa():
    # Criar um arquivo temporário para testar
    test_data = {
        "nome_empresa": "Exemplo Ltda",
        "produtos": ["produto1", "produto2"]
    }

    with open("dados_empresa.json", "w") as f:
        json.dump(test_data, f)

    # Verifica se a função retorna os dados corretos
    dados = carregar_dados_empresa()
    assert dados == test_data

    # Apaga o arquivo após o teste
    os.remove("dados_empresa.json")

def test_carregar_dados_empresa_arquivo_inexistente():
    # Testa se a função retorna None quando o arquivo não existe
    os.remove("dados_empresa.json") if os.path.exists("dados_empresa.json") else None
    assert carregar_dados_empresa() is None

def test_carregar_dados_empresa_erro_json():
    # Cria um arquivo JSON com erro
    with open("dados_empresa.json", "w") as f:
        f.write("{ nome_empresa: Exemplo Ltda, produtos: produto1 }")  # JSON malformado

    # Testa se a função retorna None com erro de JSON
    assert carregar_dados_empresa() is None
    os.remove("dados_empresa.json")

# @pytest.mark.parametrize("mensagem, esperado", [
#     ("Eu quero comprar um celular", ["smartphone"]),
#     ("Meu computador quebrou", ["notebook"]),
#     ("Estou assistindo na tv", ["televisão"]),
#     ("Tenho um laptop", ["notebook"]),
#     ("Preciso de um pc novo", ["notebook"]),
#     ("Eu adoro usar meu telefone", ["smartphone"]),
#     ("Ontem, fui para a casa de João", ["João"])  # Testando nome próprio
# ])
# def test_processar_mensagem(mensagem, esperado):
#     palavras_chave = processar_mensagem(mensagem)
#     assert palavras_chave == esperado

# def test_processar_mensagem_sem_modelo_spacy():
#     # Simula o caso quando o modelo spaCy não está carregado
#     from app.utils.spacy_utils import nlp
#     nlp = None  # Simula que o modelo não foi carregado corretamente
    
#     palavras_chave = processar_mensagem("Eu quero comprar um celular")
#     assert palavras_chave == []  # Não deve processar nada