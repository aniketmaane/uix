import sys

import pandas as pd
from pathlib import Path
import requests
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Scripts.Execution.generate_xpath import Xpath_Util, extraction

from UserLibraries.masterTemplateWriter import create_master_template_xpath
from selenium.webdriver.chrome.service import Service
import UserLibraries.utilities as utl
import time

bextract_next_page = True
def extract_first_page(df):
    bFirstPage = False
    try:
        url = df["URL"].unique()
        if url.size==0:
            bFirstPage = True
        elif url == "URL":
            bFirstPage = True
    except:
        bFirstPage = True

    if bFirstPage:
        #if len(url) == 1 and str(url[0]) == "nan":
        # Get the URL and parse
        url = input("Enter URL: ")
        extraction(url)
        global bextract_next_page
        bextract_next_page = False
    else:
        bextract_next_page = True
    return bextract_next_page

def extract_next_page(df):
    xpath_obj = Xpath_Util()

    page_list = df[ 'PAGE_TITLE'] .unique()
    driver = ""
    driver, url, Preconditions = openingTheBrowserAndExecutingPreconditions(driver, page_list, df)
    #Preconditions toggle will be False aften getting enror in executing the pre-conditions
    if Preconditions:
        title1 = driver.title
        url1 = driver.current_url
        # Parsing thehtml page
        page1 = driver.execute_script ("return document. body. innerHTML").encode('utf-8').decode('latin-1') #returns the inner HTML as a string
        soup1 = BeautifulSoup (page1, 'html.parser')
        print(f"UI extraction started for PAGELTITLE: {title1} and URL: {url1} ")
        # Extracting the xPaths on url1 page
        result_flag = xpath_obj.generate_xpath(soup1, url, title1, driver)
        if result_flag[0] is False:
            print("No Paths generated for the URL:%s" % url)
        else:
            create_master_template_xpath(result_flag[1], result_flag[2], result_flag[3], result_flag[4])
            #Logout(driver)
    else:
        print("multiple XPath generation stopped!")


def openingTheBrowserAndExecutingPreconditions (driver,page_list,df):
    try:
        #To enter the positive data of current_page
        vOutcome='FAIL:Default-->openingTheBrowserAndExecutingPreconditions'
        bPreconditions = True

        for current_page in page_list:
            if bPreconditions:

                dfrow = df[(df["PAGE_TITLE"] == current_page)]
                url= df["URL"].unique()[0]
                page_title=current_page

                if driver == "":
                    driver = utl.initiate_driver(url)
                    driver.get(url)

                    try:
                        WebDriverWait(driver, 1).until(EC.alert_is_present(),
                                                       'Timed out waiting for PA creation' +
                                                       'confirmation popup to appear.')

                        alert = driver.switch_to.alert
                        alert.accept()
                        print("alert accepted")
                    except TimeoutException:
                        print("no alert")

                    #clicking on "Click here to.login"
                    # aTab = driver.find_element(By.XPATH, '//a')
                    # aTab.click()

                field_xpath_list = list(dfrow["FIELD_XPATH"])
                test_data_List = list(dfrow["VALUE"])
                actual_response, driver, bPreconditions = utl.test(dfrow, current_page, field_xpath_list,test_data_List, driver, key= "", test = "beforeTest")

    except:
        vOutcome = 'FAIL:openingTheBrowserAndExecutingPreconditions-->' + str(sys.exc_info())
        print(vOutcome)
    else:
        Voutcome = driver, url, bPreconditions
    finally:
        return Voutcome

if __name__ == "__main__":
    path = Path(__file__)
    ROOT_DIR = path.parent.parent.parent.absolute()
    driver_path = str(ROOT_DIR) + "\\Driver\\chromedriver…exe"
    manual_guide = str(ROOT_DIR) + "\\Input\\Manual_Guide\\master_databuilder.xlsx"
    df = pd.read_excel(manual_guide)
    bExtract_Next_Page = extract_first_page(df)
    if bExtract_Next_Page:
        extract_next_page(df)



