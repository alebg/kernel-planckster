from tkinter import W
from typing import List
from lib.core.dto.message_repository_dto import ListMessageSourcesDTO
from lib.core.entity.models import MessageResponse, SourceData
from lib.core.ports.secondary.message_repository import MessageRepository
from lib.core.sdk.dto import generate_error_dto_and_message
from lib.infrastructure.repository.sqla.database import TDatabaseFactory
from lib.infrastructure.repository.sqla.models import SQLAMessageResponse, SQLASourceData


class SQLAMessageRepository(MessageRepository):
    def __init__(self, session_factory: TDatabaseFactory) -> None:
        super().__init__()

        with session_factory() as session:
            self.session = session

    def list_message_sources(self, message_id: int) -> ListMessageSourcesDTO:
        """
        Lists all data sources of the research context of a message response.

        @param message_id: The ID of the message to list sources for.
        @type message_id: int
        @return: A DTO containing the result of the operation.
        @rtype: ListMessageSourcesDTO
        """

        if message_id is None:
            errorDTO: ListMessageSourcesDTO = generate_error_dto_and_message(
                DTO=ListMessageSourcesDTO, entity=MessageResponse, errorCode=-1, attribute="ID"
            )
            self.logger.error(f"{errorDTO.errorMessage}")
            return errorDTO

        sqla_message: SQLAMessageResponse | None = (
            self.session.query(SQLAMessageResponse).filter_by(id=message_id).first()
        )

        if sqla_message is None:
            errorDTO = generate_error_dto_and_message(
                DTO=ListMessageSourcesDTO,
                entity=MessageResponse,
                errorCode=-2,
                attribute="ID",
                attribute_value=message_id,
            )
            self.logger.error(f"{errorDTO.errorMessage}")
            return errorDTO

        sources_list: List[SourceData | None] = []

        for citation in sqla_message.citations:
            sqla_source_data = self.session.query(SQLASourceData).filter_by(id=citation.source_data_id).first()
            if sqla_source_data is None:
                errorDTO = generate_error_dto_and_message(
                    DTO=ListMessageSourcesDTO,
                    entity=SourceData,
                    errorCode=-2,
                    attribute="ID",
                    attribute_value=citation.source_data_id,
                )
                self.logger.error(f"{errorDTO.errorMessage}")
                return errorDTO

            source_core = SourceData(
                created_at=sqla_source_data.created_at,
                updated_at=sqla_source_data.updated_at,
                deleted=sqla_source_data.deleted,
                deleted_at=sqla_source_data.deleted_at,
                id=sqla_source_data.id,
                name=sqla_source_data.name,
                type=sqla_source_data.type,
                lfn=sqla_source_data.lfn,
                protocol=sqla_source_data.protocol,
            )

            sources_list.append(source_core)

        return ListMessageSourcesDTO(status=True, data=sources_list)
