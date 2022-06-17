import boto3
import logging
import json
import os



def assume_role(account_id, role_name):

    try:
        sts_client = boto3.client('sts')
        role_arn = ("arn:aws:iam::%s:role/%s" % (account_id, role_name))
        assumedRoleObject = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=("AssumedRoleSession-%s"%role_name))
        credentials = assumedRoleObject['Credentials']
        return credentials
    except Exception:
        logging.exception(('STS Failure on assuming role %s@%s'%(role_name,account_id)))
        return

# Lambda entry point ...
def lambda_handler(event, context):
    # dump the event to the log
    logging.debug("Received event: " + json.dumps(event, indent=2))

    # Master account Id - wondering if this should be another environment variable
    master_account_id=event['master_account_id']
    
    # Assume the master account admin role credentials
    # FIXME - make this a more restricted role
    credentials=assume_role(master_account_id, 'admin')

    # Get the client to parse the organizations
    organizations_client=boto3.client('organizations',
                                      aws_access_key_id = credentials['AccessKeyId'],
                                      aws_secret_access_key = credentials['SecretAccessKey'],
                                      aws_session_token = credentials['SessionToken'])
                                      
    # Get the accounts from the organizations
    accounts=organizations_client.list_accounts()
    # print(accounts)

    # Thinking this should also be a parameter or environment variable for flexibility
    regions = ['us-west-2','us-west-1','us-east-2','us-east-1','eu-central-1','eu-west-1']

    count=0
    
    # Get a paginator for the accouints
    paginator = organizations_client.get_paginator('list_accounts')
    
    # Iterator for th paginator
    page_iterator = paginator.paginate()
    
    # Print out Headings
    print('%s,%s,%s'%('Account','Region','BucketName'))

    # Loop through the pages
    for region in regions:  
        print (region)
        for page in page_iterator:
        # Get the accounts in this page
            accounts = page['Accounts']
        
        # Loop through the accounts in the page
            for account in accounts:
                if( account['Status'] == 'SUSPENDED'):
                    # Skip suspended accounts
                    continue
                if( account['Id'] == '' or account['Id'] == '' or account['Id'] == ''):
                  continue
                credentials=assume_role(account['Id'], 'admin')
            
            # verify we were allowed to assume the role
                if credentials == None:
                    logging.warning('Skipping account %s. Access roles not set properly!'%(account['Id']))
                    continue
        
                s3_client=boto3.client(    's3',
                                        region_name = region,
                                        aws_access_key_id = credentials['AccessKeyId'],
                                        aws_secret_access_key = credentials['SecretAccessKey'],
                                        aws_session_token = credentials['SessionToken'])

                try:
                    buckets = s3_client.list_buckets()['Buckets'];
                    count=count+1
                    for bucket in buckets:
                        print('%s,%s,%s'%(account['Name'],region,bucket['Name']))
                except Exception:
                    print("%s,%s,-,-,-,-,-,-,-,-,-,-"%(account['Name'],region))


    print("count:%s"%(count))
    return event;

def get_value(map, key):
    if( key in map ):
        return map[key];
    else:
        return '-';
