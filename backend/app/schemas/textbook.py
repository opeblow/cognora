from pydantic import BaseModel, Field


class SectionPlan(BaseModel):
    index: int
    title: str
    focus: str


class TextbookPlanResponse(BaseModel):
    topic_id: str
    topic_title: str
    subject_name: str
    total_sections: int
    sections: list[SectionPlan]


class SectionContent(BaseModel):
    index: int
    title: str
    content: str
    has_content: bool


class GenerateSectionRequest(BaseModel):
    regenerate: bool = False


class GenerateSectionResponse(BaseModel):
    section_index: int
    total_sections: int
    content: str
    section_title: str
    has_more: bool


class TextbookStatusResponse(BaseModel):
    topic_id: str
    total_sections: int
    generated_sections: list[int]
    sections: list[SectionContent]
