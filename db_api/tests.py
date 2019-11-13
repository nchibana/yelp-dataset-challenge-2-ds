import requests
import numpy as np
import hashlib
import json
import pandas as pd
import time
from multiprocessing import Pool

## Test Helper Functions (from snippets - may be old.  See snippets for up-to-date functions.)

def generate_id(record):
    """Generate ID returns a repeatable hash of a given record.

    param record: python string, list, or dictionary, pandas.series
    type record: string
    """
    import hashlib
    import pandas as pd
    # Convert series to dictionary object for encoding
    if type(record) == pd.Series:
        record = str(record.to_dict())
    else:
        record = str(record)
    # Encode record to bytes
    record = record.encode()
    return hashlib.sha256(record).hexdigest()

def df_to_query(df, tablename):
    """Transform dataframe into dictionary object of correct form for database api request parsing.

    param df: Tabular data to transform
    type df: Pandas.DataFrame
    """
    import json

    def transform_df(df):
        # Generate a list of stringified dictionaries from the dataframe
        #   Note: Will transform the entire supplied dataframe.  Split datframe into chunks prior.
        records_list = df.to_json(orient='records', lines=True).split('\n')
        # Cast stringified row entris as python dict vis json loads (important for request)
        cast_records = [json.loads(x) for x in records_list]
        return cast_records

    package = {
        'table_name': tablename,
        'data': transform_df(df)
    }

    return package


def build_databunch(query, num_splits=3, max_size=None):
    import math
    databunch = []

    # Caclulate number or splits or set (dependent on max_size)
    if max_size:
        num_splits = math.ceil(len(query['data'])/max_size)

    bunch_size = int(len(query['data']) / num_splits)

    for i in range(num_splits):
        if i < num_splits-1:
            data_range = (i*bunch_size, (i+1)*bunch_size)
        else:
            data_range = (i*bunch_size, len(query['data']))
        databunch.append(
            {
                'table_name': query['table_name'],
                'data': query['data'][data_range[0]:data_range[1]]
            }
        )
    return databunch


import logging
import os
request_logger = logging.getLogger(__name__+" request:")
log_path = os.path.join(os.getcwd(), 'instance/logs/debug.log')
logging.basicConfig(filename=log_path, level=logging.INFO)
def parallel_post_requests(databunch, url, max_requests=10):
    """Request handler that will parallelize databunch POST requests.

    param databunch: Packages to POST to database API
    type databunch: list of packages
    param max_requests: How many simultaneous requests sessions to attempt
    type max_requests: int
    param url: Endpoint url.  Must be valid ipv4 or dns entry.
    type url: string
    """
    # Move imports to top of file for performance.
    from multiprocessing import Pool
    from functools import partial

    runner = partial(run_request, url=url)
    p = Pool(max_requests)
    p.map(runner, databunch)


def run_request(bunch, url):
    """Run and time a request with the python requests library
    """
    import requests
    import time
    import numpy as np
    try:
        time.sleep(np.random.random_sample()*10)
        start = time.time()
        response = requests.post(url=url, json=bunch)
        assert response.status_code == 200
        request_logger.info("POST succeded.  Status= {}".format(response.status_code))
        stop = time.time()
        request_logger.info('Batch of {} processed in {}'.format(len(bunch['data']), stop-start))
        return True
    except:
        request_logger.error("POST failed.  Trying again")
        run_request(bunch=bunch, url=url)

###########
###Tests###
###########

# TEST 1: Simple loading of business with manual dict
# def generate_test_data():
#     test_data = {
#         'table_name': 'businesses',
#         'data': [
#                 {
#             "business_id": hashlib.sha256(str(np.random.randint(0, 100000)).encode()).hexdigest(),
#             "name": 'Big Biz Inc',
#             "latitude": 1.001,
#             "longitude": 1.002,
#             "postalcode": 1234,
#             "numreviews": 9,
#             "stars": 3.4,
#             "isopen": 0,
#             "attributes": 'some number of attributes, maybe a comma',
#             "categories": 'some number of categories, maybe a comma',
#             },
#             {
#             "business_id": hashlib.sha256(str(np.random.randint(0, 100000)).encode()).hexdigest(),
#             "name": 'Big Biz Competitor Inc',
#             "latitude": 1.004,
#             "longitude": 1.006,
#             "postalcode": 9999,
#             "numreviews": 2,
#             "stars": 3.8,
#             "isopen": 1,
#             "attributes": 'some number of attributes, maybe a comma',
#             "categories": 'some number of categories, maybe a comma',
#             }

