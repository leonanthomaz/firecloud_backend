import time
import pytest
from app.utils.redis_utils import cache_response, get_cached_response
from app.configuration.settings import get_redis_client

@pytest.fixture
def clear_cache():
    # Inicializa a conexão com o Redis aqui para garantir que esteja disponível
    redis_client = get_redis_client()
    
    # Limpa o banco de dados Redis antes de cada teste
    redis_client.flushdb()

def test_cache_response(clear_cache):
    """
    Testa o armazenamento de uma resposta no Redis.
    """
    cache_response("test_key", "Test Response", expiration=3600)
    cached_response = get_cached_response("test_key")
    
    # Decodifica a resposta para garantir que ela seja uma string
    assert cached_response == "Test Response"
    assert cached_response is not None

def test_cache_expiration(clear_cache):
    """
    Testa se a resposta expira após o tempo definido.
    """
    cache_response("test_key", "Test Expiry Response", expiration=1)  # Expira em 1 segundo
    time.sleep(2)  # Espera 2 segundos para garantir que o cache expirou
    cached_response = get_cached_response("test_key")
    
    assert cached_response is None  # O cache deve ter expirado

def test_cache_overwrite(clear_cache):
    """
    Testa se o cache é sobrescrito quando a mesma chave é armazenada com um valor diferente.
    """
    cache_response("test_key", "Initial Response", expiration=3600)
    # Recupera o valor inicial
    initial_response = get_cached_response("test_key")
    assert initial_response == "Initial Response"
    
    # Sobrescreve com um novo valor
    cache_response("test_key", "Overwritten Response", expiration=3600)
    overwritten_response = get_cached_response("test_key")
    
    assert overwritten_response == "Overwritten Response"
    assert overwritten_response != "Initial Response"  # Verifica que o valor antigo foi substituído
