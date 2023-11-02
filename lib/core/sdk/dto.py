from typing import Any, Generic, List, Optional, Literal, Type, TypeVar
from pydantic import BaseModel

from lib.core.entity.models import BaseKernelPlancksterModel


TBaseKernelPlancksterModel = TypeVar("TBaseKernelPlancksterModel", bound=BaseKernelPlancksterModel)


class BaseDTO(BaseModel, Generic[TBaseKernelPlancksterModel]):
    """
    A base DTO class for the project

    @param status: The status of the operation, with True meaning 'success' and False meaning 'error'
    @type status: bool
    @param errorCode: The error code of the operation
    @type errorCode: Optional[int]
    @param errorMessage: The error message of the operation
    @type errorMessage: Optional[str]
    @param errorName: The error name of the operation
    @type errorName: Optional[str]
    @param errorType: The error type of the operation
    @type errorType: Literal["gateway_endpoint_error"] | Literal["database_error"] | str | None
    @param data: The data of the operation, representing a core entity
    @type data: Optional[TBaseModel]
    """

    status: bool
    errorCode: Optional[int] = None
    errorMessage: Optional[str] = None
    errorName: Optional[str] = None
    errorType: Literal["gateway_endpoint_error"] | Literal["database_error"] | str | None = None
    data: TBaseKernelPlancksterModel | List[TBaseKernelPlancksterModel] | None | List[None] = None


TBaseDTO = TypeVar("TBaseDTO", bound=BaseDTO[BaseKernelPlancksterModel])


def generate_error_dto_and_message(
    DTO: Any,  # TODO: Find a way of typing that this has to be the same DTO as the one that is returned
    entity: Type[TBaseKernelPlancksterModel],
    errorCode: int,
    attribute: str | None = None,
    attribute_value: Any | None = None,
    missing_data: str | None = None,
) -> Any:
    """
    Dynamically creates an error DTO for and an error message to be logged

    @param DTO: The DTO to be created
    @type DTO: Type[BaseDTO[TBaseKernelPlancksterModel]]
    @param entity: The entity that the DTO is created for
    @type entity: Type[BaseKernelPlancksterModel]
    @param errorCode: The error code of the error DTO
    @type errorCode: int
    @param attribute: The attribute of the entity that the error DTO is created for
    @type attribute: str | None
    @param attribute_value: The attribute value of the entity that the error DTO is created for
    @type attribute_value: Any | None
    @param missing_data: The missing data of the entity that the error DTO is created for
    @type missing_data: str | None
    """

    if errorCode not in range(-3, 0):
        raise ValueError(f"Error code {errorCode} is not valid")

    if attribute is not None and attribute.lower() not in ["id", "sid"]:
        raise ValueError(f"Attribute {attribute} is not valid")

    entity_name = entity.__class__.__name__

    if attribute is not None:
        attribute_name = attribute.lower().capitalize()
    if attribute is not None and attribute.lower() is "id" or "sid":
        attribute_name = attribute.upper()  # type: ignore

    if attribute_value is not None:
        attribute_value = str(attribute_value)

    if errorCode == -1:
        # Attribute value passed for the query to the database is None
        if attribute is None:
            raise ValueError(f"Attribute cannot be None for error code {errorCode}")

        message = f"{attribute_name.upper()} cannot be None"
        name = f"{attribute_name.upper()} not provided"
        type = f"{attribute_name.capitalize()}NotProvided"

    if errorCode == -2:
        # Entity with attribute doesn't exist in the database
        if attribute is None:
            raise ValueError(f"Attribute cannot be None for error code {errorCode}")
        if attribute_value is None:
            raise ValueError(f"Attribute value cannot be None for error code {errorCode}")

        message = f"with {attribute_name} {attribute_value} not found in the database"
        name = "not found"
        type = "NotFound"

    if errorCode == -3:
        # Entity with attribute has no missing_data
        if attribute is None:
            raise ValueError(f"Attribute cannot be None for error code {errorCode}")
        if missing_data is None:
            raise ValueError(f"Missing data cannot be None for error code {errorCode}")

        message = f"with {attribute_name} {attribute_value} has no {missing_data}"
        errorName = f"has no {missing_data}"
        errorType = f"HasNo{missing_data.title().strip()}"

    errorMessage = f"{entity_name} {message}"
    errorName = f"{entity_name} {name}"
    errorType = f"{entity_name}{type}"

    errorDTO = DTO(
        status=False, errorCode=errorCode, errorMessage=errorMessage, errorName=errorName, errorType=errorType
    )

    return errorDTO
