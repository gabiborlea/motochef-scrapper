import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://rennlist.com/forums/cayenne-9y0-2019/1415806-tutorial-lithium-battery-conversion-to-agm.html",
        )
        print(result.markdown)  # Show the first 300 characters of extracted 

if __name__ == "__main__":
    asyncio.run(main())
