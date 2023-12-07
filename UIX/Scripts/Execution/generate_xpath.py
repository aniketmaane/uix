"""
*Utility script to generate Xpaths for the given url
*Take the input url from the user
*Parse the html content using BeautifulSoup
*Find all the input,button,select and iframe
*Guess the Xpaths
*Generate Variable names for the Xpaths
*To run the script in Gitbash use command 'python -u utils/xpath_util.py'
"""

import os.path
import re
import sys
import time
import warnings
from pathlib import Path
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import requests
import UserLibraries.utilities as utl

from UserLibraries.masterTemplateWriter import create_master_template_xpath


warnings.filterwarnings('ignore')


class Xpath_Util:
    """"Class to generate the Xpaths"""

    def __init__(self):
        "Initialize the required variables"
        self.elements=None
        self.guessable_elements=['input', 'select', 'textarea', 'button']
        self.known_attribute_list=['id', 'name', 'placeholder', 'value', 'title', 'type', 'class']
        self.variable_names=[]
        self.button_text_lists=[]
        self.language_counter=1

    def generate_xpath(self,soup,url,title,driver):
        """generate the xpath and assign the variable names"""
        result_flag = False
        df = pd.DataFrame()
        xpath_list=[]
        url_list=[]
        title_list=[]
        action_list=[]

        for guessable_element in self.guessable_elements:
            if guessable_element == "iframe":
                self.elements = soup.find_all(guessable_element)
                for element in self.elements:
                    src = element['src']
                    try:
                        with requests.Session as s:
                            response = s.get(src,verify=True)
                        #response=httpx.get(src)
                        #response=urlopen(src).read()
                        if response.status_code==200:
                            soup_src = BeautifulSoup(response.text, 'html.parser')
                            soup_src_inputbox = soup_src.find_all('input')
                            soup_src_button = soup_src.find_all('button')
                            soup_src_all = [soup_src_inputbox, soup_src_button]

                            driver1=webdriver.Chrome(service=service, options=options)
                            driver1.get(src)
                            title=driver1.title

                            for soup_src in soup_src_all:
                                result_flag = self.extract_page(soup_src,driver,title,guessable_element,xpath_list,url_list,title_list,action_list,result_flag,src,driver1)
                        else:
                            continue

                    except Exception as e:
                        print(e)

            else:
                self.elements = soup.find_all(guessable_element)
                if len(self.elements)>0:
                    result_flag = self.extract_page(self.elements, driver, title, guessable_element, xpath_list, url_list, title_list, action_list, result_flag, src=url, driver1='')
                else:
                    continue
        if len(xpath_list)>0:
            #self.create_master_template_xpath(xpath_list, url_list, title_list, action_list)
            xpath_list = xpath_list
        else:
            print("No xpath to create master databuilder")
        return result_flag

    def extract_page(self,elements,driver,title,guessable_element,xpath_list,url_list,title_list,action_list,result_flag,src,driver1):
        xpath_obj = Xpath_Util()
        for element in elements:
            try:
                type = element['type']
            except:
                type='none'

            if (not element.has_attr("type")) or (element.has_attr("type") and element['type'] != 'hidden'):
                for attr in self.known_attribute_list:
                    if element.has_attr(attr):
                        if guessable_element == 'iframe':
                            guessable_element_iframe = elements[0].name
                            locator = self.guess_xpath(guessable_element_iframe, attr, element)
                        else:
                            locator = self.guess_xpath(guessable_element, attr, element)

                        try:
                            len_xpath = 0
                            len_iframe_xpath =0
                            if guessable_element != 'iframe':
                                len_xpath = len(driver.find_elements(by=By.XPATH,value=locator))
                            elif guessable_element == 'iframe':
                                len_iframe_xpath = len(driver1.find_elements(by=By.XPATH, value=locator))

                            if len_xpath==1 or len_iframe_xpath==1:
                                result_flag=True
                                if guessable_element=="iframe":
                                    variable_name = 'iframe_' + self.get_variable_names(element)
                                else:
                                    variable_name = self.get_variable_names(element)
                                if variable_name != "" and variable_name not in self.variable_names:
                                    self.variable_names.append(variable_name)
                                    variable_name=variable_name.split("_")[-1]
                                    xpath = "%s_%s = %s" %(guessable_element,variable_name.encode('utf-8').decode('latin-1'),locator.encode('utf-8').decode('latin-1'))
                                    xpath = xpath.split(" = ")[-1]
                                    xpath_list.append(xpath)
                                    url_list.append(src)
                                    title_list.append(title)
                                    action = self.generate_action(type,element)
                                    action_list.append(action)
                                    print("%s_%s = %s" %(guessable_element,variable_name.encode('utf-8').decode('latin-1'),locator.encode('utf-8').decode('latin-1')))
                                    break
                                else:
                                    variable_name = locator.encode('utf-8').decode('latin-1')
                                    #print(locator.encode('utf-8').decode('latin-1') + "---->Couldn't generate appropriate variable name for this path")
                        except Exception as e:
                            #print(e)
                            continue
                        finally:
                            continue

            elif guessable_element == "button" and element.getText():
                button_text = element.getText()
                if element.getText() == button_text.strip():
                    locator = xpath_obj.guess_xpath_button(guessable_element, "text()", element.getText())
                else:
                    locator = xpath_obj.guess_xpath_using_contains(guessable_element,"text()",button_text.strip())
                if len(driver.find_elements(by=By.XPATH,value=locator))==1:
                    result_flag=True
                    #check for utf-8 characters in the button_text
                    matches = re.search(r"[^\x00-\x7F]",button_text)
                    if button_text.lower() not in self.button_text_lists:
                        self.button_text_lists.append(button_text.lower())
                        if not matches:
                            #Striping and replacing characters before printing the variable name
                            print("%s_%s = %s" %(guessable_element,button_text.strip().strip("!?.").encode('utf-8').decode('latin-1').lower().replace(" + ","_").replace(" & ","_").replace(" ","_"), locator.encode('utf-8').decode('latin-1')))
                        else:
                            #printing the variable name with utf-8 characters along with langauge counter
                            print("%s_%s = %s" %(guessable_element, "foreigh_language", self.language_counter,locator.encode('utf-8').decode('latin-1')) + "---> Foreign language found, please change the variable name appropriately")
                            self.language_counter += 1
                    else:
                        #If the variable name is already taken
                        print(locator.encode('utf-8').decode('latin-1') + "---> Couldn't generate appropriate variable name for this xpath")
                    break
            elif not guessable_element in self.guessable_elements:
                print("We are not supporting this guessable element")
        return result_flag, xpath_list, url_list, title_list, action_list

    def get_variable_names(self,element):
        "Generate variable names for the xpath"
        #Conditions to check the length of the 'id' attribute and ignore if there are numerics in the 'id' attribute.
        #Also ignoring 'id' values having 'input' and 'button' strings
        if element.has_attr('id') and len(element['id'])>2 and bool(re.search(r'\d',element['id']))==False and ("input" not in element['id'].lower() and "button" not in element['id'].lower()):
            self.variable_name = element['id'].strip("_")

        #Condition to check if the 'value' attribute exists and not having date and time values in it.
        elif element.has_attr('id') and element['value'] != '' and bool(re.search(r'(\d{1,}([/-]|\s|[.])?)+(\D+)?([/-]|\s|[.])?[[\d]{1,}',element['value'])) == False and bool(re.search(r'\d{1,2}[:]\d{1,2}\s+((am|AM|pm|PM)?)',element['value']))==False:
            #condition to check if the 'type' atrribute exists getting the text() value if the 'type' attribute
            #value is in 'radio', 'submit', 'checkbox', 'search'. If the text() is not '', getting the getText() value
            #else getting the 'value' attribute for the rest of the type attributes printing the 'type' +'value'
            #attribute values. Doing a check to see of 'value' and 'type' attributes values are matching.
            if (element.has_attr('type')) and (element['type'] in ('radio', 'submit', 'checkbox','search')):
                if element.getText() != '':
                    self.variable_name = element['type'] + "_" + element.getText().strip().strip("_.")
                else:
                    self.variable_name = element['type'] + "_" + element['value'].strip("_.")
            else:
                if element['type'].lower() == element['value'].lower():
                    self.variable_name = element['value'].strip("_.")
                else:
                    self.variable_name = element['type'] + "_" + element['value'].strip("_.")
        #Condition to check if the "name" attribute exists and if the length of "name" attribute is more than 2
        #Printing the variable name
        elif element.has_attr('name') and len(element['name'])>2:
            self.variable_name = element['name'].strip("_")
        #Condition to check if the "placeholder" attribute exists and is not having any numerics in it.
        elif element.has_attr('placeholder') and bool(re.search(r'\d',element['placeholder'])) == False:
            self.variable_name = element['placeholder']
        # Condition to check if the "type" attribute exists and not in 'text', 'radio', 'button', 'checkbox','search'
        # Printing the variable name
        elif (element.has_attr('type')) and (element['type'] not in ('text', 'radio', 'button', 'checkbox','search')):
            self.variable_name = element['type']
        # Condition to check if the "type" attribute exists
        elif element.has_attr('title'):
            self.variable_name = element['title']
        elif element.has_attr('class'):
            self.variable_name = element['class']
        # Condition to check if the "role" attribute exists
        elif element.has_attr('role') and element['role'] != 'button':
            self.variable_name = element['role']
        else:
            self.variable_name = ''

        return self.variable_name.lower().replace("+/-","").replace("| ","").replace(" / ","_").\
            replace("/","_").replace(" - ","_").replace(" ","_").replace("&","").replace("-","_").\
            replace("[","_").replace("]","").replace("__","_").replace(".com","").strip("_")

    def guess_xpath(self, tag, attr, element):
        "Guess the xpath based on the tag, attr, element[attr]"
        if type(element[attr]) is list:
            element[attr] = [i.encode('utf-8').decode('latin-1') for i in element[attr]]
            element[attr] = ' '.join(element[attr])
        self.xpath = "//%s[@%s='%s']" %(tag, attr, element[attr])
        return self.xpath

    def guess_xpath_button(self, tag, attr, element):
        "Guess the xpath for button tag"
        self.button_xpath = "//%s[%s='%s']" % (tag, attr, element)
        return self.button_xpath

    def guess_xpath_using_contains(self, tag, attr, element):
        "Guess the xpath using contains function"
        self.button_contains_xpath = "//%s[contains(%s='%s')]" % (tag, attr, element)
        return self.button_contains_xpath

    def generate_action(self, type,element):
        if type=="text" or type=="email" or type=="password" or type=="search" or type=="tel":
            action = "Enter"
        elif type=="radio":
            action = "Click"
        elif type=="select":
            action = "Select"
        elif type=="checkbox":
            action = "Check"
        #elif type=="submit" or (element.name=='button' and element.text=='Submit'):
        elif type == "submit" or element.name == 'button':
            action = "Submit"
        return action

    def create_master_template_xpath(self,xpath_list,url_list,title_list,action_list):
        try:
            vOutcome = "FAIL:Default-->create_master_template"
            path = Path(__file__)
            ROOT_DIR = path.parent.parent.parent.absolute()
            manual_guide_path = str(ROOT_DIR) + "//Input//Manual_guide//"

            id_list=[]
            for i in range(1,len(xpath_list)+1):
                id_list.append(i)

            master_dict = {'APP': [], 'PAGE_TITLE': [], 'FIELD_XPATH': [], 'DATATYPE': [],
                       'MIN': [], 'MAX': [], 'URL': [], 'VALUE': [], 'ACTION': [],
                       'VALIDATION': [], 'PRECONDITIONS': [], 'WAIT_TIME': []}

            df_master_template = pd.DataFrame(master_dict)

            df_id = pd.Series(id_list)
            df_xpath = pd.Series(xpath_list)
            df_url = pd.Series(url_list)
            df_title = pd.Series(title_list)
            df_action = pd.Series(action_list)
            df_master_template['APP'] = df_id.values
            df_master_template['FIELD_XPATH'] = df_xpath.values
            df_master_template['URL'] = df_url.values
            df_master_template['PAGE_TITLE'] = df_title.values
            df_master_template['ACTION'] = df_action.values
            master_databuilder = os.path.join(manual_guide_path, "master_databuilder.xlsx")

            df_master_template.to_excel(master_databuilder, sheet_name="MasterData", index=False)

            # with pd.ExcelWriter(master_databuilder, engine='openpyxl', mode='a') as writer:
            #     df_master_template.to_excel(writer, sheet_name='MasterData', startrow=writer.sheets['MasterData'].max_row, index=False)

            #print("master_databuilder created successfully")

        except Exception as e:
            print(e)
            vOutcome = "FAIL:create_master_template-->"+str(sys.exc_info())


