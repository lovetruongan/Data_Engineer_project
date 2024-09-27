import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json

# Helper function to get job information
def get_info(url, chromepath):
    job_description = None
    job_requirement = None

    service = Service(executable_path=chromepath)
    driver = webdriver.Chrome(service=service)
    driver.get(url)

    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.sc-b8164b97-1.fkbCtV.vnwLayout__container')))

    time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    job_title = soup.find('h1', class_='sc-df6f4dcb-0 bsKseP')
    company_name = soup.find('a', class_='sc-df6f4dcb-0 dIdfPh sc-f0821106-0 gWSkfE')
    deadline = soup.find('span', class_='sc-df6f4dcb-0 bgAmOO')
    salary = soup.find('span', class_ = 'sc-df6f4dcb-0 iOaLcj')
    location = soup.find('div', class_='sc-a137b890-1 joxJgK')

    job_title = job_title.text.strip() if job_title else 'N/A'
    company_name = company_name.text.strip() if company_name else 'N/A'
    deadline = deadline.text.strip() if deadline else 'N/A'
    salary = salary.text.strip() if salary else 'N/A'
    location = location.text.strip() if location else 'N/A'

    job_detail = soup.find_all('div', class_='sc-4913d170-4 jSVTbX')

    for detail in job_detail:
        if 'Mô tả công việc' == detail.find('h2', class_ = 'sc-4913d170-5 kKmzVC').text.strip():
            job_description = detail.find('div', class_='sc-4913d170-6 hlTVkb').text.strip()
        elif 'Yêu cầu công việc' == detail.find('h2', class_ = 'sc-4913d170-5 kKmzVC').text.strip():
            job_requirement = detail.find('div', class_='sc-4913d170-6 hlTVkb').text.strip()

    # lấy quyền lợi
    benefits = soup.find_all('div', class_='sc-c683181c-2 fGxLZh')
    benefit = ''
    for i in benefits:
        benefit += '-' + i.text.strip()

    fields = []
    result = {
        'Job Title': job_title,
        'Company Name': company_name,
        'Hạn nộp hồ sơ': deadline,
        'Mức lương': salary,
        'Mô tả công việc': job_description,
        'Yêu cầu ứng viên': job_requirement,
        'Quyền lợi': benefit,
        'Địa điểm làm việc': location,
        'Lĩnh vực': fields,
        'Url': url
    }
    driver.quit()
    return result

# Main function to scrape job data and export it to a JSON file
def scrape_jobs(chromepath, output_file, start_page, end_page):
    try:
        service = Service(executable_path=chromepath)
        driver = webdriver.Chrome(service=service)

        df_job = []

        for page in range(start_page, end_page + 1):
            driver.get(f'https://www.vietnamworks.com/viec-lam?g=5&page={page}')
            time.sleep(5)

            # Scroll down to load more jobs
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            print(f'Scraping page: {page}')
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            job_containers = soup.find_all('div', class_="sc-cvBxsj gmxClk")

            for container in job_containers:
                url = container.find('a', target='_blank').get('href')
                info = get_info('https://www.vietnamworks.com' + url, chromepath)
                print(f'Found job: {url}')
                df_job.append(info)

        driver.quit()

        # Save scraped data to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(df_job, f, ensure_ascii=False, indent=4)
        print(f'Data has been saved to {output_file}')

    except Exception as ex:
        print(f'Error: {ex}')

# Main execution
if __name__ == "__main__":
    chromepath = r'C:\Users\MSI\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
    output_file = 'C:/Users/MSI/Desktop/crawl/data/job_listings_4_5.json'
    start_page = 4
    end_page = 5
    scrape_jobs(chromepath, output_file, start_page, end_page)