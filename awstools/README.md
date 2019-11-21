# data-engineering
ETL and Managmenet Scripts.  Does not contain full raw data.


## Useful AWS Commands

**AWS Workflow Notes** on the way.  Pared down datasets for testing and exploration can be found in the sample_data folder.

### Sync Folders with S3 Bucket

**Note** You must have aws cli installed and have logged into your user or IAM with access to the bucket for the following to work.

```Bash
aws s3 sync <source> <destination>
```

> Example: aws s3 sync yelp_json s3://yelp-data-shared-labs18/yelp_json


### AWS Tools Library

import os
from awstools import s3

# Setup AWS credentials and create local credential files.
s3.setup_aws()

> Function generates a '.aws' directory with credential files in it.  Credentials are not encrypted, so do not commmit that directory.

# Initialize bucket
bucket = s3.Bucket('yelp-data-shared-labs18')

# Test download of file
bucket.get(object_name, save_name)

**Example:** Download 'test.txt' and save to 'text.txt'

> bucket.get('test.txt', 'text.txt')

**Example:** Download binary type to memory and use directly

download = bucket.get('sample_data/tip.parquet')
import pandas as pd
!pip install pyarrow
pd.read_parquet(download).head()

# Test upload (saving)
test_path = os.path.join(os.getcwd(), 'text.txt')
bucket.save(test_path, 'upload_test.txt')

### Install miniconda and setup environment

1. Download miniconda

> curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

2. Install miniconda

> bash Miniconda3-latest-Linux-x86_64.sh

3. Update anaconda

> conda update -n base -c defaults conda

4. Clone this repository.

> git clone https://github.com/Lambda-School-Labs/yelp-dataset-challenge-2-ds.git

5. Setup environment

> conda env create -f <filename>
