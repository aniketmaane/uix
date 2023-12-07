import configparser
import os
import sys
import datetime
import time
from pathlib import Path
from selenium.common import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

path = Path(__file__)
ROOT_DIR = path.parent.parent.absolute()
driver_path = os.path.join(ROOT_DIR, "Driver/chromedriver.exe")
screenshot_path = os.path.join(ROOT_DIR, "Screenshot")
config_path = os.path.join(ROOT_DIR, "config.properties")
config = configparser.RawConfigParser()
config.read(config_path)
appID = 0
# buisness_date = '31/08/2023 '
# charge_amount = 51,920.00
# total_amount = 2148080

#To get service and option objects
def get_service_and_option(var):
    # var = config.get( 'CHROME', 'activate ')
    if var == 'Chrome':
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        driver_path = os.path.join(ROOT_DIR, "Driver/chromedriver.exe")
    elif var == 'Edge':
        from selenium. webdriver.edge.service import Service
        from selenium. webdriver.edge. options import Options
        driver_path = os.path.join(ROOT_DIR, "Driver/msedgedriver.exe")
    elif var == 'Safari':
        from selenium.webdriver.safari.service import Service
        from selenium.webdriver.safari.options import Options
        #driver_path = os. path. join(ROOT_DIR, "Driver/chromedriver.exe")
    elif var == 'Firefox':
        from selenium. webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options
        #driver_path = os path join(ROOT_DIR,"Driver/chromedriver exe")

    options = Options()
    options.add_argument ('--disable-gpu')
    service = Service(executable_path=driver_path)

    return service, options


#To initiate the driver
def initiate_driver(url):
    try:
        voutcome = 'FAIL:Default--initiate_driver'
        var = config.get('BROWSER', 'value')
        service,options = get_service_and_option(var)
        # service = Service(executable_path=driver_path)
        if var =="Chrome":
            driver = webdriver.Chrome(service=service, options=options)
        elif var =="Edge":
            driver = webdriver.Edge(service=service, options=options)
        elif var =="Safari":
            driver = webdriver.Safari(service=service, options=options)
        elif var =="Firefox" :
            driver = webdriver. Firefox(service=service, options=options)

        driver.get(url)
        # driver = webdriver.Edge(service=service, options=options)
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
            'Timed out waiting for PA creation ' +
            'confirmation popup to appear.')

            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(2)
            # aTab = driver.find_element(By.XPATH, '//a')
            # alab.click()
            # print ("alert accepted")
        except TimeoutException:
            msg = "no alert"
            # print ('no alert"）
            #   time.sleep(2)
        driver.maximize_window()
    except:
        voutcome = 'FAIL:initiate_driver-->' + str(sys.exc_info)
    else:
        voutcome = driver
    finally:
        return voutcome

