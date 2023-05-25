# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
def us_to_space(string):
    """
    The function replaces underscores with spaces in a given string.
    
    :param string: A string that may contain underscores that need to be replaced with spaces
    :return: The function `us_to_space` takes a string as input and replaces all underscores with spaces
    using the `replace` method. It then returns the modified string with spaces instead of underscores.
    """
    return string.replace("_", " ")