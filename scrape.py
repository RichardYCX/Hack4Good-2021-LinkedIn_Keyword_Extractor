from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from helper import login
import config
import json
import logging

profile = "https://www.linkedin.com/in/richardyang98/"
file_name = 'RY'
logging.basicConfig(filename='scrape.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
logging.info("driver setup done")

login(driver, config.email, config.password)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "profile-rail-card__actor-link.t-16.t-black.t-bold")))
logging.info("successfully logged in")

driver.get(profile)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "pv-top-card--list.inline-flex.align-items-center")))
logging.info("successfully fetched profile")

LinkedIn_Dict = {}

have_recent_activities = False
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "pv-recent-activity-section-v2__summary.t-14.t-black--light.t-normal")))
if "last 90 days are displayed here" not in \
        driver.find_element_by_class_name("pv-recent-activity-section-v2__summary.t-14.t-black--light.t-normal").text:
    have_recent_activities = True
else:
    logging.warning("no recent activities")

driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
LinkedIn_Dict['Interests'] = {}
driver.get(profile+'/detail/interests/')
WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(@id, 'pv-interests-modal__following')]")))
interest_categories = driver.find_elements_by_xpath("//*[contains(@id, 'pv-interests-modal__following')]")

for interest_category in interest_categories:
    LinkedIn_Dict['Interests'][interest_category.text] = interest_category.get_attribute('href')

logging.info("successfully fetched interest categories")
logging.debug('found', len(LinkedIn_Dict['Interests']), 'interest categories')

i = 1
for key, values in LinkedIn_Dict['Interests'].items():
    driver.get(values)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "pv-entity__summary-title-text")))
    WebDriverWait(driver, 1)
    if key == 'Influencers':
        interest_names = driver.find_elements_by_class_name("pv-entity__summary-title-text")
        interest_descriptions = driver.find_elements_by_class_name("pv-interest-entity-link.ember-view")
        LinkedIn_Dict['Interests'][key] = [{'Name': interest_name.text, 'Description': interest_description.get_attribute("href")}
                                           for interest_name, interest_description in zip(interest_names, interest_descriptions)]
    elif key == 'Companies':
        interest_names = driver.find_elements_by_class_name("pv-entity__summary-title-text")
        company_links = driver.find_elements_by_class_name("pv-interest-entity-link.ember-view")
        LinkedIn_Dict['Interests'][key] = [{'Name': interest_name.text, 'Industry': company_link.get_attribute("href")}
                                           for interest_name, company_link in zip(interest_names, company_links)]
    # else:
    #     interest_names = driver.find_elements_by_class_name("pv-entity__summary-title-text")
    #     LinkedIn_Dict['Interests'][key] = [{'Name': interest_names.text} for interest_names in interest_names]
    logging.debug('fetched', i, 'interest categories')
    i += 1

if 'Influencers' in LinkedIn_Dict['Interests']:
    for index in range(len(LinkedIn_Dict['Interests']['Influencers'])):
        description = LinkedIn_Dict['Interests']['Influencers'][index]['Description']
        driver.get(description)
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pv-about__summary-text.mt4.t-14.ember-view")))
            description = driver.find_element_by_class_name("pv-about__summary-text.mt4.t-14.ember-view").text
        except:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mt1.t-18.t-black.t-normal.break-words")))
            description = driver.find_element_by_class_name("mt1.t-18.t-black.t-normal.break-words").text

        LinkedIn_Dict['Interests']["Influencers"][index]['Description'] = description

if 'Companies' in LinkedIn_Dict['Interests']:
    for index in range(len(LinkedIn_Dict['Interests']['Companies'])):
        company_link = LinkedIn_Dict['Interests']['Companies'][index]['Industry']
        driver.get(company_link)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "org-top-card-summary-info-list__info-item")))
        company_sector = driver.find_element_by_class_name("org-top-card-summary-info-list__info-item").text
        LinkedIn_Dict['Interests']["Companies"][index]['Industry'] = company_sector
logging.info("successfully fetched interests")

if have_recent_activities:
    driver.get(profile+'/detail/recent-activity/')
    WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "occludable-update.ember-view")))
    RAs = driver.find_elements_by_class_name("occludable-update.ember-view")

    LinkedIn_Dict['Recent Activities'] = [{'Article Author': None,
                                           'Author Description': None,
                                           'Activity': None} for i in range(min(5, len(RAs)))]
    for index in range(5):
        ra = RAs[index]
        try:
            LinkedIn_Dict['Recent Activities'][index]['Article Author'] = \
                ra.find_element_by_class_name("feed-shared-actor__name.t-14.t-bold.hoverable-link-text.t-black").text
        except:
            pass

        try:
            description = ra.find_element_by_class_name("feed-shared-actor__description.t-12.t-normal.t-black--light").text or \
                ra.find_element_by_class_name("feed-shared-text-view.white-space-pre-wrap.break-words.ember-view").text
            LinkedIn_Dict['Recent Activities'][index]['Author Description'] = \
                description if 'follower' not in description else None
        except:
            pass

        try:
            LinkedIn_Dict['Recent Activities'][index]['Activity'] = ra.find_element_by_class_name("feed-shared-text-view.white-space-pre-wrap.break-words.ember-view").text
        except:
            pass

    logging.info('successfully fetched recent activities')

driver.quit()

logging.info("finished scrapping")

with open(file_name+'.json', 'w') as json_file:
    json.dump(LinkedIn_Dict, json_file)

logging.info("json file created, exiting...")