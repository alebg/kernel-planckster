from typing import List
from lib.core.sdk.dto import BaseDTO
from lib.core.entity.models import SourceData, TMessageBase


class MessageDTO(BaseDTO[TMessageBase]):
    """
    Basic DTO for messages

    @param message_id: The id of the message
    @type message_id: int | None
    @param data: Data of the message handled
    @type data: TMessageBase | None
    """

    message_id: int | None = None
    data: TMessageBase | None = None


class ListMessageSourcesDTO(BaseDTO[SourceData]):
    """
    A DTO for listing the data sources of the message response by an LLM

    @param data: The source data of the message response
    @type data: List[SourceData] | None
    """

    data: List[SourceData] | List[None] | None = None
