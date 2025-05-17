import asyncio
from contextlib import suppress

__ALL__ = [
    'cancel_gen',
]

async def cancel_gen(agen):
    task = asyncio.create_task(agen.__anext__())
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
    await agen.aclose()