from typing import Optional, List, Dict
from pydantic import BaseModel, HttpUrl, Field, validator

class ScrapingServiceOutput(BaseModel):
    link: str
    status_code: Optional[int]
    html: Optional[str]
    text: Optional[str] = None  # Included based on default value in error case




# class LinkData(BaseModel):
#     href: HttpUrl
#     text: Optional[str] = Field(None, max_length=256, description="The anchor text of the link.")

# class Metadata(BaseModel):
#     title: Optional[str] = Field(None, max_length=256, description="The title of the page.")
#     description: Optional[str] = Field(None, max_length=512, description="The meta description of the page.")
#     keywords: Optional[str] = Field(None, description="The meta keywords of the page.")
#     language: Optional[str] = Field(None, regex=r'^[a-z]{2}(-[A-Z]{2})?$', description="The language code (e.g., 'en' or 'en-US').")

# class ScrapingServiceOutput(BaseModel):
#     link: HttpUrl = Field(..., description="The URL of the page.")
#     status_code: Optional[int] = Field(None, ge=100, le=599, description="The HTTP status code of the request.")
#     html: Optional[str] = Field(None, description="The raw HTML content of the page.")
#     text: Optional[str] = Field(None, description="The extracted plain text content.")
#     links: Optional[List[LinkData]] = Field(None, description="A list of links extracted from the page.")
#     metadata: Optional[Metadata] = Field(None, description="The metadata extracted from the page.")

#     @validator("text", always=True)
#     def validate_text(cls, value, values):
#         if not value and not values.get("html"):
#             raise ValueError("Either 'html' or 'text' must be provided.")
#         return value

#     @validator("links")
#     def validate_links(cls, links):
#         if links and len(links) > 1000:
#             raise ValueError("Too many links extracted; ensure the page is not overly large.")
#         return links