#To execute the test cases
def test(df_master_databuilder, page_name, field_xpath, test_data, driver, key, test='test'):
    try:
        # if field_path == "//input[@id='t×tAddressOne']";
        # print(field_xpath)
        global appID, charge_amount, total_amount
        vOutcome = 'FAIL :Default-->execute_test_cases'
        wait_time_list = [int(df_master_databuilder["WAIT_TIME"].values[0])]
        counter = 0

        bPreconditions = ""

        for i, row in df_master_databuilder.iterrows():

            if bPreconditions == "":
                bPreconditions = True

            if bPreconditions:
                if counter > 0:
                    wait_time_list.append(int(row["WAIT_TIME"]))

                counter = 1
                wait_time_pre = wait_time_list[len(wait_time_list) - 2]

                if row["PAGE_TITLE"] == page_name:
                    if row["FIELD_XPATH"] == field_xpath:
                        value = test_data
                    else:
                        if type(row["VALUE"]) == float and str(row["VALUE"]) != "nan":
                            value = int(row["VALUE"])
                        elif type(row["VALUE"]) == float and str(row["VALUE"]) == "nan":
                            value = row["VALUE"]
                        else:
                            value = row["VALUE"]

                    if row["VALIDATION"].__contains__("PageTitle") or row["VALIDATION"]._contains("AlertMessage") or \
                        row["VALIDATION"].__contains__("No"):
                        try:
                            if row["WAIT_TIME"] != float:
                                wait_time = int(row["WAIT_TIME"])
                        except:
                            wait_time = 0

                    action = row['ACTION']
                    alert_text = ""

                    if row['ACTION'] == "Enter":
                        try:
                            if row["FIELD_XPATH"] == "//input[@id='pass']":
                                value = "@Aniket2208"
                            if str(value) != "nan":
                                driver.find_element(By.XPATH, row["FIELD_XPATH"]).send_keys(value)
                                driver.find_element(By.XPATH, row["FIELD_XPATH"]).send_keys(Keys.TAB)
                        except Exception as e:
                            print(f'Error has occured for Xpath: {row["FIELD_XPATH"]} /n {e}')
                            # retriving the same scenarion in case of failure
                            result = retriveOperation(row, wait_time_pre, driver, action, field_xpath, value)
                            bPreconditions, driver = execute_after_retrive(result, driver)
                        time.sleep(wait_time)

                    elif row['ACTION'] == "Click":
                        # This will execute if radio button is going to be tested
                        # To execute the test data if test_data == "Yes"
                        if row["FIELD_XPATH"] == field_xpath and test_data == "Yes":
                            bPreconditions, driver = performAction(row, wait_time_pre, driver, action, field_xpath)

                        # This will execute if radio button is not going to be tested
                        # Ignoring the other radio button options on the same fields
                        elif row["FIELD_XPATH"] == field_xpath and test_data == "No":
                            continue
                        else:
                            # This will execute for other radio button on the web page
                            if row["VALUE"] == "Yes":
                                bPreconditions, driver = performAction(row, wait_time_pre, driver, action, field_xpath)
                            else:
                                continue

                    elif row['ACTION'] == "Check":
                        # This will execute if checkbox is going to be tested
                        if row["FIELD_XPATH"] == field_xpath and test_data == "Yes":
                            bPreconditions, driver = performAction(row, wait_time_pre, driver, action, field_xpath)
                        # This will execute if checkbox is not going to be tested
                        elif row["FIELD_XPATH"] == field_xpath and test_data == "No":
                            continue
                        # This will execute if have other checkbox on the webpage
                        else:
                            # if row["VALUE"] == "Yes" and row["DATATYPE"] != "field_type":
                            if row["VALUE"] == "Yes":
                                bPreconditions, driver = performAction(row, wait_time_pre, driver, action, row["FIELD_ХРАТН"])
                            else:
                                continue
                        time.sleep(wait_time)


                    elif row["ACTION"] == "Select":
                        # If test case field has select operation
                        if row["FIELD_XPATH"] == field_xpath:
                            bPreconditions, driver = performAction(row, wait_time_pre, driver, action, field_xpath, value)

                        elif row["FIELD_XPATH"] == field_xpath and type(test_data) == float:
                            continue
                        elif row["FIELD_XPATH"] != field_xpath:
                            bPreconditions, driver = performAction(row, wait_time_pre, driver, action, row["FIELD_XPATH"], value)
                        elif row["FIELD_XPATH"] != field_xpath and type(row["VALUE"]) == float:
                            continue
                            time.sleep(wait_time)

                    elif row['ACTION'] == "Submit":
                        if page_name.__contains__("Rapido Contact- Get in touch with us"):
                        # manually selecting dropdowns because no attribute to create a xpath for rapido website.
                            driver.find_element(By.XPATH, "//select/option[2]").click()
                            driver.find_element(By.XPATH, "(//select) [2] / option[2]").click()

                        bPreconditions, driver = performAction(row, wait_time_pre, driver, action, row["FIELD_XPATH"], page_name=page_name)
                        time.sleep(wait_time)
                        #Handling alert if any
                        try:
                            WebDriverWait(driver, 1).until(EC.alert_is_present(),
                                                           'Timed out waiting for PA creation ' +
                                                           'confirmation popup to appear.')

                            alert = driver.switch_to.alert
                            alert.accept()
                            time.sleep(2)
                            # aTab = driver.find_element(By.XPATH, '//a')
                            # alab.click()
                            # print ("alert accepted")
                        except TimeoutException:
                            msg = "no alert"
                            # print ('no alert"）

                    elif row['ACTION'] == "ClickOnElement":
                        if True:
                            bPreconditions, driver = performAction()(row, wait_time_pre, driver, action, row["FIELD_XPATH"])
                        time.sleep(wait_time)
                    elif row['ACTION'] == "SwitchToNewWindow":
                        bPreconditions, driver = performAction(row, wait_time_pre, driver, action)
                    elif row['ACTION'] == "SwitchToFrame":
                        bPreconditions, driver = performAction(row, wait_time_pre, driver, action, value=row["VALUE"])
                    elif row['ACTION'] == "EnterText":
                        bPreconditions, driver = performAction(row, wait_time_pre, driver, action, row["FIELD_XPATH"])
                    elif row['ACTION'] == "SwitchToParentFrame":
                        bPreconditions, driver = performAction(row, wait_time_pre, driver, action)
                    elif row['ACTION'] == "SwitchToParentDefaultContent":
                        bPreconditions, driver = performAction(row, wait_time_pre, driver, action)
                    elif action =="MaximizeWindow":
                        bPreconditions, driver = performAction(row, wait_time_pre, driver, action)
                    elif action == "CloseWindow":
                        try:
                            value=row["VALUE"]
                            driver.close
                        except:
                            result = retrive_operation(now, wait_time_pre, driver, action)
                            bPreconditions, driver = execute_after_retrive(result, driver)

            else:
                break

    except:
        vOutcome = 'FAIL:test-->' + str(sys.exc_info())
        print(vOutcome)
    else:
        if test == "test":
            actual_response, bPreconditions = get_actual_response(driver, row["VALIDATION"], key, alert_text, field_xpath, bPreconditions)
        else:
            actual_response, bPreconditions = ("beforeTest", True)
    finally:
        #driver.close()
        return actual_response, driver, bPreconditions


