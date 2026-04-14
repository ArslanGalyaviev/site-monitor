from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import asyncio
import httpx
import time

@dataclass
class CheckResult:
    url: str
    status_code: int | None
    response_time_ms: float
    is_available: bool
    error: str | None
    checked_at: str

async def check_site_async(url: str, client: httpx.AsyncClient, timeout: float = 5.0) -> CheckResult:
    start_time = time.perf_counter()
    status_code: Optional[int] = None
    error: Optional[str] = None
    is_available: bool = False

    try:
        response = await client.get(url, timeout=timeout)
        status_code = response.status_code
        is_available = True
        if status_code >= 400:
            error = f"HTTP {status_code}: {response.reason_phrase}"
    except httpx.ConnectError:
        is_available = False
        error = "Не удалось подключиться к серверу"
    except httpx.TimeoutException:
        is_available = False
        error = "Истекло время ожидания"
    except httpx.RequestError as exc:
        is_available = False
        error = f"Ошибка запроса: {type(exc).__name__}"
    finally:
        end_time = time.perf_counter()
        response_time_ms = round((end_time - start_time) * 1000, 2)
    return CheckResult(
        url=url,
        status_code=status_code,
        response_time_ms=response_time_ms,
        is_available=is_available,
        error=error,
        checked_at=datetime.now(timezone.utc).isoformat()
    )

async def check_multiple_sites(urls: list[str], timeout: float = 5.0) -> list[CheckResult]:
    async with httpx.AsyncClient() as client:
        tasks = [check_site_async(url, client, timeout) for url in urls]
        results = await asyncio.gather(*tasks)
        return list(results)

if __name__ == "__main__":
    test_urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/500",
        "https://thissitedoesnotexist12345.com",
        "https://httpbin.org/delay/10"
    ]
    start = time.perf_counter()
    results = asyncio.run(check_multiple_sites(test_urls, timeout=5.0))
    total_time = time.perf_counter() - start
    print(f"Потрачено {total_time:.2f} секунд на {len(test_urls)} ссылки")
    for r in results:
        print(r, end='\n\n')


