import time
import random
import asyncio
import csv
import aiohttp
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from utils import parse_patent


async def fetch(session, url, headers, proxy=None, delay=3):
    # Keep track of the time of the last request and the user agent used
    if not hasattr(fetch, "last_request_time"):
        fetch.last_request_time = {}
    if not hasattr(fetch, "last_user_agent"):
        fetch.last_user_agent = {}
    if not hasattr(fetch, "last_proxy_time"):
        fetch.last_proxy_time = {}

    user_agent = headers.get("User-Agent")
    current_time = time.monotonic()

    # If this is the first request with this user agent, set the last request time to now
    # if user_agent not in fetch.last_request_time:
    #     fetch.last_request_time[user_agent] = current_time
    # # Calculate the time elapsed since the last request with this user agent
    # else:
    #     elapsed_time = current_time - fetch.last_request_time[user_agent]
    #     # If less than delay seconds have elapsed, add a delay
    #     if elapsed_time < delay:
    #         await asyncio.sleep(delay - elapsed_time)
    #     # Update the last request time for this user agent
    #     fetch.last_request_time[user_agent] = current_time

    if proxy not in fetch.last_proxy_time:
        fetch.last_proxy_time[proxy] = current_time
    # Calculate the time elapsed since the last request with this proxy
    else:
        elapsed_time = current_time - fetch.last_proxy_time[proxy]
        # If less than 3 seconds have elapsed, add a delay
        if elapsed_time < delay:
            await asyncio.sleep(delay - elapsed_time)
        # Update the last request time for this proxy
        fetch.last_proxy_time[proxy] = current_time

    async with session.get(url, headers=headers, proxy=proxy) as response:
        html = await response.text()
        return html


async def parse(url, headers, proxy=None):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url, headers, proxy=proxy)
        number_of_patent = url.split("=")[2].split("&")[0]
        soup = BeautifulSoup(html, "lxml")
        parsed_info = parse_patent(soup, number_of_patent)
        return parsed_info


async def main(urls, user_agents, proxies):
    results = []
    tasks = []

    async with aiohttp.ClientSession() as session:
        for url in urls:
            headers = random.choice(user_agents)
            proxy = random.choice(proxies) if proxies else None
            task = asyncio.ensure_future(parse(url, headers, proxy=proxy))
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)

    # write the parsed information to a csv file
    # with open("data.csv", "a", newline="", encoding="utf-8") as file:
    #     writer = csv.writer(file)
    #     header = [
    #         "number",
    #         "date",
    #         "quotes",
    #         "authors",
    #         "patent_owner",
    #         "mpk",
    #         "spk",
    #         "country",
    #         "type_of_document",
    #         "title",
    #         "abstract",
    #         "patent_claims",
    #         "patent_description",
    #         "source_of_information",
    #     ]
    #     writer.writerows([header])
    #     writer.writerows(results)

    print([i[1] for i in results])


import datetime

if __name__ == "__main__":
    start_number = 2006534
    n_batch = 10
    links = [
        f"https://new.fips.ru/registers-doc-view/fips_servlet?DB=RUPAT&DocNumber={i}&TypeFile=html"
        for i in range(start_number, start_number + n_batch)
    ]

    n_user_agents = 2
    software_names = [SoftwareName.CHROME.value]
    operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
    user_agent_rotator = UserAgent(
        software_names=software_names, operating_systems=operating_systems
    )

    user_agents = [
        {"User-Agent": user_agent_rotator.get_random_user_agent()}
        for i in range(n_user_agents)
    ]

    proxies = [
        # "http://103.127.1.130:80",
        "http://212.46.230.102:6969",
        # "http://47.113.203.122:5001",
    ]


    print(datetime.datetime.now())
    start_time = time.time()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(links, user_agents, proxies))

    end_time = time.time()
    print(datetime.datetime.now())
    print(
        f"Затраченное время: {round(end_time-start_time, 2)}; Количество спарсенных патентов: {n_batch}"
    )
