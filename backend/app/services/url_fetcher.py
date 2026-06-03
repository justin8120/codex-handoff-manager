from bs4 import BeautifulSoup
import httpx


MAX_TEXT_LENGTH = 4_000


async def fetch_url_summary(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "").strip() if description_tag else ""

    for element in soup(["script", "style", "noscript", "svg"]):
        element.extract()

    body_text = " ".join(soup.get_text(" ").split())
    summary = "\n".join(
        item
        for item in [
            f"Title: {title}" if title else "",
            f"Description: {description}" if description else "",
            f"Page text: {body_text[:MAX_TEXT_LENGTH]}",
        ]
        if item
    )
    return summary[:MAX_TEXT_LENGTH]
