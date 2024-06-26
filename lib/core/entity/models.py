from enum import Enum
import os
import re
import uuid
from pydantic import BaseModel, field_validator
from typing import Any, TypeVar
from datetime import datetime


class KnowledgeSourceEnum(Enum):
    """
    Enum for the different knowledge sources that can be used to create a research context.

    TELEGRAM: the knowledge source is a Telegram channel
    TWITTER: the knowledge source is a Twitter account
    AUGMENTED: the knowledge source is a collection of user uploads
    SENTINEL: the knowledge source is a collection of user uploads, and the user wants to be notified when new uploads are available
    USER: the knowledge source is a collection of user uploads
    """

    TELEGRAM = "telegram"
    TWITTER = "twitter"
    AUGMENTED = "augmented"
    SENTINEL = "sentinel"
    USER = "user"


class ProtocolEnum(Enum):
    """
    Enum for the different protocols that can be used to store a source_data.

    S3: the source_data is stored in an S3 bucket
    NAS: the source_data is stored in a NAS
    LOCAL: the source_data is stored locally
    """

    S3 = "s3"
    NAS = "nas"
    LOCAL = "local"


class SourceDataStatusEnum(Enum):
    """
    Enum for the different status that a source data can have.

    CREATED: the source data has been created
    UNAVAILABLE: the source data is not available
    AVAILABLE: the source data is available and part of a consistent dataset
    INCONSISTENT_DATASET: the source data is available but part of an inconsistent dataset
    """

    CREATED = "created"
    UNAVAILABLE = "unavailable"
    AVAILABLE = "available"
    INCONSISTENT_DATASET = "inconsistent_dataset"


class LFN(BaseModel):
    """
    Represents a Logical File Name, used to store files in a consistent way, regardless of the protocol used

    @param protocol: the protocol used to store the source_data
    @param tracer_id: the id of the user that uploaded the source_data
    @param job_id: the id of the job that created the source_data
    @param source: the source of the source_data (e.g., Twitter, Telegram, etc.)
    @param relative_path: the relative path of the source_data
    """

    protocol: ProtocolEnum
    tracer_id: str
    job_id: int
    source: KnowledgeSourceEnum
    relative_path: str

    @field_validator("relative_path")
    def relative_path_must_be_alphanumberic_underscores_backslashes(cls, v: str) -> str:
        marker = "sdamarker"
        if marker not in v:
            v = os.path.basename(v)  # Take just the basename, saner for the object stores
            v = re.sub(r"[^a-zA-Z0-9_\./-]", "", v)
            ext = v.split(".")[-1]
            name = v.split(".")[0]  # this completely removes dots
            seed = f"{uuid.uuid4()}".replace("-", "")
            v = f"{name}-{seed}-{marker}.{ext}"
        return v

    def to_json(cls) -> str:
        """
        Dumps the model to a json formatted string. Wrapper around pydantic's model_dump_json method: in case they decide to deprecate it, we only refactor here.
        """
        return cls.model_dump_json()

    def __str__(self) -> str:
        return self.to_json()

    @classmethod
    def from_json(cls, json_str: str) -> "LFN":
        """
        Loads the model from a json formatted string. Wrapper around pydantic's model_validate_json method: in case they decide to deprecate it, we only refactor here.
        """
        return cls.model_validate_json(json_data=json_str)


class BaseKernelPlancksterModel(BaseModel):
    """
    Base class for all models in the project

    @param created_at: the datetime when the model was created
    @param updated_at: the datetime when the model was last updated
    """

    created_at: datetime
    updated_at: datetime

    def to_json(cls) -> str:
        """
        Dumps the model to a json formatted string. Wrapper around pydantic's model_dump_json method: in case they decide to deprecate it, we only refactor here.
        """
        return cls.model_dump_json()

    def __str__(self) -> str:
        return self.to_json()


class BaseSoftDeleteKernelPlancksterModel(BaseKernelPlancksterModel):
    """
    Base class for all models in the project that can be soft deleted

    @param deleted: whether the model is deleted or not
    @param deleted_at: the datetime when the model was deleted
    """

    deleted: bool
    deleted_at: datetime | None


class User(BaseSoftDeleteKernelPlancksterModel):
    """
    Represents a user in the system

    @param id: the id of the user
    @type id: int
    @param sid: the sid of the user
    @type sid: str
    """

    id: int
    sid: str


