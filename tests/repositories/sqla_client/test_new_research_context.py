import random
from typing import List
import uuid
from faker import Faker
from lib.core.dto.client_repository_dto import NewResearchContextDTO
from lib.infrastructure.config.containers import ApplicationContainer
from lib.infrastructure.repository.sqla.database import TDatabaseFactory
from lib.infrastructure.repository.sqla.models import SQLAAgent, SQLAResearchContext, SQLAClient


def test_create_new_research_context(
    app_initialization_container: ApplicationContainer,
    db_session: TDatabaseFactory,
    fake: Faker,
    fake_agent: SQLAAgent,
    fake_client_with_source_data_list: List[SQLAClient],
) -> None:
    sqla_client_repository = app_initialization_container.sqla_client_repository()

    agent = fake_agent
    client_list = fake_client_with_source_data_list
    client = random.choice(client_list)

    client_sub = client.sub
    agent_name = agent.name

    research_context_title = fake.name()
    research_context_description = fake.text()

    with db_session() as session:
        session.add(agent)
        for client in client_list:
            session.add(client)
        session.commit()

        source_data_list = client.source_data
        source_data_id_list = [source_data.id for source_data in source_data_list]
        agent_id = agent.id

    with db_session() as session:
        new_research_context_DTO: NewResearchContextDTO = sqla_client_repository.new_research_context(
            research_context_title=research_context_title,
            research_context_description=research_context_description,
            client_sub=client_sub,
            agent_id=agent_id,
            source_data_ids=source_data_id_list,
        )

        assert new_research_context_DTO.status == True

        assert new_research_context_DTO.research_context is not None
        assert new_research_context_DTO.agent is not None

        new_research_context_id = new_research_context_DTO.research_context.id
        new_research_context_agent = new_research_context_DTO.agent

        queried_new_research_context = session.get(SQLAResearchContext, new_research_context_id)

        assert queried_new_research_context is not None
        assert (
            queried_new_research_context.title
            == new_research_context_DTO.research_context.title
            == research_context_title
        )
        assert (
            queried_new_research_context.description
            == new_research_context_DTO.research_context.description
            == research_context_description
        )
        assert queried_new_research_context.agent_id == new_research_context_agent.id

        assert new_research_context_agent.name == agent_name

        queried_new_research_context_source_data = queried_new_research_context.source_data

        assert len(queried_new_research_context_source_data) == len(source_data_id_list)

        for source_data in queried_new_research_context_source_data:
            assert source_data.id in source_data_id_list


def test_error_new_research_context_research_context_title_is_None(
    app_initialization_container: ApplicationContainer, db_session: TDatabaseFactory
) -> None:
    sqla_client_repository = app_initialization_container.sqla_client_repository()

    research_context_title = None
    research_context_description = "Test description"
    client_sub = "test"
    agent_id = 1
    source_data_ids = [1, 2, 3]

    new_research_context_DTO: NewResearchContextDTO = sqla_client_repository.new_research_context(
        research_context_title=research_context_title,  # type: ignore
        research_context_description=research_context_description,
        client_sub=client_sub,
        agent_id=agent_id,
        source_data_ids=source_data_ids,
    )

    assert new_research_context_DTO.status == False
    assert new_research_context_DTO.errorCode == -1
    assert new_research_context_DTO.errorName == "Research context title not provided"
    assert new_research_context_DTO.errorType == "ResearchContextTitleNotProvided"


def test_error_new_research_context_description_is_None(
    app_initialization_container: ApplicationContainer, db_session: TDatabaseFactory
) -> None:
    sqla_client_repository = app_initialization_container.sqla_client_repository()

    research_context_title = "test"
    research_context_description = None
    client_sub = "test"
    agent_id = 1
    source_data_ids = [1, 2, 3]

    new_research_context_DTO: NewResearchContextDTO = sqla_client_repository.new_research_context(
        research_context_title=research_context_title,
        research_context_description=research_context_description,  # type: ignore
        client_sub=client_sub,
        agent_id=agent_id,
        source_data_ids=source_data_ids,
    )

    assert new_research_context_DTO.status == False
    assert new_research_context_DTO.errorCode == -1
    assert new_research_context_DTO.errorName == "Research context description not provided"
    assert new_research_context_DTO.errorType == "ResearchContextDescriptionNotProvided"


def test_error_new_research_context_client_sub_is_None(
    app_initialization_container: ApplicationContainer, db_session: TDatabaseFactory
) -> None:
    sqla_client_repository = app_initialization_container.sqla_client_repository()

    research_context_title = "test"
    research_context_description = "Test description"
    client_sub = None
    agent_id = 1
    source_data_ids = [1, 2, 3]

    new_research_context_DTO: NewResearchContextDTO = sqla_client_repository.new_research_context(
        research_context_title=research_context_title,
        research_context_description=research_context_description,
        client_sub=client_sub,  # type: ignore
        agent_id=agent_id,
        source_data_ids=source_data_ids,
    )

    assert new_research_context_DTO.status == False
    assert new_research_context_DTO.errorCode == -1
    assert new_research_context_DTO.errorName == "Client SUB not provided"
    assert new_research_context_DTO.errorType == "ClientSubNotProvided"


