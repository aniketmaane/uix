import os
import sys
import pandas as pd
from pathlib import Path
import UserLibraries.ui_libs as ui

OF_TYPE = ui.OF_TYPE()
NOT_OF_TYPE = ui.NOT_OF_TYPE()
MANDATORY = ui.MANDATORY()

c=0
path = Path(__file__)
ROOT_DIR = path.parent.parent.absolute()
file = str(ROOT_DIR) + "/Input/" + "/manual_guide/master_databuilder.xlsx"

def get_ToExcel(raml, xpaths, title):
    try:
        # function to create new unit_test cases if you want to add new keyword you have to add here
        # all the logic should be here to create that keyword
        to_excel = {}
        theme_id_count = 1
        #df_payload = pd.read_excel(file)
        for key in xpaths:
            if key.__contains__(" = "):
                up_key = key
                xpath = up_key.split(" = ")[-1]
            else:
                up_key = key

            if key in raml.keys() and 'Minimumcharacters:' in raml[up_key].keys() and 'Maximumcharacters:' in raml[up_key].keys():
                keywords = {"class": raml[up_key]["data_type"]}
            elif key in raml.keys() and 'Minimumcharacters:' not in raml[up_key].keys() and 'Maximumcharacters:' not in raml[up_key].keys():
                keywords = {"type": raml[up_key]["data_type"]}
            else:
                continue
            validation_key = raml[up_key]["Validation"]
            if validation_key.__contains__("]["):
            #code for validating PageTitle & AlertText
                validation_key = validation_key.split("][")
                validation_positive = [validation_key[0].split(",")[0].split(":")[-1] + "," + validation_key[1].split(",")[0].split(":")[-1]]
                validation_negative = [validation_key[0].split(",")[1].split(":")[-1] + "," + validation_key[1].split(",")[1].split(":")[-1].replace("]", "")]
            else:
                validation_key = validation_key.split(",")
                validation_positive = [validation_key[0].split(":")[-1]]
                validation_negative = [validation_key[1].split(":")[-1].replace("]", "")]

            if 'Minimumcharacters:' in raml[up_key]:
                keywords["min"] = raml[up_key]['Minimumcharacters:']
            if "Maximumcharacters:" in raml[up_key]:
                keywords["max"] = raml[up_key]['Maximumcharacters:']
                k = [*keywords][0]

            if k== "class":
                for k, v in keywords.items():
                    if k == 'class':
                        if raml[up_key]["data_type"] == 'String':
                            v = "Alpha"
                        elif raml[up_key]["data_type"] == 'Numeric' :
                            v= "Numeric"
                        elif raml[up_key]["data_type"] == "TimeStamp":
                            v = "DDMMYYHHMMSS"

                        elif 'Static' in raml[up_key]["data_type"]:
                            v = raml[up_key]["data_type"].split(":")[-1]


                    if "Static" in keywords["class"]:
                        if k == "class":
                            theme_id = f"{title}_" + str(theme_id_count)
                            theme_id_count += 1
                            if "-" not in v:
                                to_excel[theme_id] = {"xpath": [key], "Expected response": validation_positive,
                                                    "Field Type": ["Alpha"] if raml[up_key]["data_type"]=="String"
                                                    else raml[up_key]["data_type"],
                                                    "Keyword": [f"Static({k}={v})"]}
                            else:
                                max_value = int(v.split("-")[-1])
                                max_value_list = [max_value]

                                for i in max_value_list:
                                    V1 = v.split("-")[0]
                                    v2 = str(i)
                                    v1 = v1 + "-" + v2
                                theme_Id = f"title" + str(theme_id_count)
                                theme_id_count += 1

                                to_excel[theme_id] = {"xpath": [key], "Expected response": validation_positive,
                                                      "Field Type": ["Alpha"] if raml[up_key]["data_type"] == "String" else
                                                      raml[up_key]["data_type"],
                                                      "Keyword": [f"Static({k}={v1})"]}

                    elif "TimeStamp" in keywords["class"]:
                        theme_id = f" {title}_" + str(theme_id_count)
                        theme_id_count += 1

                        if k == "class":
                            to_excel[theme_id] = {"xpath": [key], "Expected response": validation_positive,
                                                  "Field Type": ["Alpha"] if raml[up_key]["data_type"] == "String"
                                                  else raml[up_key]["data_type"],
                                                  "Keyword": [f"TimeStamp({k}={v})"]}

                    elif "Static" not in keywords["class"] and "TimeStamp" not in keywords["class"]:
                        theme_id = f"{title}_" + str(theme_id_count)
                        theme_id_count += 1
                        to_excel[theme_id] = {"xpath": [key], "Expected response": validation_positive,
                                              "Field Type": ["Alpha"] if raml[up_key]["data_type"] == "String"
                                              else raml[up_key]["data_type"],
                                              "Keyword": [f"OF_TYPE({k}={v})"]}

                for k, v in keywords.items():
                    if k == 'class':
                        if raml[up_key]["data_type"] == 'String':
                            v = "Alpha"
                        elif raml[up_key]["data_type"] == 'Numeric':
                            v = "Numeric"
                        elif raml[up_key]["data_type"] == "TimeStamp":
                            v = "Alphanumeric"
                        elif 'Static' in raml[up_key]["data_type"]:
                            if v.__contains__("Pattern"):
                                v = 'Alphanumeric'
                            else:
                                v = raml[up_key]["data_type"].split(":")[-1]

                    theme_id = f"{title}_" + str(theme_id_count)
                    theme_id_count += 1

                    to_excel[theme_id] = {"xpath": [key], "Expected response": validation_negative,
                                          "Field Type": ["Alpha"] if raml[up_key]["data_type"] == "String"
                                          else raml[up_key]["data_type"],
                                          "Keyword": [f"NOT_OF_TYPE({k}={v})"]}

                theme_id = f"{title}_" + str(theme_id_count)
                theme_id_count += 1

                to_excel[theme_id] = {"xpath": [key], "Expected response": "Rapido Contact- Get in touch with us",
                                      "Field Type": ["Alpha"] if raml[up_key]["data_type"] == "String"
                                      else raml[up_key]["data_type"],
                                      "Keyword": ["MANDATORY(EMPTY)"]}

    except:
        vOutcome = 'FAIL:get_ToExcel-->' + str(sys.exc_info())
    else:
        vOutcome = to_excel
    finally:
        return vOutcome

