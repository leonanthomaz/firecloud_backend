from abc import ABC, abstractmethod
from typing import Any, Dict

class IAProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        context: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        pass