#generating actual_response for validation
def get_actual_response (driver, validation, key, alert_text, field_xapth, bPreconditions):
    actual_response = ''
    try: 
        if "][" in validation:
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                           'Timed out waiting for PA creation ' +
                                           'confirmation popup to appear.')
            alert = driver.switch_to.alert
            actual_response_alert = alert.text
            alert.accept()
            time.sleep(1)
            actual_response_pageTitle = driver.title
            actual_response = [actual_response_alert, actual_response_pageTitle]

        elif "PageTitle" in validation:
            actual_response = driver.title

        elif "AlertMessage" in validation:
            if alert_text == "":
                WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                               'Timed out waiting for PA creation ' +
                                               'confirmation popup to appear.')
                actual_response = alert_text
            else:
                actual_response = alert_text

        vOutcome = actual_response, bPreconditions

    except:
        vOutcome = "FAIL: get_actual_response-->" + + str(sys.exc_info())
        print(vOutcome)
    finally:
        return vOutcome


#Method to perform actions on web page e.g. click, entering the value inside input boxes,
# select dropdown, switching into the iframe, switching to the child browsers
def performAction(df, wait_time_pre, driver, action, field_xpath="", value="", page_name=""):
    try:
        if action == "Click" or action == "ClickOnElement":
            driver.find_element(By.XPATH, field_xpath).click()
        elif action == "Select":
            Select(driver.find_element(By.XPATH, field_xpath)).select_by_visible_text(value)
        elif action == "Submit":
            submit_button = driver.find_element(By.XPATH, field_xpath)
            ActionChains(driver).move_to_element(submit_button).click(submit_button).perform()
        elif action == "SwitchToNewWindow":
            driver = switch_to_new_window(driver)
        elif action == "SwitchToFrame":
            driver. switch_to. frame(value)
        elif action == "EnterText":
            element = driver.find_element(By.XPATH, field_xpath)
            element. click()
            time.sleep(1)
            element.clear()
            time.sleep(1)
            element.send_keys(value)
        elif action == "SwitchToParentFrame":
            driver.switch_to.parent_frame()
        elif action == "SwitchToParentDefaultContent":
            driver.switch_to.default_content()
        elif action == "MaximizeWindow":
            driver.maximize_window()
        elif action == "CloseWindow":
            driver.close()

        bPreconditions = True

    except Exception as e:
        print(e)
        if action in ["Click", "ClickOnElement", "Submit"]:
            result = retriveOperation(df, wait_time_pre, driver, action, field_xpath)
        elif action == "Select":
            result = retriveOperation(df, wait_time_pre, driver, action, field_xpath, value)
        elif action == "SwitchToFrame":
            result = retriveOperation(df, wait_time_pre, driver, action, value)
        elif action == "EnterText":
            result = retriveOperation(df, wait_time_pre, driver, action, field_xpath, value)
        elif action in ["SwitchToNewWindow", "SwitchToParentFrame", "SwitchToParentDefaultContent", "MaximizeWindow", "CloseWindow"]:
            result = retriveOperation(df, wait_time_pre, driver, action)

        bPreconditions, driver = execute_after_retrive(result, driver)

    return bPreconditions, driver

