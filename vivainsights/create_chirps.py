# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import vivainsights as vi
import pkg_resources

def create_chirps(data: pd.DataFrame,
                  brief: str = None,
                  metrics: list = None,
                  hrvar: list = ["Organization", "SupervisorIndicator"],
                  bm_hrvar: list = ["FunctionType", "SupervisorIndicator"],
                  min_group: int = 5,
                  bp = {},
                  return_type = 'standard'
                  ):
    
    """
    Name
    ----
    create_chirps
    
    Description
    ------------    
    This function creates headlines based on the provided data, brief, metrics, and other parameters.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame containing the Person Query data to run the data on. 
        The Person Query should be grouped at a weekly level, and must contain the columns `PersonId` and `MetricDate`.
    
    brief : str, optional
        The brief for which the metrics are to be returned. Defaults to None.
        Valid briefs are:
        - Collaboration patterns
        - After-hours work
        - Working on weekends
        - External connection
        - Inefficient meetings
        - Meeting scheduling
        - Time in meetings
        - Punctuality
        - Advanced notice
        - Meeting size and duration
        - Network sizes
        - Time to focus
        - Focus time adoption
        - Hybrid work
        - Manager coaching time
        - Healthy rhythms
        - Shifting directions
        - Confidence in leadership
        - Alignment with career goals
        - Urgency
        - Visibility
        
        `brief_to_metrics()` is used to extract the metrics associated with each brief.
    
    metrics : list, optional
        A list of metrics to be included in the analysis. Defaults to None.
        Each metric should correspond to a column name in `data`.

    hrvar : list
        A list of the HR or organizational variables to group by when computing headline metrics.  
        Defaults to `['Organization', 'SupervisorIndicator']`.
    
    bm_hrvar : list, optional
        A list of benchmark human resource variables. Defaults to ["FunctionType", "SupervisorIndicator"].
    
    min_group : int, optional
        The minimum group size set for privacy. Defaults to 5.
        Groups with fewer people than `min_group` will not be included in the analysis.
    
    bp : dict
        A dictionary containing the benchmark mean for each metric and the directionality of the threshold.  
        `bp` requires a two-level nested dictionary where the first level consists of two explicit keys: 'above' and 'below'.
        Each of these keys maps to a second-level dictionary, which contains its own set of key-value pairs.
        The keys in the second-level dictionaries represent metrics, and the values represent the corresponding thresholds
        The keys should correspond to the metric names and the values should be the benchmark means. 
        By default, this uses the dictionary output from `extract_best_practice()`. 
        
    return_type : str, optional
        The type of output to return. Defaults to 'standard'.
        Valid options are:
        - 'standard': Returns a DataFrame containing all the columns.
        - 'compact': Returns a DataFrame containing only the columns `Attribute`, `AttributeValue`, and `Headlines`.

    Returns
    -------
    pd.DataFrame: When `return_type == 'standard'`, a data frame containing the following columns:
        - `TestType`: The type of test.
        - `Attribute`: The name of the HR or organizational attribute. 
        - `AttributeValue`: The value of the group identified by the HR or organizational attribute.
        - `Metric`: The name of the metric.
        - `MetricValue`: The value of the metric.
        - `n`: The number of people in the group.
        - `Headlines`: String containing the headline surfaced in the analysis. 
        - `Interest_Score`: The interest score for the test.
        
    pd.DataFrame: When `return_type == 'compact'`, a data frame containing the following columns:
        - `Attribute`: The name of the HR or organizational attribute. 
        - `AttributeValue`: The value of the group identified by the HR or organizational attribute.
        - `Headlines`: String containing the headline surfaced in the analysis.

    Raises
    ------
    ValueError: If neither `brief` nor `metrics` are provided.
    """
    
    # Either `brief` or `metrics` must be provided
    if not brief and not metrics:
        raise ValueError('Either `brief` or `metrics` must be provided.')
    
    # If `brief` is not None, run `brief_to_metrics`, which returns a list of metrics
    # Otherwise, set up an empty list
    if brief:
        all_metrics = brief_to_metrics(brief) 
    elif not brief:
        all_metrics = []
     
    # Set up empty list for merging
    if not metrics:
        metrics = []    
        
    # If values are provided to both `brief` and 'metrics', then the final metrics will be combined. 
    all_metrics = list(set(all_metrics + metrics))
    
    # Diagnostic
    print(f'Crunching headlines for the following metrics: {all_metrics}')
    
    # If 'MetricDate' is not DateTime, convert to DateTime
    if data['MetricDate'].dtype != 'datetime64[ns]':
        data['MetricDate'] = pd.to_datetime(data['MetricDate'])    
    
    # 1. Trend test - 4 weeks vs 12 weeks -------------------------------------
    
    list_ts = vi.test_ts(
        data = data,
        metrics = metrics,
        hrvar = hrvar,
        min_group = min_group,
        bp = bp,
        bm_hrvar = bm_hrvar,
        return_type = 'headlines'
        )
    
    # 2. Internal benchmark test ----------------------------------------------
    
    list_int_bm = vi.test_int_bm_lfl(
        data = data,
        metrics = metrics,
        hrvar = hrvar,
        bm_hrvar = bm_hrvar, 
        min_group = min_group,
        return_type = 'headlines'
        )
    
    # 3. Best practice test ---------------------------------------------------
    
    list_bp = vi.test_best_practice(
        data = data,
        metrics = metrics,
        hrvar = hrvar,
        bp = bp,
        return_type = 'headlines'
        )
    
    # All the headlines -------------------------------------------------------
    
    list_headlines = [list_ts, list_int_bm, list_bp]

    all_headlines = pd.concat(list_headlines)
    
    # If no headlines are generated, return an empty DataFrame
    if all_headlines.empty:
        print('There are no qualified headlines. Please try again with a different set of parameters.')
        return all_headlines
    
    # Additional calculations ------------------------------------------------   
    
    total_n = data['PersonId'].nunique()
    all_headlines['prop_n'] = all_headlines['n'] / total_n
    
    # Interesting score -------------------------------------------------------
    # Output - return all the headlines - append the interesting score
    
    # If `TestType == 'Internal Benchmark'`, then multiply `Interest_Score` by 0.9
    all_headlines['Interest_Score'] = np.where(
        all_headlines['TestType'] == 'Internal Benchmark',
        all_headlines['Interest_Score'] * 0.9,
        all_headlines['Interest_Score']
        )    
    
    # If `TestType == 'Best Practice'`, then multiply `Interest_Score` by 0.8
    all_headlines['Interest_Score'] = np.where(
        all_headlines['TestType'] == 'Best Practice',
        all_headlines['Interest_Score'] * 0.8,
        all_headlines['Interest_Score']
        )
    
    all_headlines['Interest_Score2'] = all_headlines['Interest_Score'] * all_headlines['prop_n']
    
    # `Interest_Score2_minmax` - min-max scaled score
    all_headlines['Interest_Score2_minmax'] = (
        all_headlines['Interest_Score2'] - all_headlines['Interest_Score2'].min()) / (
            all_headlines['Interest_Score2'].max() - all_headlines['Interest_Score2'].min()
            )
    # `Interest_Score2_minmax` - min-max scaled score
    all_headlines['Interest_Score'] = all_headlines['Interest_Score'] * all_headlines['n'] / total_n
    
    # Drop and rename columns
    all_headlines = all_headlines.drop(columns=['prop_n', 'Interest_Score', 'Interest_Score2'])
    all_headlines.rename(columns={'Interest_Score2_minmax': 'Interest_Score'}, inplace=True)   
    
    # Sort 'Interest_Score' in descending order
    all_headlines = all_headlines.sort_values(by='Interest_Score', ascending=False) 
    
    # Return output
    if return_type == 'standard':
        return all_headlines
    elif return_type == 'compact':
        # Only return Attribute, AttributeValue, Headlines
        compact_headlines = all_headlines.groupby(['Attribute', 'AttributeValue']).agg(
            {'Headlines': lambda x: ' '.join(x)}
            ).reset_index()
        return compact_headlines
    else:
        raise ValueError('Invalid `return_type`. Please select either `standard` or `compact`.')


