from typing import List

from lib.core.entity.models import SourceData
from lib.core.sdk.usecase_models import BaseErrorResponse, BaseRequest, BaseResponse


class ListSourceDataRequest(BaseRequest):
    """
    Request Model for the List Source Data Use Case.
    """

    knowledge_source_id: int | None = None


class ListSourceDataResponse(BaseResponse):
    """
    Response Model for the List Source Data Use Case.
    """

    source_data_list: List[SourceData]


class ListSourceDataError(BaseErrorResponse):
    """
    Error Response Model for the List Source Data Use Case.
    """

    knowledge_source_id: int | None = None