#updating Preconditions and driver after retrive operation -
def execute_after_retrive(result, driver):
    try:
        vOutcome = 'FAIL:Default-->execute_after_retrive-->' + str(sys.exc_info())
        if result[1]:
            driver = result[0]
            bPreconditions = True
        else:
            # logout (driver)
            bPreconditions = False
    except:
        print('FAIL:get_AppID-->' + str(sys.exc_info()))
    else:
        vOutcome = bPreconditions
    finally:
        return vOutcome, driver


def retriveOperation(df, wait_time, driver, action, xpath="", value=""):
    try:
        WebDriverWait (driver, wait_time).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        if action == 'Enter':
            #xpath = "//input[@name='TxtUID']"
            driver.find_element (By.XPATH, xpath).send_keys(value)
            driver. find_element (By.XPATH, xpath). send_keys(Keys.TAB)
            result = True
            print(f"retried successfully for {xpath} and action: {action}")
        elif action == 'Click':
            driver.find_element(By.XPATH, xpath).click
            result = True
            print(f"retried successfully for {xpath} and action: {action}")
        elif action == "Check":
            driver. find_element(By.XPATH, xpath).click()
            result = True
            print(f"retried successfully for {xpath} and action: {action}")
        elif action == "Select" :
            Select (driver. find_element(By.XPATH, xpath)).select_by_visible_text(value)
            result = True
            print(f"retried successfully for {xpath} and action: {action}")
        elif action =='Submit':
            submit_button = driver.find_element(By.XPATH, xpath)
            ActionChains(driver).move_to_element(submit_button).click(submit_button).perform()
            result = True
            print(f"retried successfully for {xpath} and action: {action}")
        elif action == "ClickOnElement":
            driver.find_element(By.XPATH, xpath).click()
            print(f"retried successfully for {xpath} and action: {action}")

        elif action == "SwitchToNewWindow":
            driver = switch_to_new_window(driver)
            print(f"retried successfully for action: {action}")
            result = True
        elif action == "SwitchToFrame":
            driver.switch_to.frame(value)
            print(f"retried successfully for action: {action}")
            result = True
        elif action == "EnterText":
            element = driver.find_element(By.XPATH, xpath)
            element.click()
            time.sleep(1)
            element.clear()
            time.sleep(1)
            element.send_keys(value)
            print(f"retried successfully for action: {action}")
            result = True
        elif action == "SwitchToParentFrame":
            driver.switch_to.parent_frame()
            print(f"retried successfully for action: {action}")
            result = True
        elif action == "SwitchToParentDefaultContent":
            driver.switch_to.default_content()
            print(f"retried successfully for action: {action}")
            result = True
        elif action == "MaximizeWindow":
            driver.maximize_window()
            print(f"retried successfully for action: {action}")
            result = True
        elif action == "CLoseWindow":
            driver.close()
            print(f"retried successfully for action: {action}")
            result = True

    except Exception as e:
        result = False
        takeScreenshot(df, driver)
        print(f"Unable to retrive for action: {action}")

    finally:
        return driver, result



def takeScreenshot (df, driver):
    try:
        vOutcome = 'FAIL: Default-->takeScreenshot'
        page_name = df['PAGE_TITLE']
        page_name = page_name.replace(" ", "")
        action = df['ACTION']

        if str(df['VALUE']) != 'nan':
            name = page_name + "_" + action + "_" + df['VALUE']
        else:
            name = page_name + "_" + action

        date = str(datetime.date.today())
        current_date_directory_path = os.path.join(screenshot_path, date)

        if os.path.isdir(current_date_directory_path) :
            pass
        else:
            os.mkdir(current_date_directory_path)
            driver.save_screenshot(f"{current_date_directory_path}/{name}•jpeg")
    except:
        vOutcome = 'FAIL:takeScreenshot-->' + str(sys.exc_info())
        # Logout(driver) '
    else:
        voutcome = f"Screenshot {name}.jpeg taken"
    finally:
        print(voutcome)


