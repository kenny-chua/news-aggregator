from sqlmodel import SQLModel, Field
from typing import NamedTuple, Optional


# Define a named tuple for api data extraction
class RawHeadline(NamedTuple):
    source_id: Optional[str]
    source_name: Optional[str]
    author: Optional[str]
    title: str
    description: Optional[str]
    url: str
    url_to_image: Optional[str]
    published_at: str


# Define the SQLModel class for top headlines
class TopHeadline(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: Optional[str] = Field(default=None)
    url: str = Field(unique=True)
    content: Optional[str] = Field(default=None)
    source_name: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    title: str
    description: Optional[str] = Field(default=None)
    url_to_image: Optional[str] = Field(default=None)
    published_at: str
    sentiment: Optional[str] = Field(default=None)
    bias: Optional[str] = Field(default=None)
