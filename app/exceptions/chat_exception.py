from datetime import datetime, timezone

class ChatBlockException(Exception):
    def __init__(self, user_response: str, function_name: str, status: int, chat_code: str):
        self.response_data = {
            "useful_context": {
                "user_response": user_response,
                "system_response": {"function": function_name},
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "status": status,
            "chat_code": chat_code
        }
        super().__init__(user_response)