def brief_to_metrics(brief: str):
    """
    Name
    ----
    brief_to_metrics
    
    Description
    ------------    
    Accepts a brief and returns a list of metrics associated with the brief.
    
    Parameters
    ----------
    brief : str
        The brief for which the metrics are to be returned.
    """
    
    # Read in the briefs and metrics file
    if(pkg_resources.resource_exists(__name__, 'data/briefs_and_metrics.csv')):
        stream = pkg_resources.resource_stream(__name__, 'data/briefs_and_metrics.csv')
    elif(pkg_resources.resource_exists(__name__, '../data/briefs_and_metrics.csv')):
        stream = pkg_resources.resource_stream(__name__, '../data/briefs_and_metrics.csv')
    else:
        print('Error: please report issue to repo maintainer')
        
    briefs_and_metrics = pd.read_csv(stream, encoding='utf-8')
    
    # Standardise case for easier matching
    briefs_and_metrics['Brief'] = briefs_and_metrics['Brief'].str.lower()
    brief = brief.lower()
        
    # Convert to dictionary
    brief_metric_dict = briefs_and_metrics.groupby('Brief')['Metric'].apply(list).to_dict()
    
    # If 'brief' value is not in the dictionary, it returns an empty list.    
    return brief_metric_dict.get(brief, [])

def extract_best_practice():
    """
    Name
    ----
    extract_best_practice
    
    Description
    ------------
    Extract the best practice thresholds from a list of default best practices.
    To be used in conjunction with `create_chirps()` and `test_best_practice()`. 
    
    Returns
    -------
    dict: A dictionary containing the best practice thresholds.
    
    """
    
    # Read in the best practice file
    if(pkg_resources.resource_exists(__name__, 'data/best_practice.csv')):
        stream = pkg_resources.resource_stream(__name__, 'data/best_practice.csv')
    elif(pkg_resources.resource_exists(__name__, '../data/best_practice.csv')):
        stream = pkg_resources.resource_stream(__name__, '../data/best_practice.csv')
    else:
        print('Error: please report issue to repo maintainer')
        
    best_practice = pd.read_csv(stream, encoding='utf-8')
    
    # Create a nested dictionary
    best_practice_dict = {}
    for _, row in best_practice.iterrows():
        direction = row['Direction']
        metric = row['Metric']
        threshold = row['Threshold']
        
        if direction not in best_practice_dict:
            best_practice_dict[direction] = {}
        
        best_practice_dict[direction][metric] = threshold
    
    return best_practice_dict