# switch to new window after opening the web page
def switch_to_new_window(driver):
    try:
        voutcome = 'FAIL :Default-->switch_to_new_window'
        handles = driver.window_handles
        if len(handles)>1:
            driver.switch_to.window(handles[len(handles)-1])
            #print（driver.title）
        else:
            driver=driver
    except:
        voutcome = 'FAIL: switch_to_new_window-=>' + str(sys.exc_info())
    else:
        voutcome = driver
    finally:
        return voutcome


def update_df2(df2, index, module, page_name, test_case_name, xpath,keyword, test_data, expected_response, actual_response):

    try:
        vOutcome = 'FAIL:Default-->update_df2'
        global appID
        df2.at[index, 'Module'] = module
        df2.at[index, 'Page Title'] = page_name
        df2.at[index, 'Test_Case_Id'] = test_case_name
        df2.at[index, 'Field_Xpath'] = xpath
        df2.at[index, 'Keyword'] = keyword
        df2.at[index, 'Test Data'] = test_data
        df2.at[index, 'Expected response'] = expected_response
        df2.at[index, 'Actual response'] = actual_response

    except:
        vOutcome = 'FAIL:update_df2-->' + str(sys.exc_info())
    else:
        vOutcome = df2
    finally:
        return vOutcome


def add_result_df2(df2, index, actual_response, validation_key):
    try:
        vOutcome = 'FAIL:Default-->add_result_df2'
        expected_result_list_for_alert = ["Only characters are allowed."]
        expected_result = df2["Expected response"].values[-1]
        actual_result = actual_response
        if type(validation_key)==str and validation_key == "PageTitle":
            if expected_result in actual_response:
                result = 'Pass'
            elif actual_response in expected_result_list_for_alert:
                result = 'Pass'
            else:
                result = 'Fail'
        elif type(validation_key)==str and validation_key == "AlertMessage" :
            if actual_result in expected_result:
                result = 'Pass'
            else:
                result = 'Fail'
        elif type(validation_key)==list:
            expected_alert = expected_result.split(",")[0]
            expected_pageTitle = expected_result.split(",")[1]
            actual_alert = validation_key[0]
            actual_pageTitle = validation_key[1]
            if expected_alert == actual_alert and expected_pageTitle == actual_pageTitle:
                result = 'Pass'
            else:
                result = 'Fail'

        df2.at[index, 'Result'] = result

    except:
        vOutcome = 'FAIL:add_result_df2-->' + str(sys.exc_info())
    else:
        vOutcome = df2
    finally:
        return vOutcome





















# def execute(df,page_title,field_xpath,test_data,driver):
#
#     if df["PAGE_TITLE"]==page_title:
#
#         if df["VALIDATION"].__contains__("NextPage"):
#
#             if df["ACTION"] == 'Enter':
#
#                 if df["FIELD_XPATH"] == field_xpath:
#
#                     if type(test_data)==float and str(test_data)=='nan':
#                         pass
#                     else:
#                         value=test_data
#                         driver.find_element(By.XPATH, df['FIELD_XPATH']).send_keys(value)
#                         time.sleep(2)
#                         print(test_data, end=" ")
#
#                 else:
#                     value = df['VALUE']
#                     driver.find_element(By.XPATH, df['FIELD_XPATH']).send_keys(value)
#                     print(test_data, end=" ")
#
#             elif df["ACTION"] == 'Click' and df['VALUE'] == 'Yes':
#                 driver.find_element(By.XPATH, df['FIELD_XPATH']).click()
#
#             elif df["ACTION"] == 'Check' and df['VALUE'] == 'Yes':
#                 driver.find_element(By.XPATH, df['FIELD_XPATH']).click()
#
#             elif df["ACTION"] == 'Select':
#                 Select(driver.find_element(By.XPATH, df['FIELD_XPATH']).select_by_visible_text(df['VALUE']))
#
#             elif df["ACTION"] == 'Submit':
#                 submit_button = driver.find_element(By.XPATH, df['FIELD_XPATH'])
#                 ActionChains(driver).move_to_element(submit_button).click(submit_button).perform()
#
#     return driver






