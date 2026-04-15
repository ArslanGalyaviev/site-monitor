import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, token: str, chat_id: int, timeout: float = 5.0):
        self.token = token
        self.chat_id = chat_id
        self.timeout = timeout
        self.base_url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    async def send_message(self, text: str, parse_mode: Optional[str] = "HTML") -> bool:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    json={
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": parse_mode
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        logger.info(f"Уведомление отправлено")
                        return True
                    else:
                        logger.error(f"Телеграмм получил ошибку: {data}")
                        return False
                else:
                    logger.error(f"HTTP {response.status_code}: {response.text}")
                    return False
        except httpx.RequestError as exc:
            logger.error(f"Ошибка отправки уведомления: {type(exc).__name__}")
            return False
    
    def format_alert(self, url: str, status: str, details: str) -> str:
        emoji = "🔴" if status == "Сайт упал" else "🟢"
        return (
            f"{emoji} <b>Мониторинг сайтов</b>\n\n"
            f"<b>Сайт:</b> <code>{url}</code>\n"
            f"<b>Статус:</b> {status}\n"
            f"<b>Детали:</b> {details}"
        )