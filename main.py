from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, JsonCssExtractionStrategy
import asyncio
import json

async def get_post_page_number_and_title(url):
    config = CrawlerRunConfig(
        css_selector='#mb_page',
        cache_mode=CacheMode.DISABLED
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        pages = result.markdown.replace(' ', '').replace('\n', '').split('/')
        pages = int(pages[len(pages) - 1])
        title = result.metadata['title']
        return pages, title


async def save_page_markdown(url, title):
    config = CrawlerRunConfig(
        excluded_tags=['header', 'img', 'a', 'b', 'nav', 'div.thead', 'span'],
        css_selector='.tpost .trow .tcell.alt1 div',
        excluded_selector='.widget_trending_showthread_list',
        cache_mode=CacheMode.DISABLED
    )
    
    async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)
            try: 
                f = open('markdowns/' + title + '.md', 'a')
                f.write(url + '\n' + result.markdown.replace('\n', '\n\n'))
                f.close()
            except Exception:
                print('error')
                
async def save_post(url):
    post_page_number, post_title = await get_post_page_number_and_title(url)   
    for i in range(1, post_page_number + 1):
        post_page = url.replace('.html', f'-{i}.html')
        await save_page_markdown(post_page, post_title)

async def get_list_page_number(url):
    config = CrawlerRunConfig(
        css_selector='.pagenav .vbmenu_control',
        cache_mode=CacheMode.DISABLED
    )
    
    
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        pages = result.markdown.split(' ')
        pages = int(pages[len(pages) - 1])
        return pages

async def get_list_links(url):
    schema = {
        "name": "Links",
        "baseSelector": "h4",
        "fields": [
            {
                "name": "href",
                "selector": "a",
                "type": "attribute",
                "attribute": "href"
            },
        ]
    }

    
    config = CrawlerRunConfig(
        css_selector='h4 a',
        cache_mode=CacheMode.DISABLED,
        extraction_strategy=JsonCssExtractionStrategy(schema)
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=config)
        links = json.loads(result.extracted_content)
        return links
    
    
async def run_all_pages_crawler(url):
    pages = await get_list_page_number(url)
    
    for page in range(1, pages + 1):
        page_url = url[:-1] + (f'-{page}.html' if page != 1 else '/')
        links = await get_list_links(page_url) 
        for link in links:
            await save_post(link['href'])
            
            
async def run_one_page_crawler(url):
    links = await get_list_links(url) 
    for link in links:
        await save_post(link['href'])
    
            
def main():
    asyncio.run(run_all_pages_crawler("https://rennlist.com/forums/cayenne-9y0-2019-247/"))

if __name__ == "__main__":
    main()