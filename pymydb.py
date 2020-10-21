#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Jason Brown'
__email__  = 'jason@jasonbrown.us'
__date__   = '20201019'

import MySQLdb, boto3, json
from subprocess import call
from time import strftime

def main():
    logtime = strftime("%Y%m%d")
    database = []

    '''Connection to AWS Secrets Manager'''
    secret_name = ''
    region_name = ''

    client = boto3.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response['SecretString'])

    '''Connect to the MySQL database'''
    try:
        conn = MySQLdb.connect (host = secret['hostname'],
                                user = secret['username'],
                                passwd = secret['password'])
        cursor = conn.cursor()
    except:
        print("Cannot connect to database")
        return 0
    
    '''Iterate through all the databases in the MySQL server'''
    cursor.execute("SHOW DATABASES;")
    row = cursor.fetchall()
    for i in row:
        database.append('%s' % (i))
    cursor.close()
   
    for j in database:
        '''Ignore databases we do not care about and dump the remaining
           Place SQL backups in a backup directory
        '''
        if j == "information_schema" or j == "performance_schema" or j == "mysql":
            continue
        call('/usr/bin/mysqldump -u%s -p%s -h%s %s > backup/%s-%s.sql' % (secret['username'], secret['password'], secret['hostname'], j, j, logtime), shell=True)
    
def upload():

    s3 = boto3.client('s3')

    with open('', 'rb') as data:
        s3.upload_fileobj(data, '', '')
    
if __name__ == '__main__':
    main()
    upload()