class KnowledgeSource(BaseSoftDeleteKernelPlancksterModel):
    """
    Represents a knowledge source, a collection of sources defined by the user

    @param id: the id of the knowledge source
    @param source: the source of the source_data (e.g., Twitter, Telegram, etc.)
    @param content_metadata: depending on the source, can be the query made to the source or the list of user uploads; meant to be a json formatted string, including e.g. an URL
    """

    id: int
    source: KnowledgeSourceEnum
    content_metadata: str


class SourceData(BaseSoftDeleteKernelPlancksterModel):
    """
    Represents a source_data or a file

    @param id: the id of the source_data
    @param name: the name of the source_data
    @param type: the type of the source_data (e.g., pdf, txt, etc.)
    @param lfn: the logical file name of the source_data
    @param protocol: the protocol used to store the source_data
    @param status: the status of the source_data
    """

    id: int
    name: str
    type: str
    lfn: LFN
    status: SourceDataStatusEnum

    @classmethod
    def from_json(cls, json_str: str) -> "SourceData":
        """
        Loads the model from a json formatted string. Wrapper around pydantic's model_validate_json method: in case they decide to deprecate it, we only refactor here.
        """
        return cls.model_validate_json(json_data=json_str)


class EmbeddingModel(BaseSoftDeleteKernelPlancksterModel):
    """
    An embedding model is a model that can be used to embed a vector storde associated with a research context (including its source data), into a vector space

    @param id: the id of the embedding model
    @param name: the name of the embedding model
    """

    id: int
    name: str


class LLM(BaseSoftDeleteKernelPlancksterModel):
    """
    A LLM (Language Learning Model) is a model that can be used to generate a response to a user query, given a vectorized research context

    @param id: the id of the LLM
    @param name: the name of the LLM
    """

    id: int
    llm_name: str


class ResearchContext(BaseSoftDeleteKernelPlancksterModel):
    """
    A research context belongs to a research topic, and is defined using a subset of the collection of source_data of the research topic
    This is the context in which conversations will happen

    @param id: the id of the research context
    @param title: the title of the research context
    @param description: the description of the research context
    """

    id: int
    title: str
    description: str


class VectorStore(BaseSoftDeleteKernelPlancksterModel):
    """
    Represents a vector store, a vectorization of a research context to be inputted to an LLM

    @param id: the id of the vector store
    @param name: the name of the vector store
    @param lfn: the logical file name of the vector store
    """

    id: int
    name: str
    lfn: LFN


class Conversation(BaseSoftDeleteKernelPlancksterModel):
    """
    Represents a conversation between a user and an agent, within in a research context
    This is where messages will be exchanged

    @param id: the id of the conversation
    @param title: the title of the conversation
    """

    id: int
    title: str


class MessageSenderTypeEnum(Enum):
    """
    Enum for the different types of sender of messages

    USER: the sender is a user
    AGENT: the sender is an agent
    """

    USER = "user"
    AGENT = "agent"


class MessageBase(BaseSoftDeleteKernelPlancksterModel):
    """
    Base class for user queries and agent responses

    @param id: the id of the message
    @type id: int
    @param content: the content of the message
    @type content: str
    @param timestamp: the datetime when the message was sent
    @type timestamp: datetime
    @param sender: the name of the sender of the message
    @type sender: str
    @param sender_type: the type of the sender of the message
    @type sender_type: MessageSenderTypeEnum
    """

    id: int
    content: str
    timestamp: datetime
    sender: str
    sender_type: MessageSenderTypeEnum


TMessageBase = TypeVar("TMessageBase", bound=MessageBase)


class UserMessage(MessageBase):
    """
    Represents the query of a user to an agent
    """

    sender_type: MessageSenderTypeEnum = MessageSenderTypeEnum.USER


class AgentMessage(MessageBase):
    """
    Represents the response to a user query
    It will be tied to citations that the LLM made to generate the response, and to an LLM directly
    """

    sender_type: MessageSenderTypeEnum = MessageSenderTypeEnum.AGENT


class Citation(BaseSoftDeleteKernelPlancksterModel):
    """
    Represents a citation for a part of a source_data, in an agent's response to a user query

    @param id: the id of the citation
    @param citation_metadata: the position of the citation in the source_data; TODO: meant to be a json formatted string
    """

    id: int
    citation_metadata: str
