from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)


async def ddg_definitions(
    query: str,
    max_results: int = 10,
    pause_between: float = 1.0,
    retries: int = 3,
    retry_pause: float = 2.0,
) -> list[dict[str, Any]] | None:
    await asyncio.sleep(pause_between)
    attempt = 0

    while attempt < retries:
        try:
            with DDGS() as ddgs:
                return ddgs.text(keywords=query, max_results=max_results)
            break
        except Exception:  # noqa: BLE001
            attempt += 1
            if attempt >= retries:
                return None
            await asyncio.sleep(retry_pause)
    return None


async def ddg_html_search(query: str, max_results: int = 10) -> list[dict] | None:
    """
    Повертає list[dict] виду:
    [{'title': ..., 'url': ..., 'snippet': ...}, …].
    """
    try:
        url = "https://duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        }
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, params=params, headers=headers) as resp,
        ):
            resp.raise_for_status()
            html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        results = []

        for result in soup.select("div.result")[:max_results]:
            a_title = result.select_one("a.result__a")
            title = a_title.get_text(strip=True) if a_title else ""
            url = a_title["href"] if a_title and a_title.has_attr("href") else ""

            snippet_tag = (
                result.select_one("a.result__snippet")
                or result.select_one("div.result__snippet")
                or result.select_one(".result__body .snippet")
                or result.select_one(".result__snippet")
            )
            if snippet_tag:
                snippet = " ".join(snippet_tag.stripped_strings)
                snippet = re.sub(r"\u00A0", " ", snippet)
                snippet = re.sub(r"\s+", " ", snippet).strip()
            else:
                snippet = ""

            results.append({"title": title, "href": "https:" + url, "body": snippet})  # ty:ignore[unsupported-operator]

        return results
    except Exception:
        logger.exception("Error during DuckDuckGo HTML search")
        return None


async def get(text: str) -> list[dict[str, Any]] | None:
    result = await ddg_html_search(text)
    if result is None:
        result = await ddg_definitions(text)
    return result or None
