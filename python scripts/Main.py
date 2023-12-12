import pandas as pd
import datetime as dt
import os
from unidecode import unidecode

CURRENT_DIR = os.getcwd()
INPUT_FILES_FOLDER = os.path.join(CURRENT_DIR, "Data\input_files")
OUTPUT_FILES_FOLDER = os.path.join(CURRENT_DIR, "Data\output_files")

class Response:
    def __init__(self, success:bool = False, message:str = None) -> None:
        self.success = success
        self.message = message

class File:
    def __init__(self, name:str, extension:str) -> None:
        self.name = name
        self.extension = extension
        self._full_name = name + "." + extension
    
    @property
    def full_name(self):
        return self.name + "." + self.extension

def fn_clean_text(s):
    # Check if s is a string
    if isinstance(s, str):
        s = unidecode(s)  # è -> e (unicode transliteration)
        s = s.lower()
        return s

    return s
  
def fn_check_file(file_path:str):
    response = Response()
            
    if os.path.exists(file_path) == False:
        response.message = f"File {file_path} doesn't exist!"
        return response
    
    if ~os.path.isfile(file_path) == False:
        response.message = f"File {file_path} is not a file!"
        return response
    
    response.success = True
    
    return response
    
def clean_ingredients_dataset(input_file:File, output_file:File, ingredient_column_name:str, synonyms_column_name:str, files_to_merge:list = [], columns_to_remove:list = [], columns_to_rename:dict = {}):    
    INPUT_FILE_PATH = os.path.join(INPUT_FILES_FOLDER, input_file.full_name)
    OUTPUT_FILE_PATH = os.path.join(OUTPUT_FILES_FOLDER, output_file.full_name)
    
    check_file = fn_check_file(INPUT_FILE_PATH)
    
    if check_file.success == False:
        print(check_file.message)
        return
    
    df_ingredients = None
    
    if input_file.extension == "xlsx":
        df_ingredients = pd.DataFrame(pd.read_excel(INPUT_FILE_PATH))
    else:
        df_ingredients = pd.DataFrame(pd.read_csv(INPUT_FILE_PATH, sep=';'))
    
    if df_ingredients.empty:
        print(f"File {input_file.name} is empty!")
        return
    
    if len(files_to_merge) > 0:
        for f in files_to_merge:
            temp_path = os.path.join(INPUT_FILES_FOLDER, f.full_name)
            
            check_file = fn_check_file(temp_path)
    
            if check_file.success == False:
                print(check_file.message)
                return
            
            temp_df = pd.DataFrame(pd.read_csv(temp_path, sep=';'))
            
            if temp_df.empty:
                continue
                       
            df_ingredients = pd.concat([df_ingredients, temp_df])     
            
    if len(columns_to_remove) > 0:
        df_ingredients.drop(labels=columns_to_remove, axis=1, inplace=True) #drop unnecessary columns
        
    df_ingredients.reset_index(drop=True,inplace=True)
    
    if len(columns_to_rename) > 0:
        df_ingredients.rename(columns=columns_to_rename, inplace=True)
        
    df_ingredients = df_ingredients.dropna() #drop empty rows

    df_ingredients = df_ingredients[~(df_ingredients[ingredient_column_name].str.startswith("(") | df_ingredients[ingredient_column_name].str.startswith("["))] #delete unnecessary rows

    df_ingredients[synonyms_column_name].replace(to_replace=r"(?<=\d),\s+(?=\d)", regex=True, value=',', inplace=True) #example 1, 3, 4-Octadecanetrio to 1,3,4-Octadecanetrio
    df_ingredients[synonyms_column_name].replace(to_replace=", ", value='|', inplace=True)
    df_ingredients[synonyms_column_name].replace(to_replace=" and ", value='|', inplace=True)
    df_ingredients[synonyms_column_name].replace(to_replace="and ", value='', inplace=True)
    df_ingredients[synonyms_column_name].fillna(df_ingredients[ingredient_column_name], inplace=True)                                            # ako nema synoym, da go stavi generickoto ime
    df_ingredients[synonyms_column_name] = df_ingredients[synonyms_column_name].str.split("|") #split synonyms from string to array of strings
    df_ingredients['synonym'] = df_ingredients.apply(lambda x: x[synonyms_column_name] if x[ingredient_column_name] in x[synonyms_column_name] else [x[ingredient_column_name]] + x[synonyms_column_name], axis=1)

    df_ingredients = df_ingredients.explode(synonyms_column_name)

    df_ingredients[ingredient_column_name] = df_ingredients[ingredient_column_name].str.strip()
    df_ingredients[synonyms_column_name] = df_ingredients[synonyms_column_name].str.strip()

    df_ingredients[synonyms_column_name] = df_ingredients[synonyms_column_name].str.replace(r'\s+', ' ', regex=True)  
    
    df_ingredients["synonym"] = df_ingredients["synonym"].apply(fn_clean_text)

    df_ingredients.drop_duplicates(subset='synonym', inplace=True)
    
    if output_file.extension == "xlsx":
        df_ingredients.to_excel(OUTPUT_FILE_PATH, index=False)
    else:
        df_ingredients.to_csv(OUTPUT_FILE_PATH, sep=";", index=False)
        
        
clean_ingredients_dataset (
    input_file=File("ingredient_w_synonyms", "csv"),
    output_file=File("ingredients_clean", "xlsx"),
    ingredient_column_name="generic_name",
    synonyms_column_name="synonym",
    files_to_merge=[File("additional_ingredients","csv")],
    columns_to_rename={'name': 'generic_name'},
    columns_to_remove=["page_number"]
)