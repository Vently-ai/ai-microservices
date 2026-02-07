from temporalio.client import Client
from .workflow import UserDiaryWorkflow

async def create_waiting_job(
    *,
    session_id: str,
    user_background: str,
    user_status: str,
    user_diary_summary_1: str,
    temporal_address: str = "localhost:7233",
    task_queue: str = "post-interaction",
):
    client = await Client.connect(temporal_address)

    await client.start_workflow(
        UserDiaryWorkflow.run,
        session_id=session_id,
        user_background=user_background,
        user_status=user_status,
        user_diary_summary_1=user_diary_summary_1,
        id=session_id,  # session_id == workflow_id
        task_queue=task_queue,
    )

async def start_job_with_diary(
    *,
    session_id: str,
    user_diary: str,
    temporal_address: str = "localhost:7233",
):
    client = await Client.connect(temporal_address)
    handle = client.get_workflow_handle(session_id)

    await handle.signal(
        UserDiaryWorkflow.start_with_diary,
        user_diary,
    )
