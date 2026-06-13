import math
import os
from typing import Any

import httpx
from fastapi import HTTPException

from app.models import NearbyPlace, NearbyPlacesResponse


GOOGLE_PLACES_SEARCH_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"
DEFAULT_RADIUS_METERS = 1500
MAX_RESULTS = 5


def build_nearby_query(meal_name: str, meal_type: str, tags: list[str]) -> str:
    profile = " ".join([meal_name, meal_type, *tags])
    if any(term in profile for term in ["杜老爺", "包裝冰品"]):
        return "便利商店 超市 冰品"
    if any(term in profile for term in ["健康餐", "高蛋白", "低脂", "低油"]):
        return "健康餐 雞胸肉餐盒"
    if any(term in profile for term in ["便當", "餐盒"]):
        return "便當 餐盒"
    if any(term in profile for term in ["冰品", "甜點", "高糖"]):
        return "冰品 甜點 冰淇淋"
    if "素食" in profile:
        return "素食餐廳"
    if "早餐" in profile:
        return "早餐店"
    if "飲料" in profile:
        return "飲料店"
    if "咖啡" in profile:
        return "咖啡廳"
    if "火鍋" in profile:
        return "火鍋"
    if "麵食" in profile:
        return "麵店"
    return "餐廳"


async def search_nearby_places(
    lat: float,
    lng: float,
    meal_name: str,
    meal_type: str,
    tags: list[str],
    radius_meters: int | None = None,
) -> NearbyPlacesResponse:
    query = build_nearby_query(meal_name, meal_type, tags)
    if os.getenv("NEARBY_PROVIDER", "google").strip().lower() != "google":
        raise HTTPException(status_code=503, detail="附近店家服務尚未設定。")

    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=503, detail="附近店家服務尚未設定，請設定 GOOGLE_MAPS_API_KEY。")

    radius = radius_meters or _env_radius()
    payload = {
        "textQuery": query,
        "languageCode": "zh-TW",
        "regionCode": "TW",
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius,
            },
        },
        "maxResultCount": MAX_RESULTS,
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": (
            "places.displayName,places.formattedAddress,places.location,"
            "places.rating,places.types,places.googleMapsUri"
        ),
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(GOOGLE_PLACES_SEARCH_TEXT_URL, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="目前無法取得附近店家，請稍後再試。") from error

    data = response.json()
    return NearbyPlacesResponse(
        query=query,
        places=[_map_google_place(item, lat, lng) for item in data.get("places", [])[:MAX_RESULTS]],
    )


def _env_radius() -> int:
    try:
        return int(os.getenv("GOOGLE_PLACES_RADIUS_METERS", str(DEFAULT_RADIUS_METERS)))
    except ValueError:
        return DEFAULT_RADIUS_METERS


def _map_google_place(place: dict[str, Any], lat: float, lng: float) -> NearbyPlace:
    location = place.get("location") if isinstance(place.get("location"), dict) else {}
    place_lat = _float_or_none(location.get("latitude"))
    place_lng = _float_or_none(location.get("longitude"))
    distance = (
        round(_haversine_distance_meters(lat, lng, place_lat, place_lng), 1)
        if place_lat is not None and place_lng is not None
        else None
    )
    display_name = place.get("displayName") if isinstance(place.get("displayName"), dict) else {}
    return NearbyPlace(
        name=str(display_name.get("text") or ""),
        address=str(place.get("formattedAddress") or ""),
        rating=_float_or_none(place.get("rating")),
        distanceMeters=distance,
        types=[str(item) for item in place.get("types", []) if str(item)],
        mapUrl=str(place.get("googleMapsUri") or ""),
    )


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _haversine_distance_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    earth_radius_meters = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return earth_radius_meters * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
