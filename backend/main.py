from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.executor import run_python_code
from backend.llm import analyze_code_with_llm, generate_task

app = FastAPI(title="SIGGMA JUDGE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str
    difficulty: str


class CodeRequest(BaseModel):
    code: str
    task_text: str = ""
    input_data: str = "" 

@app.post("/api/generate_task")
async def get_new_task(request: TopicRequest):
    task_text = await generate_task(request.topic, request.difficulty, model_name="mistral:latest")
    return {"task": task_text}

@app.post("/api/execute")
async def execute_code(request: CodeRequest):
    # Передаем ввод в песочницу
    execution_result = run_python_code(request.code, request.input_data)
    
    ai_feedback = await analyze_code_with_llm(
        code=request.code, 
        execution_result=execution_result,
        task_context=request.task_text,
        model_name="mistral:latest"
    )
    
    return {
        "execution": execution_result,
        "ai_feedback": ai_feedback
    }