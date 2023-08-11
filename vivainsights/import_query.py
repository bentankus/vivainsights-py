# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
This function imports a Viva Insights Query from a .csv file and optimizes the
variable classifications for other functions in the package. The function takes in a file path (x)
and an optional encoding parameter (default is 'utf-8'). It checks if the file is a .csv file, reads
in the file using pandas, cleans the column names by removing spaces and special characters, and
returns the resulting data as a pandas dataframe. If there is an error reading the file, the function prints an error message.
"""
import pandas as pd
import re 

def import_query(x, encoding: str = 'utf-8'):
    """
    Name
    ----
    import_query

    Description
    ----------- 
    The function `import_query` reads a CSV file, removes leading and trailing spaces from column names,
    and replaces spaces and special characters with underscores in column names.
    
    Parameters
    ----------
    x : 
        The parameter `x` is the input file name or path. It should be a string representing the file name or path of the CSV file you want to import.
    encoding : str, optional
        The encoding parameter specifies the character encoding to be used when reading the CSV file. The default value is 'utf-8', which is a widely used encoding for text files. However, you can specify a different encoding if needed.
    
    Returns
    -------
        The variable `data` if the input file is a valid CSV file. If the input file is not a valid CSV
    file, the function will print an error message and return `None`.
    """    
    
    # in case '.csv' is not all in lower case, make it lower case
    if x[-4:].lower() == '.csv':
        x = x[:-4] + '.csv'
    
    try:
        # Check if '.csv' exists in variable x.
        if re.search('.csv', x):
            try:
                # Try to read in csv file, if file can not be read, exception is thrown.
                data = pd.read_csv(x, encoding=encoding, delimiter=',')
                # Remove leading and trailing spaces
                # Remove spaces and special characters and replacing them with underscores within column names.
                data.columns = [re.sub('[^a-zA-Z0-9,]', '_', c.strip()) for c in data]
            except: 
                print('Something went wrong when reading the file')
                
        return data
            
        
    except:
        print('The input file must be a .csv file')
