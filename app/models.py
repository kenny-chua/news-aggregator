from sqlmodel import Field, SQLModel
from typing import NamedTuple, Optional


# Define a named tuple for api data extraction
class RawHeadline(NamedTuple):
    published_at: str
    source_id: Optional[str]
    source_name: Optional[str]
    author: Optional[str]
    url: str
    title: str
    subheading: Optional[str]


# Define the SQLModel class for top headlines
class TopHeadline(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    published_at: str
    source_id: Optional[str] = Field(default=None)
    source_name: Optional[str] = Field(default=None)
    author: Optional[str] = Field(default=None)
    url: str = Field(unique=True)
    content: Optional[str] = Field(default=None)
    title: str
    subheading: Optional[str] = Field(default=None)
    sentiment: Optional[str] = Field(default=None)
    political_class: Optional[str] = Field(default=None)
    bias: Optional[str] = Field(default=None)
