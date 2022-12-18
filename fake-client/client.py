import asyncio
import time

import httpx


async def client_get(client, client_get_args, client_get_kwargs, expected_status_code):
    start_time = time.time()
    response = await client.get(*client_get_args, **client_get_kwargs)

    print(client_get_args, response.status_code, int(time.time() - start_time))


async def main():
    async with httpx.AsyncClient(http2=True) as client:
        first_coros = [
            client_get(
                client, ["http://localhost:27001/sleep-9"], {"timeout": 180}, 504
            )
            for _ in range(9)
        ]

        first_tasks = [asyncio.create_task(c) for c in first_coros]

        next_coros = [
            client_get(client, ["http://localhost:27001/ok"], {"timeout": 180}, 200)
            for _ in range(23)
        ]

        next_tasks = [asyncio.create_task(c) for c in next_coros]

        await asyncio.gather(*first_tasks, *next_tasks)


asyncio.run(main())