#         ]
#     }
#     return test_data

## Build post request
# request = requests.post(url='http://localhost:5000/api/data/', json=generate_test_data())
# try:
#     print(request)
# except:
#     print('Test 1 Failed')
#     raise

# ## Test 2: Testing rapid requests
# # Currently failing rapid simultaneous requests.
# for i in range(3):
#     time.sleep(1)
#     request = requests.post(url='http://localhost:5000/api/data/', json=generate_test_data())
#     print(request, ' ', i)

# TEST 3: Load sample_users.json and attempt time writing to db.

# # Users
# df = pd.read_parquet('sample_users.parquet')
# package = df_to_query(df=df, tablename='users')

# # Build databunch for more smaller requests
# databunch = build_databunch(package, max_size=1000)

# for bunch in databunch:
#     batch_size = len(bunch['data'])
#     start = time.time()
#     request2 = requests.post(url='https://db-api-yelp18-staging.herokuapp.com/api/data', json=bunch)
#     print(request2)
#     stop = time.time()
#     print('Batch of {} processed in {}'.format(batch_size, stop-start))


# # Tips
# df = pd.read_parquet('sample_tips.parquet')
# df['tip_id'] = df.apply(generate_id, axis=1)
# package = df_to_query(df=df, tablename='tips')
# batch_size = len(package['data'])

# # Build databunch for more smaller requests
# databunch = build_databunch(package, max_size=100)

# start = time.time()

# parallel_post_requests(
#     databunch=databunch,
#     url='https://db-api-yelp18-staging.herokuapp.com/api/data',
#     max_requests=20
#     )

# stop = time.time()
# print('Batch of {} processed in {}'.format(batch_size, stop-start))


# # Checkins
# df = pd.read_parquet('sample_checkins.parquet')
# df['checkin_id'] = df.apply(generate_id, axis=1)
# df = df.rename(columns={'date':'dates'})
# package = df_to_query(df=df, tablename='checkins')
# batch_size = len(package['data'])

# # Build databunch for more smaller requests
# databunch = build_databunch(package, max_size=200)

# start = time.time()

# parallel_post_requests(
#     databunch=databunch,
#     url='https://db-api-yelp18-staging.herokuapp.com/api/data',
#     max_requests=20
#     )

# stop = time.time()
# print('Batch of {} processed in {}'.format(batch_size, stop-start))

# # Reviews
# df = pd.read_parquet('sample_reviews.parquet')
# package = df_to_query(df=df, tablename='reviews')
# batch_size = len(package['data'])

# # Build databunch for more smaller requests
# databunch = build_databunch(package, max_size=200)

# start = time.time()

# parallel_post_requests(
#     databunch=databunch,
#     url='https://db-api-yelp18-staging.herokuapp.com/api/data',
#     max_requests=10
#     )

# stop = time.time()
# print('Batch of {} processed in {}'.format(batch_size, stop-start))


# # Photos
# df = pd.read_parquet('sample_photos.parquet')
# package = df_to_query(df=df.head(15), tablename='photos')
# batch_size = len(package['data'])

# # Build databunch for more smaller requests
# databunch = build_databunch(package, max_size=200)

# start = time.time()

# parallel_post_requests(
#     databunch=databunch,
#     url='https://db-api-yelp18-staging.herokuapp.com/api/data',
#     max_requests=15
#     )

# stop = time.time()
# print('Batch of {} processed in {}'.format(batch_size, stop-start))

# TEST 4 GET Requests
url='https://db-api-yelp18-staging.herokuapp.com/api/data'

# 4.A data_viz get request
package = {
    'schema': 'biz_words',
    'params': {
        'business_id': 'ajoqEHnCZTD8-8GqGLq9-Q'
        },
}
response = requests.get(url=url, json=package)
print('Status: ', response.status_code)
print('Content: ', response.text)