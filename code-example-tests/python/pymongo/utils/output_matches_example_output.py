import json
import re
import os
from datetime import datetime
from bson import Decimal128, ObjectId

def preprocess_file_contents(contents):
    # Detect multiple objects and wrap them into an array 
    contents = contents.strip()  
    contents = re.sub(r"}\n{", "},\n{", contents) # Add commas between objects if they are concatenated
    contents = re.sub(r"'(.*?)'", r'"\1"', contents) # Convert single-quoted values to double quotes  
    contents = re.sub(r"^\{", "[{", contents) # Wrap first object in an array if no array starts
    contents = re.sub(r"\}$", "}]", contents) # Wrap last object in an array if no array ends

    # Ensure keys are quoted properly  
    processed = re.sub(  
        r"(\b[a-zA-Z_]\w*)\s*:",  # Match alphanumeric keys (letters, optional underscores) followed by a colon  
        r'"\1":',  # Wrap the key in double quotes without touching the colon  
        contents
    )

    # Quote any unquoted ISO-like date values for the dateofbirth key
    # Avoids the issue "dateofbirth": "datetime(1998", 12, 26...
    ISO_processed = re.sub(
        r'"dateofbirth"\s*:\s*(("(?:[^"]+)")|(\d{4}-\d{2}-\d{2}))',  # Match dateofbirth field and values  
        lambda match: f'"dateofbirth": "{match.group(1).strip()}"',
        processed
    )

    final_processed = re.sub(
        r'datetime\(([^)]+)\)',
        r'"datetime(\1)"',
        ISO_processed
    )

    return final_processed # Return final sanitized string

context = {  
        "Decimal128": lambda value: Decimal128(value),  
        "ObjectId": lambda value: ObjectId(value),  
        "Date": lambda value: datetime.fromisoformat(value),  
}  

def run_in_new_context(processed_expected_output):
    expectedOutputArray =[]
    try:  
        # Safely parse expected output
        expectedOutputArray = eval(processed_expected_output, context)  
        return expectedOutputArray
    except Exception as error:  
        print("Failed to parse expected output:", error)  
        return False  

# Helper function to normalize MongoDB data types for comparison  
def normalize_item(item):  
    normalized = {}  
    for key, value in item.items():  
        if isinstance(value, Decimal128) or isinstance(value, ObjectId):  
            normalized[key] = str(value) # Convert Decimal128 and ObjectId to strings  
        elif isinstance(value, datetime):  
            normalized[key] = value.isoformat() # Convert dates to ISO8601 strings  
        else:  
            normalized[key] = value # Keep other values as-is  
    return normalized  

def output_matches_example_output(filepath, output):
    # Read the content of the expected output file  
    filepath_string = f"/examples/{filepath}"
    filepath_prefix = os.path.dirname(__file__).replace("utils", "")
    output_file_path = filepath_prefix + filepath_string
    
    try:  
        with open(output_file_path, "r", encoding="utf8") as expected_file:  
            raw_expected_output = expected_file.read()  
    except Exception as e:  
        print("Failed to read expected output file:", e)  
        return False

    processed_expected_output = preprocess_file_contents(raw_expected_output)
    expected_output_array = run_in_new_context(processed_expected_output)

    # Directly use the `output` as it is already expected to be a valid array of objects
    actual_output_array = output

    if actual_output_array is None or expected_output_array is None:  
        print("One or both arrays are undefined.")  
        return False  

    if len(actual_output_array) != len(expected_output_array):  
        print("Mismatch in array lengths.")  
        return False
    
    all_elements_match = all(  
        any(  
            json.dumps(normalize_item(actual_item), sort_keys=True) ==  
            json.dumps(normalize_item(expected_item), sort_keys=True)  
            for actual_item in actual_output_array  
        )  
        for expected_item in expected_output_array  
    )  

    if not all_elements_match:
        print(  
            "Mismatch between actual output and expected output:",   
            actual_output_array, expected_output_array  
        )  
        return False  
    return all_elements_match