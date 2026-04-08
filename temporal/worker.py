import asyncio
from concurrent.futures import ThreadPoolExecutor
from temporalio.client import Client
from temporalio.worker import Worker

from .workflow import UserDiaryWorkflow
from .activities import (
    diary_summary_agent,
    past_week_diary_summary_agent,
    overall_status_agent,
    background_agent,
    terminate_session_in_redis
)

from .client import get_temporal_client

async def start_worker(
    task_queue: str = "post-interaction",
):
    client = await get_temporal_client()

    with ThreadPoolExecutor(max_workers=10) as executor:
        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[UserDiaryWorkflow],
            activities=[
                diary_summary_agent,
                past_week_diary_summary_agent,
                overall_status_agent,
                background_agent,
                terminate_session_in_redis
            ],
            activity_executor=executor,
        )

        await worker.run()

async def main():
    await start_worker()
    
if __name__ == "__main__":
    asyncio.run(main())