def raml_to_excel(page_name, raml_data):
    try:
        vOutcome = 'FAIL:Default-->raml_to_excel_Json'
        frames = pd.DataFrame()
        df_payload = pd.read_excel(file)
        counter = 0
        list_value = []
        list_keyword_value = []
        value = []

        for name, field_details in raml_data.items():

            for i, row in df_payload.iterrows():
            #print(type(row[ "VALUE"]))| # row[ "VALUE"] = row[ "VALUE"J .astype(str)| # print(type(row[ "VALUE"]))| # if page_name=="References"： print (1).
                if field_details["xpath"][0].__contains__("]["):
                    xpath = field_details["xpath"][0].split("]]")[-1]
                else:
                    xpath = field_details["xpath"][0]

                if df_payload.iloc[i]['FIELD_XPATH'] == xpath and df_payload.iloc[i]['PAGE_TITLE'] == page_name:
                    if str(row["VALUE"]) != 'nan' and field_details['Keyword'][0].__contains__("Static"):
                        values = row["VALUE"]
                        values = str(values).split("!")
                        value = values

                        for value in values:
                            # print(type(V)
                            keyword_value = page_name + xpath + value
                            keyword_value = keyword_value.replace(" ", "")
                            if keyword_value in list_keyword_value:
                                continue
                            else:
                                list_value.append(value)
                                list_keyword_value.append(keyword_value)
                else:
                    continue

                key = field_details['Keyword'][0]

                if key == "Static(class=Static)":
                    if len(values) > 1:
                        for i in range(len(value)):
                            frame = pd.DataFrame(field_details)
                        frames = pd.concat([frames, frame], ignore_index=True)
                        break
                    else:
                        frame = pd.DataFrame(field_details)
                        frames = pd.concat([frames, frame], ignore_index=True)
                        break

                elif key.__contains__("Static") and key.__contains__("Alphanumeric"):
                    if len(values) > 1:
                        for i in range(len(value)):
                            frame = pd.DataFrame(field_details)
                            frames = pd.concat([frames, frame], ignore_index=True)
                            break
                    else:
                        frame = pd.DataFrame(field_details)
                        frames = pd.concat([frames, frame], ignore_index = True)
                        break
                elif key.__contains__("Static") and key.__contains__("Numeric"):
                    if len(values) > 1:
                        for i in range(len(value)):
                            frame = pd.DataFrame(field_details)
                            frames = pd.concat([frames, frame], ignore_index=True)
                    else:
                        frame = pd.DataFrame(field_details)
                        frames = pd.concat([frames, frame], ignore_index=True)
                        break

                elif key.__contains__("Static") and key.__contains__("Alpha"):
                    if len(values) > 1:
                        for i in range(len(value)):
                            frame = pd.DataFrame(field_details)
                            frames = pd.concat([frames, frame], ignore_index=True)
                    else:
                        frame = pd.DataFrame(field_details)
                        frames = pd.concat([frames, frame], ignore_index=True)
                        break
                else:
                    frame = pd.DataFrame(field_details)
                    frames = pd.concat([frames, frame], ignore_index=True)
                    break

        frames.insert(4, 'Value', "")

        try:
            for index, row in frames.iterrows():
                fieldType = row["Field Type"]
                method = row["Keyword"]
                field_name = row["xpath"]
                min = 0
                max = 0
                dfrow = df_payload[(df_payload["FIELD_XPATH"] == field_name) & (df_payload["PAGE_TITLE"] == page_name)]
                # for Reference Page
                if len(dfrow)>1:
                    dfrow = dfrow.iloc[0]

                if fieldType == "Alpha" or fieldType == "Alphanumeric" \
                        or fieldType == "Numeric" or fieldType == "Alpha" or fieldType == "Static" \
                        or fieldType.__contains__('Static:Alpha') or fieldType._contains_('Static:Alphanumeric') \
                        or fieldType.__contains__('Static:Numeric'):

                    min = int(dfrow["MIN"])
                    max = int(dfrow["MAX"])

                    if method.__contains__("NOT_OF_TYPE") and "min" not in method and "max" not in method:
                        method = method.split("-")[0]
                    elif fieldType == "radio" or fieldType == "checkbox":
                        method = method
                    elif fieldType.__contains__("dropdown"):
                        method = method
                        dropdown_list = [dfrow['VALUE'].values[0],""]

                    if 'NOT_OF_TYPE' in method:
                        listFrmCurrentExecution = executeNotOfType(method, fieldType, min, max)

                    elif "OF_TYPE" in method and 'pattern' not in method:
                         listFrmCurrentExecution = executeOfType(method, fieldType, min, max)

                    elif 'MANDATORY' in method: # execute if mandatory
                        if fieldType.__contains__("dropdown") and "YES" in method:
                            listFrmCurrentExecution = dropdown_list[0]
                        elif fieldType.__contains__("dropdown") and "NO" in method:
                            listFrmCurrentExecution = dropdown_list[1]
                        else:
                            listFrmCurrentExecution = executeMandatory(method)

                    elif 'Static' in method and "-" not in method:
                        listFrmCurrentExecution = list_value[counter]
                        counter = counter + 1

                    elif 'Static' in method and 'Alpha' in method:
                        listFrmCurrentExecution_1 = list_value[counter]
                        listFrmCurrentExecution_2 = executeOfType(method, fieldType, min, max)
                        listFrmCurrentExecution = listFrmCurrentExecution_1 + listFrmCurrentExecution_2
                        counter = counter + 1

                    elif 'Static' in method and "Alphanumeric" in method:
                        listFrmCurrentExecution_1 = list_value[counter]
                        listFrmCurrentExecution_2 - executeOfType(method, fieldType, min, max)
                        listFrmCurrentExecution =  listFrmCurrentExecution_1 + listFrmCurrentExecution_2
                        counter = counter + 1

                    elif "Static" in method and "Numeric" in method:
                        listFrmCurrentExecution_1 = list_value[counter]
                        listFrmCurrentExecution_2 = executeOfType(method, fieldType, min, max)
                        listFrmCurrentExecution = listFrmCurrentExecution_1 + listFrmCurrentExecution_2
                        counter = counter + 1

                    elif "Static" in method and "Pattern" in method:
                        listFrmCurrentExecution_1 = list_value[counter]
                        listFrmCurrentExecution_2 = executePattern(method)
                        listFrmCurrentExecution = listFrmCurrentExecution_1 + listFrmCurrentExecution_2
                        counter = counter + 1

                    frames.at[index, 'Value'] = listFrmCurrentExecution # ***listFrmCurrentExecution
                    global c
                    # print(c)
                    c = c + 1
                    if index + 1 == len(frames):
                        break

        except:
            print(str(sys.exc_info()))

        # list = pd.Series(1)
        # df['Value'] = list.values
        # frames.loc(index).at['Value"］= listFrmcurrentExecution

        strDefGuidePath= str(ROOT_DIR)+f'/Output/Ui_Def_Guide/{page_name.replace(" ", "").replace("/", "")}_Guide.xlsx'

        if not os.path.isfile(strDefGuidePath):
            frames.to_excel(strDefGuidePath, sheet_name='TestData', index=False)
        else:
            with pd.ExcelWriter(strDefGuidePath, engine='openpyxl', mode='a', if_sheet_exists='replace') as excelwriter:
                    frames.to_excel(excelwriter, sheet_name='TestData', index=False)
        print(f'Test Data Created = {len(frames)} ')
        print(f'UI DEF Guide Created. ')
        print('-'*70)

    except:
        vOutcome = 'FAIL:raml_to_excel_Ison-->'+str(sys.exc_info())

    else:
        vOutcome='PASS:raml_to_excel_json'

    finally:
        return vOutcome



