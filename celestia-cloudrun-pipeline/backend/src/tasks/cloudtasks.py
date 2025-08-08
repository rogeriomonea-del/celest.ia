from google.cloud import tasks_v2
from core.config import settings
from core.logging import logger
import json
import base64

def enqueue_task(handler_path: str, payload: dict, queue: str = "celestia-queue"):
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(settings.gcp_project_id, settings.gcp_location, queue)
    body = json.dumps(payload).encode("utf-8")

    if not settings.service_url:
        raise RuntimeError("SERVICE_URL (Cloud Run URL) não definido para push handler.")

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": f"{settings.service_url.rstrip('/')}{handler_path}",
            "headers": {
                "Content-Type": "application/json"
            },
            "body": body,
        }
    }

    response = client.create_task(request={"parent": parent, "task": task})
    logger.info(f"Task enqueued to {queue}: {response.name}")
    return response.name
