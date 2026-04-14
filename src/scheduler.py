import asyncio
import logging
from typing import Optional
import httpx

from async_checker import check_site_async, CheckResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

class SiteMonitor:
    def __init__(self, urls: list[str], check_interval: float = 30.0, timeout: float = 5.0):
        self.urls = urls
        self.check_interval = check_interval
        self.timeout = timeout
        self.number_of_failures: dict[str, int] = {url: 0 for url in urls}
        self.failure_threshold = 3
    
    async def check_and_track(self, url: str, client: httpx.AsyncClient) -> CheckResult:
        result = await check_site_async(url, client, self.timeout)

        if result.is_available:
            if self.number_of_failures[url] > 0:
                logger.info(f"{url} восстановился после {self.number_of_failures[url]} неудач")
            self.number_of_failures[url] = 0
        else:
            self.number_of_failures[url] += 1
            if self.number_of_failures[url] == self.failure_threshold:
                logger.error(f"{url} упал, количество неудач подряд: {self.number_of_failures[url]}")
            elif self.number_of_failures[url] > self.failure_threshold:
                logger.warning(f"{url} все еще не восстановлен, количество неудач подряд: {self.number_of_failures[url]}")
        return result
    
    async def run(self):
        logger.info(f"Запуск мониторинга {len(self.urls)} сайтов(интервал = {self.check_interval} секунд)")

        async with httpx.AsyncClient() as client:
            while True:
                logger.info(f"Новая проверка {len(self.urls)} сайтов")
                
                tasks = [self.check_and_track(url, client) for url in self.urls]
                await asyncio.gather(*tasks)

                logger.info(f"Пауза на {self.check_interval} секунд\n")
                await asyncio.sleep(self.check_interval)

if __name__ == "__main__":
    test_urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/500",
        "https://thissitedoesnotexist12345.com",
    ]

    monitor = SiteMonitor(urls=test_urls, check_interval=30.0, timeout=5.0)

    try:
        asyncio.run(monitor.run())
    except KeyboardInterrupt:
        logger.info("Остановлено пользователем")