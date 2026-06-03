from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


SourceType = Literal["text", "image", "url"]


class MealAnalysisResult(BaseModel):
    id: str
    mealName: str
    mealType: str
    estimatedCalories: float
    estimatedProtein: float
    tags: list[str]
    mainIngredients: list[str]
    allergens: list[str]
    recommendationReason: str
    confidence: float = Field(ge=0, le=1)
    sourceType: SourceType
    createdAt: str
    isAiGenerated: bool


class TextAnalyzeRequest(BaseModel):
    description: str


class UrlAnalyzeRequest(BaseModel):
    url: HttpUrl


class RecommendRequest(BaseModel):
    healthGoal: str
    tags: list[str]
    excludedIngredients: list[str]
    keyword: str | None = None
