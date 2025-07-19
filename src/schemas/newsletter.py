from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl


class InlineButton(BaseModel):
    text: str
    url: HttpUrl


class NewsletterMessage(BaseModel):
    text: Optional[str] = None
    parse_mode: Optional[Literal["HTML", "MarkdownV2"]] = "HTML"
    photo: Optional[HttpUrl] = None
    video: Optional[HttpUrl] = None
    keyboard: Optional[List[List[InlineButton]]] = None