def extraction(url):
    #print("Start of %s" % __file__)

    # Initialize the xpath object
    xpath_obj = Xpath_Util()

    driver = utl.initiate_driver(url)
    title = driver.title
    page = driver.execute_script("return document.body.innerHTML").encode('utf-8').decode('latin-1')

    soup = BeautifulSoup(page, 'html.parser')

    # Extracting the xPaths on url1 page
    result_flag = xpath_obj.generate_xpath(soup, url, title, driver)
    if not result_flag[0]:
        print("No Paths generated for the URL:%s" % url)
    else:
        create_master_template_xpath(result_flag[1], result_flag[2], result_flag[3], result_flag[4])


#     -----Start of Script-----
if __name__ == "__main__":
    print("Start of %s" %__file__)

    # Initialize the xpath object
    xpath_obj = Xpath_Util()

    #no_of_pages = int(input("Enter the number of pages to be extracted: "))

    # Get the URL and Parse
    url = input("Enter URL: ")

    # Create a Crome Session
    path = Path(__file__)
    ROOT_DIR = path.parent.parent.parent.absolute()
    manual_guide_path = str(ROOT_DIR) + "//Input//Manual_guide//"
    driver_path = str(ROOT_DIR) + "/Driver/chromedriver.exe"
    service = Service(executable_path=driver_path)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=service, options=options)
    time.sleep(3)
    driver.get(url)
    driver.maximize_window()

    time.sleep(2)
    # Parsing the HTML page with BeautifulSoup

    # result = requests.get(url)
    # content = result.text
    page = driver.execute_script("return document.body.innerHTML").encode('utf-8').decode('latin-1')

    soup = BeautifulSoup(page, 'html.parser')

    if xpath_obj.generate_xpath(soup, url, title) is False:
        print("No xpath generated for the URL:%s" % url)

    driver.quit()

    # if no_of_pages==1:
    #     # Execute generate_Xpath
    #     if xpath_obj.generate_xpath(soup,url,title) is False:
    #         print("No xpath generated for the URL:%s" %url)
    #
    #     driver.quit()

    # elif no_of_pages>1:
    #
    #     # if xpath_obj.generate_xpath(soup,url,title) is False:
    #     #     print("No xpath generated for the URL:%s" %url)
    #
    #     df = pd.read_excel(manual_guide_path)
    #
    #     for i,row in df.iterrows():
    #
    #         page_title = row["PAGE_TITLE"]
    #         field_xpath = row["FIELD_XPATH"]
    #         test_data = row["VALUE"]
    #
    #         driver = execute(row,page_title,field_xpath,test_data,driver)
    #
    #     time.sleep(2)
    #     title1=driver.title
    #     url1=driver.cuuernt_url
    #     page1 = driver.execute_script("return document.body.innerHTML").encode('utf-8').decode('latin-1')
    #     soup1 = BeautifulSoup(page, 'html.parser')
    #
    #     if xpath_obj.generate_xpath(soup1,url1,title1) is False:
    #         print("No xpath generated for the URL:%s" %url)
    #
    #     driver.quit()
