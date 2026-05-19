import httpx
import random

OLLAMA_URL = "http://localhost:11434/api/generate"

async def generate_task(topic: str, difficulty: str, model_name: str = "mistral:latest"):
    seed = random.randint(1, 100000)
    
    prompt = f"""Сгенерируй ОДНУ уникальную задачу по программированию на РУССКОМ ЯЗЫКЕ.
Тема: "{topic}". Сложность: "{difficulty}". Уникальный ID: {seed}.

ЕСЛИ ТЕМА "ЕГЭ Информатика":
Генерируй задачу СТРОГО в формате реального ЕГЭ (например, задание 17 на поиск пар в массиве, или задание 24 на обработку строк, или 27 на оптимизацию). 

Структура ответа:
1. Название задачи (с номером).
2. Подробное условие.
3. Входные данные.
4. Выходные данные.
5. Пример.

НИКАКОГО КОДА РЕШЕНИЯ! ТОЛЬКО ТЕКСТ ЗАДАЧИ."""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OLLAMA_URL,
                json={"model": model_name, "prompt": prompt, "stream": False, "options": {"temperature": 0.8}},
                timeout=60.0
            )
            return response.json()["response"] if response.status_code == 200 else "Ошибка генерации."
        except Exception as e:
            return f"Ошибка Ollama: {e}"


SYSTEM_PROMPT = SYSTEM_PROMPT = """ТЫ — СУРОВЫЙ И ЖЕСТКИЙ AI-МЕНТОР (SIGGMA JUDGE). 
Твоя задача — проверить код пользователя и дать ревью. Отвечай СТРОГО на русском языке.

АБСОЛЮТНОЕ ПРАВИЛО: ТЕБЕ СТРОГО ЗАПРЕЩЕНО ПИСАТЬ ЛЮБОЙ КОД! ВООБЩЕ НИКАКОГО КОДА НА PYTHON ИЛИ ДРУГИХ ЯЗЫКАХ!
Если пользователь написал пустой код (pass) или код с ошибкой, просто укажи на это словами. 
Если ты напишешь хотя бы одну строчку кода решения — ты провалишь задачу.

Формат ответа:
1. Оценка сложности (Big O), если код был написан.
2. Указание на ошибки (словами, без кода).
3. Намек, куда двигаться дальше (только теория)."""
async def analyze_code_with_llm(code: str, execution_result: dict, task_context: str = "", model_name: str = "mistral:latest"):
    prompt = f"""
    условие задачи: {task_context}
    код пользователя:
    {code}
    
    статус: {execution_result['status']}
    вывод консоли: {execution_result['output']}
    ошибки из консоли (переведи суть на русский, если надо): {execution_result['error']}
    """
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                OLLAMA_URL,
                json={"model": model_name, "prompt": prompt, "system": SYSTEM_PROMPT, "stream": False},
                timeout=60.0
            )
            return response.json()["response"] if response.status_code == 200 else "ошибка api."
        except Exception as e:
            return f"ошибка Ollama: {e}"