import json
import pandas as pd
from selenium import webdriver
from model import Job  # Ensure you have this model available in your local environment
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup  # Import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Define the function to scrape job listings
def scrape_jobs(chromepath, output_file):
    try:
        job_list_detail = []
        url = 'https://www.topcv.vn/tim-viec-lam-it-phan-mem-c10026?sba=1'
        service = Service(executable_path=chromepath)
        driver = webdriver.Chrome(service=service)
        driver.get(url)
        
        for next_page in range(1, 2):
            job_items = driver.find_elements(By.CLASS_NAME, 'job-item-search-result')
            quick_view_button = job_items[0].find_elements(By.XPATH, "//div[@class='body']/div[@class='body-content']/div[@class='title-block']/div[@class='box-right']/p[@class='quick-view-job-detail']")
            
            for job_detail_view in quick_view_button:
        # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", job_detail_view)
                time.sleep(1)  # Wait for the scroll to complete
        
                try:
            # Click the element using JavaScript
                    driver.execute_script("arguments[0].click();", job_detail_view)
                except Exception as e:
                    print(f"Error clicking element: {e}")
        
                time.sleep(1)
        
                header_job = driver.find_elements(By.XPATH, "//div[@class='box-view-job-detail']/div[@class='box-header']")
                body_job = driver.find_elements(By.XPATH, "//div[@class='box-view-job-detail']/div[@class='box-scroll']")
                
                if len(header_job) > 0 and len(body_job) > 0:
                    header_job = header_job[0]
                    body_job = body_job[0]
                    job = Job.Job()
                    
                    job.title = header_job.find_elements(By.XPATH, "//div[@class='box-title']/h2[@class='title']")[0].text
                    job.salary = header_job.find_elements(By.XPATH, "//div[@class='header-normal-default']/div[@class='box-info-job']/div[@class='box-info-header']/div[@class='box-item-header'][1]/div[@class='box-item-value']")[0].text
                    job.location = driver.find_elements(By.XPATH, "//div[@class='header-normal-default']/div[@class='box-info-job']/div[@class='box-info-header']/div[@class='box-item-header'][2]/div[@class='box-item-value']")[0].text
                    job.exp = header_job.find_elements(By.XPATH, "//div[@class='header-normal-default']/div[@class='box-info-job']/div[@class='box-info-header']/div[@class='box-item-header'][3]/div[@class='box-item-value']")[0].text
                    
                    # Use BeautifulSoup to clean up the HTML content
                    job.description = clean_html(body_job.find_elements(By.XPATH, "//div[@class='box-job-info']/div[@class='content-tab'][1]")[0].get_attribute("innerHTML"))
                    job.requirement = clean_html(body_job.find_elements(By.XPATH, "//div[@class='box-job-info']/div[@class='content-tab'][2]")[0].get_attribute("innerHTML"))
                    job.benefit = clean_html(body_job.find_elements(By.XPATH, "//div[@class='box-job-info']/div[@class='content-tab'][3]")[0].get_attribute("innerHTML"))
                    job.working_location = body_job.find_elements(By.XPATH, "//div[@class='box-job-info']/div[@class='box-address']/div/div")[0].text
                    
                    if len(body_job.find_elements(By.XPATH, "//div[@class='box-job-info']/div[@class='content-tab'][4]/div[@class='content-tab__list']")) > 0:
                        job.working_time = body_job.find_elements(By.XPATH, "//div[@class='box-job-info']/div[@class='content-tab'][4]/div[@class='content-tab__list']")[0].text
                    
                    job.company = body_job.find_elements(By.XPATH, "//div[@class='job-detail__company']/div[@class='job-detail__company--information']/div[@class='job-detail__company--information-item company-name']/div[@class='box-main']/h2[@class='company-name-label']/a[@class='name']")[0].text
                    job_list_detail.append(job.__dict__)  # Save the job details as a dictionary
            
            # Navigate to the next page
            driver.find_elements(By.CLASS_NAME, "pagination")[0].find_elements(By.TAG_NAME, "li")[2].click()
            time.sleep(4)
        
    except Exception as ex:
        print(f'Error: {ex}')
    
    finally:
        if job_list_detail: 
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(job_list_detail, f, ensure_ascii=False, indent=4)
            print(f"Data has been written to {output_file}")
        else:
            print("No job details scraped.")

# Helper function to clean HTML using BeautifulSoup
def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator="\n").strip()  # Convert HTML to plain text

# Main execution
if __name__ == "__main__":
    chromepath = r'C:\Users\MSI\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'  
    output_file = 'C:/Users/MSI/Desktop/crawl/data/job_listings_1-10.json'  
    scrape_jobs(chromepath, output_file)
