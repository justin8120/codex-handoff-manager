import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.models import MealAnalysisResult, RecommendRequest, TextAnalyzeRequest, UrlAnalyzeRequest
from app.services import openai_meal_analyzer
from app.storage.meals_store import add_meal, load_meals, recommend_meals


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_meals()
    yield


app = FastAPI(title="Smart Diet Recommendation API", lifespan=lifespan)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:4173", "http://localhost:4174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "aiConfigured": openai_meal_analyzer.is_configured(),
        "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    }


@app.post("/api/analyze/text", response_model=MealAnalysisResult)
def analyze_text(request: TextAnalyzeRequest) -> MealAnalysisResult:
    return openai_meal_analyzer.analyze_text(request.description)


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
