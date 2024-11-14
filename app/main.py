from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import asyncio
import uuid

app = FastAPI()


# Модель для входных данных
class OperationRequest(BaseModel):
    x: int
    y: int
    operator: str


# Модель для получения результата задачи
class TaskResultRequest(BaseModel):
    task_id: str


# Хранение результатов и статусов задач
results = {}


# Функция для выполнения операции в фоне
async def perform_operation(task_id: str, x: int, y: int, operator: str):
    try:
        results[task_id][
            'status'] = "In Progress"  # Устанавливаем статус в "В процессе"
        await asyncio.sleep(1)  # Имитируем длительную задачу

        if operator == "+":
            result = x + y
        elif operator == "-":
            result = x - y
        elif operator == "*":
            result = x * y
        elif operator == "/":
            if y == 0:
                raise ValueError("Division by zero is not allowed.")
            result = x / y
        else:
            raise ValueError("Invalid operator.")

        # Сохраняем результат работы задачи и обновляем статус
        results[task_id] = {"result": result, "status": "Completed"}
    except Exception as e:
        results[task_id] = {"error": str(e), "status": "Failed"}


@app.post("/calculate/")
async def calculate(op: OperationRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())  # Генерируем уникальный ID для задачи
    # Добавляем задачу в результаты с начальным статусом
    results[task_id] = {"status": "Pending"}
    background_tasks.add_task(perform_operation, task_id, op.x, op.y,
                              op.operator)
    return {"task_id": task_id}  # Возвращаем ID фоновой задачи


@app.post("/result/")
async def get_result(task_request: TaskResultRequest):
    task_id = task_request.task_id
    result = results.get(task_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Task ID not found.")

    return result


@app.get("/tasks/")
async def list_tasks():
    # Возвращаем список всех задач с их статусами
    task_statuses = [{"task_id": task_id, "status": task_info["status"]} for
                     task_id, task_info in results.items()]
    return task_statuses
