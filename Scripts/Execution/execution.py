import os
from pathlib import Path
import pandas as pd
import UserLibraries.utilities as utl
from datetime import date, datetime


actual_response = ""

def execution(counter, api_def_guide_path, manual_excel_guide, report_path):
    bPreconditions = ""
    try:
        #df2 = utl.initiate_df2()
        df = pd.read_excel(file)
        df_report = pd.DataFrame()
        url = df["URL"].unique()[0]

        for id, row_ui_exe_guide in df.iterrows():
            if bPreconditions == "":
                bPreconditions = True

                if bPreconditions:
                    #url = row_vi_exe_guide[ "URL")
                   if row_ui_exe_guide["Toggle"]:

                        ui_def_guide = (api_def_guide_path + "//" + row_ui_exe_guide["PAGE_TITLE"] + "_Guide.xlsx").replace(" ", "")

                        if os.path.isfile((api_def_guide_path + "//" + row_ui_exe_guide["PAGE_TITLE"] + "_Guide.xlsx").replace(" ", "")):
                            df_ui_guide_path = pd.read_excel(ui_def_guide, dtype=str)
                            page_name = row_ui_exe_guide["PAGE_TITLE"]

                            # preconditions = row_ui_exe_guide["PRECONDITIONS"] #comment this to execute on same driver
                            if os.path.isfile(manual_excel_guide):
                                df_master_databuilder = pd.read_excel(manual_excel_guide, dtype=str)
                                keyword_xpath = []
                                driver = ''

                                # taking validation page into dataframe
                                dfrow = df_master_databuilder[(df_master_databuilder["PAGE_TITLE"] == page_name)]
                                module = dfrow["APP"].unique()[0]
                                xpath_list = dfrow["FIELD_XPATH"].unique()

                                if bPreconditions:
                                    # Taking test data one by one
                                    bexecuted_preconditions = True

                                    for index, row_ui_def_guide in df_ui_guide_path.iterrows():

                                        preconditions = row_ui_exe_guide["PRECONDITIONS"]
                                        # to execute on same driver instance reading preconditions
                                        xpath = row_ui_def_guide["xpath"]

                                        field_xpath = row_ui_def_guide["xpath"]
                                        key = row_ui_def_guide["Keyword"]

                                        # for EMPTY and NOT_OF_TYPE test data -> taking the required data into dataframe
                                        if "EMPTY1" in key or "NOT_OF_TYPE1" in key:
                                            df_reset = dfrow.reset_index(drop=True)
                                            index = df_reset[df_reset["FIELD_ХРАТН"] == xpath].index.values[0]
                                            dfrow_empty = df_reset.iloc[:index + 1]

                                            if "EMPTY" in key:
                                                df_drop = df_reset.iloc[index + 1:]
                                                df_submit = df_drop[df_drop["ACTION"] == "Submit"].reset_index(drop=True)
                                                dfrow_empty = pd.concat([dfrow_empty, df_submit.iloc[:1]], ignore_index=True)

                                        if bexecuted_preconditions:
                                            if driver == "":
                                                driver = utl. initiate_driver(url)

                                                if "EMPTY1" in key or "NOT_OF_TYPE1" in key:
                                                    df_test_frame = dfrow_empty
                                                else:
                                                    df_test_frame = df_master_databuilder
                                                    field_xpath_list = list(df_test_frame["FIELD_XPATH"])
                                                    test_data = list(df_test_frame["VALUE"])
                                                    test = "test"

                                            if type(preconditions) != float:
                                                precondition = preconditions.split(":")

                                                for page_name in precondition:

                                                    df_test_frame = df_master_databuilder[(df_master_databuilder["PAGE_TITLE"] == page_name)]
                                                    url = df[(df ["PAGE_TITLE"] == page_name)]["URL"].unique ()[0]
                                                    #dfrow = df[(df["PAGE_TITLE"] == current_page)]
                                                    field_xpath_list = list(df_test_frame["FIELD_XPATH"])
                                                    # field_type_list = list(df_pre[ "FIELD_TYPE"])
                                                    test_data = list(df_test_frame["VALUE"])

                                                    actual_response, driver, bPreconditions = utl.test(df_test_frame, page_name, field_xpath_list,
                                                                                            test_data, driver, key="", test='beforeTest')

                                                    #driver, Preconditions = utl.initiate_preconditions (preconditions, df_master_databuilder, driver)
                                                    # code to stop the execution if any precondition or test case gets fail - bPreconditions = False

                                            if bPreconditions:
                                                # updating preconditions to empty string once pre-conditions are executed
                                                #bexecuted_preconditions = False
                                                test_case_name = page_name.replace(" ", "") + "_" + xpath + "_" + str(counter)

                                                if xpath in xpath_list:
                                                    test_data = row_ui_def_guide["Value"]
                                                    keyword_xpath.append(xpath + str(test_data))

                                                    if driver == "":
                                                        driver = utl.initiate_driver(url)

                                                    actual_response, driver, bPreconditions = utl.test(df_test_frame, page_name, field_xpath,
                                                                                                       test_data, driver, key="", test=test)

                                                    if bPreconditions:
                                                        # Generating after test conditions
                                                        driver = afterTest(driver, page_name)
                                                        # Handle error if actual responce contains "FAIL"
                                                        bToggle = True
                                                        if actual_response.__contains__("FAIL"):
                                                            bToggle = False
                                                            print(f"Test Case: {test_case_name} Failed" )
                                                            break
                                                        else:
                                                            keyword = row_ui_def_guide["Keyword"]
                                                            expected_response = row_ui_def_guide["Expected response"]
                                                            df_result = pd.DataFrame()
                                                            df2 = utl.update_df2(df_result, index, module, page_name, test_case_name, xpath,
                                                                                 keyword, test_data, expected_response, actual_response)
                                                            if "][" in dfrow["VALIDATION"].unique()[0]:
                                                                validation_key = actual_response
                                                            elif "AlertMessage" in dfrow["VALIDATION"].unique()[0]:
                                                                validation_key = "AlertMessage"
                                                            elif "PageTitle" in dfrow["VALIDATION"].unique()[0]:
                                                                validation_key = "PageTitle"

                                                            df2 = utl.add_result_df2(df2, index, actual_response, validation_key)

                                                    else:
                                                        break

                                                else:
                                                    print(f"{xpath} from Ui_Def_Guide is not matching with " f"any Path in master_databuilder")
                                                    continue

                                                if bToggle:
                                                    df_report = pd.concat([df_report, df2], ignore_index=True)
                                                    df2 = pd.DataFrame()
                                                    print(counter)
                                                    counter = counter + 1
                                                    # re-assigning driver before running next test case
                                                    # driver="

                                            else:
                                                break

                                        # logging out and quiting the browser after test case execution
                                        # if bPreconditions：
                                        # utl.logout(driver)
                                        # driver.quit()

                                    else:
                                        break

    except Exception as e:
        print(e)

    if bPreconditions:
        #utl.logout(driver)
        df_report.to_excel(report_path, index=False)
    else:
        print("Execution stopped!")


