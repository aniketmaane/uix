import json
import sys

# from sqlalchemy import create_engine
import pandas as pd
# import cx_Oracle
import warnings
from pathlib import Path
import os
import configparser
from xml.etree import ElementTree as et
from UserLibraries.ui_def_guide import *

# from Interfaces.get_db_pass import get_db_pass_from_es
# from Utilities.APIDefGuideTempleteWriter import Get_Templete_writer
# from Utilities.api_def_guide import get_ToExcel, raml_to_excel
# from Utilities.raml_support import normalize_raml,Get_Xml_Scanner

warnings.filterwarnings ("ignore")

def gen_def_guide_excel():
    count = 0
    path = Path(__file__)
    ROOT_DIR = path.parent.parent.parent.absolute()
    #print(tupe(ROOT_DIR))
    file = str(ROOT_DIR) + "/Input/" + "/manual_guide/" + "master_databuilder.xlsx"
    manual_guide_path = os.path.join(ROOT_DIR, "manual_guide")
    manual_excel = "master_databuilder.xlsx"

    ############ RAML forms #############
    df = pd.read_excel(file)

    df = pd.read_excel(file)
    other_df = pd.DataFrame()
    correct_frames = pd.DataFrame()
    incorrect_frames = pd.DataFrame()
    continous_incorrect = pd.DataFrame()
    correct_api_list = []

    apis = Get_Apis_Dict(df)

    for key, val in apis.items():
        correct = True
        wrong_fields = []
        for field in val["FIELD_XPATH"]:
            if field["MIN"] != "No" and field["MAX"] != "No":
                pass
            else:
                wrong_fields.append(field["FIELD_XPATH"])
                correct = False

        if correct:
            correct_api_list = correct_api_list + val["FIELD_XPATH"]
            val.pop("FIELD_XPATH")
            frame = pd.DataFrame(val)
            correct_frames = pd.concat([correct_frames, frame],ignore_index = True)
            # correct_frames = correct_frames.append(frame, ignore_index=True)
        else:
            val.pop("FIELD_XPATH")


    ############################## RAML forms ########################

    #correct_frames.drop(['APP'], axis=1, inplace=True)

    # df1 = pd.Series(['True', 'True', 'True
    # correct frames["Toggle"] = "True""True"], name = 'Toggle ')
    tog = []
    for i in range(len(correct_frames)):
        tog.append(True)

    df1 = pd.Series(tog, name='Toggle')
    df = pd.concat([correct_frames, df1], axis=1)
    #print(df.dtypes)
    strDefGuidePath = str(ROOT_DIR) + f'/Output/ui_execution_guide.xlsx'
    df.to_excel(strDefGuidePath, sheet_name="PAGE_DATA", index=False)

    dict_json = {}
    # api: [list of dataframe rows format]-
    test_json = {}

    for row in correct_api_list:
        # print(correct_api_list)
        if row["PAGE_TITLE"] not in dict_json:
            dict_json[row["PAGE_TITLE"]] = []
            dict_json[row["PAGE_TITLE"]].append(row)
        else:
            dict_json[row["PAGE_TITLE"]].append(row)

        # print(dict_json)

    for page_title, fields in dict_json.items():
        field_data = {}
        for row in fields:
            if type(row['DATATYPE']) != float:
                if page_title not in test_json:
                    test_json[page_title] = {}
                    test_json[page_title][row['FIELD_XPATH']] = {'data_type': row['DATATYPE'],
                                                               'Minimumcharacters:' : int(row['MIN']), 'Maximumcharacters:': int(row["MAX"]),
                                                                "Validation": row['VALIDATION']}

                else:
                    test_json[page_title][row['FIELD_XPATH']] = {'data_type': row['DATATYPE'],
                                                                 'Minimumcharacters:': int(row['MIN']),'Maximumcharacters:': int(row["MAX"]),
                                                                 "Validation": row['VALIDATION']}
            else:
                continue

    print("UI DEF Guide creation started...")
    print('-' * 70)
    for page_title, data in test_json.items():
        try:
            print(f'Web Page Title: {page_title}')
            normalised_xpath = []
            for key in data.keys():
                normalised_xpath.append(key)

            to_excel = get_ToExcel(data, normalised_xpath, page_title)
            # print(to_excel)
            # for apiname, field details in to_excel.items():

            raml_to_excel(page_title, to_excel)

        except Exception as KeyError:
            print("some fields are missing in master data")

    # print("="+70)
    print("API's DEF Guide creation completed!")
    # print(f"Total test data created = fcount)")

#This method is used to parse the JSON Payload and convert
# into dictionary format to hit multiple requests in a loop
def Get_Apis_Dict(df):
    try:
        vOutcome = 'FAIL:Default-->Get_Apis_Dict'
        apis = {}
        for idx, row in df.iterrows():
            if row["PAGE_TITLE"] not in apis:
                apis[row["PAGE_TITLE"]] = {}
                apis[row["PAGE_TITLE"]]["APP"] = [row["APP"]]
                apis[row["PAGE_TITLE"]]["PAGE_TITLE"] = [row["PAGE_TITLE"]]
                apis[row["PAGE_TITLE"]]["URL"] = [row["URL"]]
                apis[row["PAGE_TITLE"]]["PRECONDITIONS"] = [row["PRECONDITIONS"]]
                apis[row["PAGE_TITLE"]]["FIELD_XPATH"] = []
                apis[row["PAGE_TITLE"]]["FIELD_XPATH"].append(row)
            else:
                apis[row["PAGE_TITLE"]]["FIELD_XPATH"].append(row)
    except:
        vOutcome = 'FAIL:Get_Apis_Dict-->'+str(sys.exc_info())
    else:
        vOutcome = apis
    finally:
        return vOutcome

if __name__ == "__main__":
    gen_def_guide_excel()


