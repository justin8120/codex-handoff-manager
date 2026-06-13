from typing import Literal

from pydantic import BaseModel, Field


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
    recommendedGoals: list[str] = Field(default_factory=list)


class MealUpsertResponse(BaseModel):
    meal: MealAnalysisResult
    action: Literal["created", "merged"]


class TextAnalyzeRequest(BaseModel):
    description: str | None = None
    text: str | None = None
    excludedIngredients: list[str] = Field(default_factory=list)

    @property
    def content(self) -> str:
        return self.description or self.text or ""


class UrlAnalyzeRequest(BaseModel):
    url: str | None = None
    excludedIngredients: list[str] = Field(default_factory=list)


class RecommendRequest(BaseModel):
    healthGoal: str
    tags: list[str]
    excludedIngredients: list[str]
    keyword: str | None = None
