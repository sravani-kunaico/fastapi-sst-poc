import os
import time
import boto3
from typing import Optional, List
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from boto3.dynamodb.conditions import Key

class TaskRequest(BaseModel):
    content: str
    userId: Optional[str] = None
    taskId: Optional[str] = None
    isDone: bool = False

class TaskListResponse(BaseModel):
    tasks: List[TaskRequest]

app = FastAPI()
handler = Mangum(app)

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}


@app.post("/create-task")
async def create_task(task_request: TaskRequest):
    created_time = int(time.time())
    item = {
        "userId": task_request.userId,
        "content": task_request.content,
        "isDone": False,
        "createdAt": created_time,
        "taskId": f"task_{uuid4().hex}",
        "ttl": int(created_time + 86400),  # Expire after 24 hours.
    }

    # Save Item.
    table = _get_table()
    table.put_item(Item=item)
    return {"task": item}


@app.get("/get-task/{task_id}")
async def get_task(task_id: str):
    # Get the task from the table.
    table = _get_table()
    response = table.get_item(Key={"taskId": task_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return item


@app.get("/list-tasks/{user_id}")
async def list_tasks(user_id: str):
    # List the top N tasks from the table, using the user index.
    table = _get_table()
    response = table.query(
        IndexName="userIdIndex",
        KeyConditionExpression=Key("userId").eq(user_id),
        ScanIndexForward=False,
        Limit=10,
    )
    tasks = response.get("Items")
    return {"tasks": tasks}

# List all tasks
@app.get("/list-tasks", response_model=TaskListResponse)
async def get_all_tasks() -> List[dict]:
    try:
        # Scan to retrieve all records
        table = _get_table()
        response = table.scan()
        tasks = response.get('Items', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"tasks": tasks}

@app.put("/update-task")
async def update_task(task_request: TaskRequest):
    # Update the task in the table.
    table = _get_table()
    table.update_item(
        Key={"taskId": task_request.taskId},
        UpdateExpression="SET content = :content, isDone = :isDone",
        ExpressionAttributeValues={
            ":content": task_request.content,
            ":isDone": task_request.isDone,
        },
        ReturnValues="ALL_NEW",
    )
    return {"updated_task_id": task_request.taskId}


@app.delete("/delete-task/{task_id}")
async def delete_task(task_id: str):
    # Delete the task from the table.
    table = _get_table()
    table.delete_item(Key={"taskId": task_id})
    return {"deleted_task_id": task_id}


def _get_table():
    table_name = os.environ.get("TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)
