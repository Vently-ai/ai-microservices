import asyncio
from datetime import timedelta
from typing import Optional

from temporalio import workflow

# Safe import for determinism
with workflow.unsafe.imports_passed_through():
    from .activities import (
        diary_summary_agent,
        past_week_diary_summary_agent,
        overall_status_agent,
        background_agent,
    )


@workflow.defn
class UserDiaryWorkflow:
    def __init__(self):
        self._user_diary: Optional[str] = None

    # -------- Signal --------
    @workflow.signal
    async def start_with_diary(self, user_diary: str):
        self._user_diary = user_diary

    # -------- Workflow --------
    @workflow.run
    async def run(
        self,
        session_id: str,
        user_background: str,
        user_status: str,
        user_diary_summary_1: str,
    ) -> str:
        # Wait for diary
        await workflow.wait_condition(lambda: self._user_diary is not None)
        user_diary = self._user_diary

        # Step 1: Diary summary (sequential)
        user_diary_summary_0 = await workflow.execute_activity(
            diary_summary_agent,
            args=[
                user_diary,
                session_id
            ],
            start_to_close_timeout=timedelta(seconds=120),
        )

        # Step 2: Parallel agents
        weekly_task = workflow.execute_activity(
            past_week_diary_summary_agent,
            args=[
                user_diary_summary_0,
                user_diary_summary_1,
                session_id
            ],
            start_to_close_timeout=timedelta(seconds=120),
        )

        status_task = workflow.execute_activity(
            overall_status_agent,
            args=[
                user_status,
                user_diary,
                session_id
            ],
            start_to_close_timeout=timedelta(seconds=120),
        )

        background_task = workflow.execute_activity(
            background_agent,
            args=[
                user_background,
                user_diary,
                session_id,
            ],
            start_to_close_timeout=timedelta(seconds=120),
        )

        await asyncio.gather(
            weekly_task,
            status_task,
            background_task,
        )

        return "WORKFLOW COMPLETED"