def executePattern(method):
    if "-" in method:
        regex = method.split('-', 1)[1]
        regex = regex.replace ("'", '')
        regex = regex[:-2].replace("'", " ").replace("(", "")
        value = rstr.xeger(repr(regex))
        value = value.replace("'", '')

    else:
        regex = method.split('(', 1)[1]
        regex = regex.replace ("'", '')
        regex = regex[:-2].replace("'", '')
        value = rstr.xeger(repr(regex))
        value = value.replace("'", '')
        return value

def executeMandatory (method):
    className = method.split('(', 1)[0]
    value = method.split('(', 1)[1]
    value = value.replace(")", "")
    if value == 'EMPTY':
        dictionary = {'method': 'EMPTY'}
    elif value == 'MISSING':
        dictionary = {'method': 'MISSING'}
    elif value == 'YES':
        dictionary = {'method': 'YES'}
    elif value == "NO":
        dictionary = {'method':'NO'}

    classObj = eval(className)
    func = getattr(classObj, className)

    if dictionary['method'] == "Boolean":
        return func(method=dictionary['method'])
    else:
        return func(method=dictionary['method'])

def executeNotOfType(method, fieldType, min_value, max_value):
    if "_" in fieldType:
        if "Pattern" not in fieldType:
            fieldType = fieldType.split(":")[-1].split("-", 1)[0]
        else:
            fieldType = "Alphanumeric"
    else:
        if "TimeStamp" in fieldType:
            fieldType = "Alphanumeric"
        else:
            fieldType = fieldType.split(":")[-1]

    className = method.split('(', 1)[0]
    value = method.split('(', 1)[1]
    key = value.split("=")[0]
    value = value.split("=")[1].replace(')', "")
    #print(type(value))

    if value.__contains__("."):
        value = value.split(".")[0]
    if key == 'class':
        dictionary = {"class": value, "min": min_value, "max": max_value, "method": "class"}
    elif key == 'max':
        dictionary = {"class": fieldType, "min": '1', "max": max_value, "method": "max"}
    elif key == 'min':
        dictionary = {"class": fieldType, "min": min_value, "max": "10", "method": "min"}

    classObj = eval(className)
    func = getattr(classObj, className)

    if dictionary['class'] == "Boolean":
        return func(value=dictionary["class"])
    else:
        return func(value=dictionary["class"], min= dictionary["min"]
                    , max=dictionary["max"], method=dictionary["method"])

def executeOfType(method, fieldType, min_value, max_value):

    className = method.split('(', 1)[0]
    value = method.split('(', 1)[1]
    key = value.split("=")[1]

    if '-' not in value:
        value = value.split("=")[1].replace(')', '')
    else:
        value = value.split("-")[1].replace(')', '')

    if key == 'class' and className == 'OF_TYPE':
        dictionary = {'class': value, 'min': min_value, 'max': max_value, 'method': 'class'}
    elif key == 'class' and className == 'Static':
        dictionary = {'class': fieldType, 'min': '1', 'max': value, "method": 'max'}
    elif key == 'max' :
        dictionary = {'class': fieldType, 'min': '1', 'max': value, 'method': 'max'}
    elif key == 'min':
        dictionary = {'class': fieldType, 'min': value, 'max': '10', 'method': 'min'}

    if className == "Static":
        className = "OF_TYPE"

    classObj = eval(className)
    func = getattr(classObj, className)

    if dictionary['class'] == "Boolean":
        return func(value=dictionary['class' ])
    else:
        return func(value=dictionary['class'], min=dictionary['min'],max=dictionary['max'], method=dictionary ['method'])
