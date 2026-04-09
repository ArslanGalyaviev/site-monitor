from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import httpx
import time

@dataclass
class CheckResult:
    url: str
    status_code: int | None
    response_time_ms: float
    is_up: bool
    error: str | None
    checked_at: str

def check_site(url: str, timeout: float = 5.0) -> CheckResult:
    start_time = time.perf_counter()
    status_code: Optional[int] = None
    error: Optional[str] = None
    is_up: bool = False

    try:
        response = httpx.get(url, timeout=timeout)
        status_code = response.status_code
        is_up = True
        if status_code >= 400:
            error = f"HTTP {status_code}: {response.reason_phrase}"
    except httpx.ConnectError:
        is_up = False
        error = "Не удалось подключиться к серверу"
    except httpx.TimeoutException:
        is_up = False
        error = "Истекло время ожидания"
    except httpx.RequestError as exc:
        is_up = False
        erorr = f"Ошибка запроса: {type(exc).__name__}"
    finally:
        end_time = time.perf_counter()
        response_time_ms = round((end_time - start_time) * 1000, 2)
    return CheckResult(
        url=url,
        status_code=status_code,
        response_time_ms=response_time_ms,
        is_up=is_up,
        error=error,
        checked_at=datetime.now(timezone.utc).isoformat()
    )


if __name__ == '__main__':
    test_urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/500",
        "https://thissitedoesnotexist12345.com",
        "https://httpbin.org/delay/10"
    ]
    for u in test_urls:
        result = check_site(u, timeout=5.0)
        print(result)