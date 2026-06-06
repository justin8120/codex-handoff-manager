import os
import json
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models import MealAnalysisResult, RecommendRequest, TextAnalyzeRequest, UrlAnalyzeRequest
from app.services import openai_meal_analyzer
from app.storage.meals_store import add_meal, load_meals, recommend_meals


load_dotenv()


class UnicodeEscapedJSONResponse(JSONResponse):
    def render(self, content: object) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_meals()
    yield


app = FastAPI(
    title="Smart Diet Recommendation API",
    lifespan=lifespan,
    default_response_class=UnicodeEscapedJSONResponse,
)

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[*frontend_origins, "http://localhost:4173", "http://localhost:4174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        **openai_meal_analyzer.provider_status(),
    }


@app.post("/api/analyze/text", response_model=MealAnalysisResult)
def analyze_text(request: TextAnalyzeRequest) -> MealAnalysisResult:
    return openai_meal_analyzer.analyze_text(request.content)


@app.post("/api/analyze/image", response_model=MealAnalysisResult)
async def analyze_image(file: UploadFile = File(...)) -> MealAnalysisResult:
    return await openai_meal_analyzer.analyze_image(file)


@app.post("/api/analyze/url", response_model=MealAnalysisResult)
async def analyze_url(request: UrlAnalyzeRequest) -> MealAnalysisResult:
    return await openai_meal_analyzer.analyze_url(str(request.url))


@app.get("/api/meals", response_model=list[MealAnalysisResult])
def get_meals() -> list[MealAnalysisResult]:
    return load_meals()


@app.post("/api/meals", response_model=MealAnalysisResult)
def create_meal(meal: MealAnalysisResult) -> MealAnalysisResult:
    return add_meal(meal)


@app.post("/api/recommend", response_model=list[MealAnalysisResult])
def recommend(request: RecommendRequest) -> list[MealAnalysisResult]:
    return recommend_meals(
        health_goal=request.healthGoal,
        tags=request.tags,
        excluded_ingredients=request.excludedIngredients,
        keyword=request.keyword,
    )