def afterTest (driver, page_name):
    try:
        vOutcome = 'FAIL:Default-->afterTest'
        # Clearing the form on personal page to execute next test case
        if page_name in ['Rapido Contact- Get in touch with us']:
            url='https://www.rapido.bike/Contact'
            driver.get(url)
        vOutcome = driver

    except:
        vOutcome = "FAIL:afterTest-->' + str(sys.exc_info())"
        #utl.logout(driver)

    finally:
        return vOutcome


if __name__ == "__main__":
    counter = 1
    path = Path(__file__)
    ROOT_DIR = path.parent.parent.parent.absolute()
    file = str(ROOT_DIR) + "//Output//ui_execution_guide.xlsx"
    api_def_guide_path = os.path.join(ROOT_DIR, "Output//Ui_Def_Guide")
    manual_guide_path = os.path.join(ROOT_DIR, "Input/Manual_Guide")
    manual_excel_guide = os.path.join(manual_guide_path, "master_databuilder.xlsx")
    date_dmy = str(date.today)
    date_dmyhms = str(datetime.now()).split(" ")[0].replace(":", "-").replace(" ", "-")
    report_path = os.path.join(ROOT_DIR, f"Report//UI_Testing_Report_{date_dmyhms}.xlsx")
    print("Execution started...")
    execution(counter, api_def_guide_path, manual_excel_guide, report_path)
    print("Execution finished...")
