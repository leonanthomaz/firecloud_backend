from enum import Enum

class Provider(str, Enum):
    OPENAI = "OPENAI"
    DEEPSEEK = "DEEPSEEK"