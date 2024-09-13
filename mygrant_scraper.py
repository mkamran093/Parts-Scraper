from bs4 import BeautifulSoup

def MyGrantScraper(partNo, driver, logger):

    url = 'https://www.mygrantglass.com/pages/search.aspx?q=' + partNo + '&sc=r&do=Search'
    parts = []
    try:
        logger.info("Searching part in MyGrant: " + partNo)
        driver.get(url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()
        try:
            div = soup.find('div', {'id': 'cpsr_DivParts'})
            locations = div.find_all('h3')[1:]
            tables = div.find_all('tbody')
            for table in tables:
                rows = table.find_all('tr')[1:]
                for row in rows:
                    data = row.find_all('td')[1:]
                    part = [data[1].find('a').text.replace('\n', '').strip(), data[2].text.replace('\n', '').strip(), data[0].find('span').text.replace('\n', '').strip(), locations[0].text.split(' - ')[0].strip()]
                    parts.append(part)
                locations.pop(0)
            return parts
        except:
            print("not found")
            return None
    except:
        logger.error("Part number not found: " + partNo + " on MyGrant")
        return None        