def test_error_new_research_context_agent_name_is_None(
    app_initialization_container: ApplicationContainer, db_session: TDatabaseFactory
) -> None:
    sqla_client_repository = app_initialization_container.sqla_client_repository()

    research_context_title = "test"
    research_context_description = "Test description"
    client_sub = "test"
    agent_id = None
    source_data_ids = [1, 2, 3]

    new_research_context_DTO: NewResearchContextDTO = sqla_client_repository.new_research_context(
        research_context_title=research_context_title,
        research_context_description=research_context_description,
        client_sub=client_sub,
        agent_id=agent_id,  # type: ignore
        source_data_ids=source_data_ids,
    )

    assert new_research_context_DTO.status == False
    assert new_research_context_DTO.errorCode == -1
    assert new_research_context_DTO.errorName == "Agent ID not provided"
    assert new_research_context_DTO.errorType == "AgentIDNotProvided"


def test_error_new_research_context_client_sub_not_found(
    app_initialization_container: ApplicationContainer,
    db_session: TDatabaseFactory,
    fake_agent: SQLAAgent,
) -> None:
    sqla_client_repository = app_initialization_container.sqla_client_repository()

    agent = fake_agent
    agent_name = agent.name

    research_context_title = "test"
    research_context_description = "Test description"
    client_sub = f"test-{uuid.uuid4()}"
    source_data_ids = [1, 2, 3]

    with db_session() as session:
        session.add(agent)
        session.commit()

        agent_id = agent.id
        new_research_context_DTO: NewResearchContextDTO = sqla_client_repository.new_research_context(
            research_context_title=research_context_title,
            research_context_description=research_context_description,
            client_sub=client_sub,
            agent_id=agent_id,
            source_data_ids=source_data_ids,
        )

        assert new_research_context_DTO.status == False
        assert new_research_context_DTO.errorCode == -1
        assert new_research_context_DTO.errorName == "Client not found"
        assert new_research_context_DTO.errorType == "ClientNotFound"


def test_error_new_research_context_agent_id_not_found(
    app_initialization_container: ApplicationContainer,
    db_session: TDatabaseFactory,
    fake_client: SQLAClient,
) -> None:
    sqla_client_repository = app_initialization_container.sqla_client_repository()

    client = fake_client
    client_sub = client.sub

    irrealistic_agent_id = 9999999999999

    research_context_title = "test"
    research_context_description = "Test description"
    source_data_ids = [1, 2, 3]

    with db_session() as session:
        session.add(client)
        session.commit()

        new_research_context_DTO: NewResearchContextDTO = sqla_client_repository.new_research_context(
            research_context_title=research_context_title,
            research_context_description=research_context_description,
            client_sub=client_sub,
            agent_id=irrealistic_agent_id,
            source_data_ids=source_data_ids,
        )

        assert new_research_context_DTO.status == False
        assert new_research_context_DTO.errorCode == -1
        assert new_research_context_DTO.errorName == "Agent not found"
        assert new_research_context_DTO.errorType == "AgentNotFound"


def test_error_new_research_context_source_data_ids_not_found(
    app_initialization_container: ApplicationContainer,
    db_session: TDatabaseFactory,
    fake_client: SQLAClient,
    fake_agent: SQLAAgent,
) -> None:
    sqla_client_repository = app_initialization_container.sqla_client_repository()

    client = fake_client
    agent = fake_agent
    client_sub = client.sub
    agent_name = agent.name

    research_context_title = "test"
    research_context_description = "Test description"
    source_data_ids = [999999999]

    with db_session() as session:
        session.add(client)
        session.add(agent)
        session.commit()

        agent_id = agent.id

        new_research_context_DTO: NewResearchContextDTO = sqla_client_repository.new_research_context(
            research_context_title=research_context_title,
            research_context_description=research_context_description,
            client_sub=client_sub,
            agent_id=agent_id,
            source_data_ids=source_data_ids,
        )

        sqla_source_data_error_dict = {}
        for sd_id in source_data_ids:
            sqla_source_data_error_dict[f"ID {sd_id}"] = f"Source data not found in the database"

        error_message = f"Error with the following source data. Operation aborted.\n\n {sqla_source_data_error_dict}"

        assert new_research_context_DTO.status == False
        assert new_research_context_DTO.errorCode == -1
        assert new_research_context_DTO.errorMessage == error_message
        assert new_research_context_DTO.errorName == "Source data database errors"
        assert new_research_context_DTO.errorType == "SourceDataDatabaseErrors"
