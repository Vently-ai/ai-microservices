import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from .workflow import UserDiaryWorkflow
from .activities import (
    diary_summary_agent,
    past_week_diary_summary_agent,
    overall_status_agent,
    background_agent,
)

async def start_worker(
    temporal_address: str = "localhost:7233",
    task_queue: str = "post-interaction",
):
    client = await Client.connect(temporal_address)

    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[UserDiaryWorkflow],
        activities=[
            diary_summary_agent,
            past_week_diary_summary_agent,
            overall_status_agent,
            background_agent,
        ],
    )

    await worker.run()
    
if __name__ == "__main__":
    asyncio.run(main())
