import threading
from typing import Dict, Optional, List
from .models import ProgressResponse

class TaskManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._tasks: Dict[str, ProgressResponse] = {}

    def create_task(self, task_id: str, title: str) -> ProgressResponse:
        with self._lock:
            task = ProgressResponse(
                task_id=task_id,
                status="queued",
                filename=title,
                progress_percent=0.0
            )
            self._tasks[task_id] = task
            return task

    def update_task(self, task_id: str, **kwargs):
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)

    def get_task(self, task_id: str) -> Optional[ProgressResponse]:
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 15) -> List[ProgressResponse]:
        with self._lock:
            # Retorna las tareas en orden inverso (más recientes primero)
            tasks = list(self._tasks.values())
            tasks.reverse()
            return tasks[:limit]

task_manager = TaskManager()

