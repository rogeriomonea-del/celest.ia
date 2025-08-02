from ai_engine.openai_caller import call_openai
from ai_engine.gemini_caller import call_gemini

def analyze(prompt, engine="openai"):
    if engine == "openai":
        return call_openai(prompt)
    elif engine == "gemini":
        return call_gemini(prompt)
    else:
        return "Engine inválido. Use 'openai' ou 'gemini'."
