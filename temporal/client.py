from temporalio.client import Client
from .workflow import UserDiaryWorkflow
from config import Config

_temporal_client: Client | None = None

async def get_temporal_client() -> Client:
    """
    Singleton Temporal client
    """
    global _temporal_client
    
    if _temporal_client is None:
        _temporal_client = await Client.connect(
            Config.TEMPORAL["address"],
            namespace=Config.TEMPORAL["namespace"]
        )
    
    return _temporal_client


async def create_waiting_job(
    *,
    session_id: str,
    user_background: str,
    user_status: str,
    user_diary_summary_1: str,
    task_queue: str = "post-interaction",
):
    client = await get_temporal_client()
    
    await client.start_workflow(
        workflow=UserDiaryWorkflow.run,
        args=[
            session_id,
            user_background,
            user_status,
            user_diary_summary_1
        ],
        id=session_id,
        task_queue=task_queue,
    )   


    # await client.start_workflow(
    #     UserDiaryWorkflow.run,
    #     session_id=session_id,
    #     user_background=user_background,
    #     user_status=user_status,
    #     user_diary_summary_1=user_diary_summary_1,
    #     id=session_id,  # session_id == workflow_id
    #     task_queue=task_queue,
    # )

async def start_job_with_diary(
    *,
    session_id: str,
    user_diary: str,
):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(session_id)

    await handle.signal(
        UserDiaryWorkflow.start_with_diary,
        user_diary,
    )
