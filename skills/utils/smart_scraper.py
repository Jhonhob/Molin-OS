"""
AI 友好型智能网页采集器 (Smart Scraper)
===========================================
汲取 Crawl4AI 的设计精髓，将脆弱爬虫升级为高鲁棒性采集器。
自动剔除导航栏、Footer、广告弹窗等噪声，
输出干净结构化 Markdown，直接喂给大模型。

（实际落地时安装沙箱: pip install crawl4ai）

用法：
    from skills.utils.smart_scraper import MolinSmartScraper
    scraper = MolinSmartScraper()
    result = await scraper.scrape_and_clean("https://example.com")
"""

import asyncio
import re
import json
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# 确保 molib 可导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class MolinSmartScraper:
    """AI 专用重型采集器 — 网页 → 纯净 Markdown"""

    # HTML 噪声标签（被剔除的元素）
    NOISE_TAGS = {
        "nav", "footer", "header", "aside", "script", "style",
        "noscript", "iframe", "form", "button", "select", "input",
    }
    # 常见噪声类名/id 模式
    NOISE_PATTERNS = [
        r"\b(ad|ads|advert|banner|popup|modal|overlay|sidebar|widget|social|share|comment|related|recommend|sponsored|cookie|gdpr)\b",
    ]

    def __init__(self, use_headless: bool = True, timeout: int = 30):
        self.use_headless = use_headless
        self.timeout = timeout
        self._crawl4ai_available = False
        try:
            import crawl4ai  # noqa: F401
            self._crawl4ai_available = True
        except ImportError:
            pass

    async def scrape_and_clean(self, url: str) -> dict:
        """
        抓取并清洗网页。

        Returns:
            {"status": "success", "url": ..., "raw_markdown": ..., "metadata": ...}
        """
        # 优先使用 crawl4ai（沙箱）
        if self._crawl4ai_available:
            return await self._scrape_via_crawl4ai(url)

        # 降级：使用 aiohttp + BeautifulSoup 本地清洗
        return await self._scrape_local(url)

    async def _scrape_via_crawl4ai(self, url: str) -> dict:
        """通过 crawl4ai 抓取（沙箱环境）"""
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

        config = CrawlerRunConfig(
            excluded_tags=list(self.NOISE_TAGS),
            exclude_external_links=True,
            remove_overlay_elements=True,
            word_count_threshold=10,
        )

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)

        if not result.success:
            return {"status": "failed", "url": url, "error": result.error_message}

        return {
            "status": "success",
            "url": url,
            "raw_markdown": result.markdown,
            "metadata": {
                "title": result.metadata.get("title", ""),
                "length_chars": len(result.markdown),
                "length_tokens": len(result.markdown.split()),
                "engine": "crawl4ai",
            },
        }

    async def _scrape_local(self, url: str) -> dict:
        """本地降级方案：aiohttp + 手工清洗"""
        try:
            import aiohttp
        except ImportError:
            return {"status": "failed", "url": url, "error": "aiohttp not installed"}

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(url, headers=headers, allow_redirects=True) as resp:
                    if resp.status != 200:
                        return {"status": "failed", "url": url, "error": f"HTTP {resp.status}"}
                    html = await resp.text()
        except Exception as e:
            return {"status": "failed", "url": url, "error": str(e)}

        # 清洗 HTML → 纯文本 Markdown
        cleaned = self._clean_html(html, url)
        return {
            "status": "success",
            "url": url,
            "raw_markdown": cleaned,
            "metadata": {
                "title": self._extract_title(html),
                "length_chars": len(cleaned),
                "length_tokens": len(cleaned.split()),
                "engine": "local",
            },
        }

    def _clean_html(self, html: str, source_url: str) -> str:
        """手工清洗 HTML → 纯净 Markdown"""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            # 无 BeautifulSoup → 退化到正则清洗
            return self._regex_clean(html)

        soup = BeautifulSoup(html, "html.parser")

        # 1. 删除噪声标签
        for tag_name in self.NOISE_TAGS:
            for el in soup.find_all(tag_name):
                el.decompose()

        # 2. 删除噪声类名
        for pattern in self.NOISE_PATTERNS:
            for el in soup.find_all(class_=re.compile(pattern, re.I)):
                el.decompose()
            for el in soup.find_all(id=re.compile(pattern, re.I)):
                el.decompose()

        # 3. 提取主要正文
        main = soup.find("main") or soup.find("article") or soup.body
        if main is None:
            return self._regex_clean(html)

        # 4. 保留有意义的文本标签
        allowed = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "td", "th", "blockquote", "pre", "code"}
        lines = []
        for el in main.descendants:
            if el.name in allowed and el.get_text(strip=True):
                text = el.get_text(" ", strip=True)
                if len(text) > 5:  # 过滤太短的文本
                    prefix = "#" * int(el.name[1]) + " " if el.name.startswith("h") else ""
                    lines.append(f"{prefix}{text}")

        domain = urlparse(source_url).netloc
        return f"# {self._extract_title(soup) or domain}\n\n" + "\n\n".join(lines)

    def _regex_clean(self, html: str) -> str:
        """退化正则清洗（无 BeautifulSoup 时）"""
        # 移除 script/style
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.I)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.I)
        html = re.sub(r"<noscript[^>]*>.*?</noscript>", "", html, flags=re.DOTALL | re.I)
        # 移除 HTML 标签，保留文本
        html = re.sub(r"<[^>]+>", " ", html)
        # 压缩空白
        html = re.sub(r"\s+", " ", html).strip()
        return html

    def _extract_title(self, soup_or_html) -> str:
        """提取页面标题"""
        try:
            from bs4 import BeautifulSoup
            if isinstance(soup_or_html, BeautifulSoup):
                title = soup_or_html.find("title")
                return title.get_text(strip=True) if title else ""
        except ImportError:
            pass
        match = re.search(r"<title[^>]*>(.*?)</title>", str(soup_or_html), re.I | re.DOTALL)
        return match.group(1).strip() if match else ""

    # ── 批量采集 ────────────────────────────────

    async def batch_scrape(self, urls: list[str], concurrency: int = 3) -> list[dict]:
        """并发批量采集"""
        sem = asyncio.Semaphore(concurrency)

        async def _scrape_one(url):
            async with sem:
                return await self.scrape_and_clean(url)

        tasks = [_scrape_one(u) for u in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
