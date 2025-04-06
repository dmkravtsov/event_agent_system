import logging
import os
from abc import ABC, abstractmethod
from typing import Any, List
from pydantic import BaseModel, ConfigDict

# Ensure log directory exists
os.makedirs("logs", exist_ok=True)

# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/agent_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class BaseAgent(BaseModel, ABC):
    """
    Base class for all agents in the project.
    This class defines the shared interface and base functionality 
    that can be reused by child agent classes.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "BaseAgent"
    logger: logging.Logger = logging.getLogger("BaseAgent")

    @abstractmethod
    async def process(self, data: Any) -> Any:
        """
        Method for processing incoming data. Must be implemented in child classes.

        :param data: Input data to be processed.
        :return: Processed output data.
        """
        pass

    async def log(self, message: str, level: str = "INFO") -> None:
        """
        Logs a message at the specified level.

        :param message: The message to log.
        :param level: Logging level (e.g., INFO, WARNING, ERROR).
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(f"{self.name}: {message}")

    async def handle_error(self, error: Exception, context: Any = None) -> None:
        """
        Handles exceptions and logs them with ERROR level.

        :param error: The raised exception.
        :param context: Optional context related to the exception.
        """
        await self.log(f"Error: {error}. Context: {context}", level="ERROR")

    async def validate_data(self, data: List[Any]) -> bool:
        """
        Validates the input data before processing.
        Logs a warning if the data is missing or invalid.

        :param data: A list of data items to validate.
        :return: True if data is valid, False otherwise.
        """
        if not isinstance(data, list) or not data:
            await self.log("Invalid or empty data provided.", level="WARNING")
            return False
        return True
