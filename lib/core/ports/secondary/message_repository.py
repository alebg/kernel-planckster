from abc import ABC, abstractmethod
import logging

from lib.core.dto.message_repository_dto import ListMessageSourcesDTO


class MessageRepository(ABC):
    """
    Abstract base class for the message repository.

    @cvar logger: The logger for this class.
    @type logger: logging.Logger
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def list_message_sources(self, message_id: int) -> ListMessageSourcesDTO:
        """
        Lists all data sources of the research context of a message.

        @param message_id: The ID of the message to list sources for.
        @type message_id: int
        @return: A DTO containing the result of the operation.
        @rtype: ListMessageSourcesDTO
        """
        raise NotImplementedError
