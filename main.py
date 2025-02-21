from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, JsonCssExtractionStrategy
import asyncio
import json
import requests
from bs4 import BeautifulSoup

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
        print(f'Saving {url} - {i} of {post_page_number}')
        post_page = url.replace('.html', f'-{i}.html')
        await save_page_markdown(post_page, post_title)

def get_list_page_number(url):
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, 'html5lib')
    nr_pages = soup.select('.pagenav .vbmenu_control')
    if (len(nr_pages) > 0):
        nr_pages = nr_pages[0].text
        # nr_pages = int(nr_pages)
        nr_pages = nr_pages.split(' ')
        return int(nr_pages[len(nr_pages) - 1])
    
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
    print(f'Running {url}')
    links = await get_list_links(url) 
    for link in links:
        await save_post(link['href'])
    
            
async def run_multiple_pages(url, page_start, page_end):
    nr_pages = get_list_page_number(url)
    print(nr_pages)
    
    if (page_start > nr_pages):
        print("Page start is greater than the number of pages")
        return
    
    if (page_end > nr_pages):
        print("Page end is greater than the number of pages")
        return
    
    pages = []
    
    for page in range(page_start, page_end + 1):
        page_url = url[:-1] + (f'-{page}.html' if page != 1 else '/')
        pages.append(page_url)
        
    tasks = [run_one_page_crawler(url) for url in pages]
    await asyncio.gather(*tasks)

def main():
    asyncio.run(run_multiple_pages("https://rennlist.com/forums/cayenne-9y0-2019-247/", 5, 10))
    
if __name__ == "__main__":
    main()