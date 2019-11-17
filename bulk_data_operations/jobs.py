"""
Jobs Library
    Read in jobs, Fetch Job Assets, Delete Jobs
"""
import s3
import json
import os


class g():
    def __init__(self, bucket=None, job_list=None):
        self.bucket=bucket
        self.job_list = job_list

g = g()


##########################
###s3 Control Functions###
##########################

def get_bucket():
    if g.bucket == None:
        bucket = s3.Bucket('yelp-data-shared-labs18')
        g.bucket = bucket
        return g.bucket
    return g.bucket

def download_data(object_path, save_path='/tmp/'):
    bucket = get_bucket()
    save_path = save_path + object_path.split('/')[-1]
    bucket.get(object_path, save_path)
    return save_path



###########################
###Job Control Functions###
###########################


def get_jobs(job_type='post'):
    bucket = get_bucket()
    if g.job_list == None:
        jobs = []
        for job in bucket.find('Jobs/', suffix='json'):
            if job_type in job.lower():
                jobs.append(job)
        g.job_list = jobs
        return g.job_list
    return g.job_list


def pop_current_job():
    """Pop job from list"""
    jobs = get_jobs()
    job_name = jobs.pop()
    return job_name


def read_job(job):
    temp = download_data(job)
    print(temp)
    with open(temp) as jobfile:
        response = json.load(jobfile)
    delete_local_file(temp)
    return response


def delete_s3_file(filepath):
    bucket = get_bucket()
    return bucket.delete_object(filepath)


def delete_local_file(filepath):
    os.remove(filepath)


if __name__ == "__main__":
    for i in range(2):
        current_job = pop_current_job()
        asset = read_job(current_job)['Key']
