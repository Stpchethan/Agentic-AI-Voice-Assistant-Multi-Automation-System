from langchain_core.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """Search the web for recent information about a topic. Return titles, URLs, and snippets."""
    try:
        results = tavily.search(query=query, max_results=5)

        out = []

        for r in results.get("results", []):
            out.append(
                f'Title: {r.get("title", "No title")}\n'
                f'URL: {r.get("url", "No URL")}\n'
                f'Snippet: {r.get("content", "")[:300]}\n'
            )

        return "\n--------\n".join(out) if out else "No search results found."

    except Exception as e:
        return f"Web search failed: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return f"Failed to retrieve page. Status code: {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")

        summary_section = soup.find("div", class_="summary")

        if summary_section:
            return summary_section.get_text(separator=" ", strip=True)[:3000]

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if not text:
            return "No readable content found. The website may block scraping."

        return text[:3000]

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"


# Test only when running this file directly
if __name__ == "__main__":
    print(
        scrape_url.invoke(
            "https://indianexpress.com/section/technology/artificial-intelligence/"
        )
    )