#!/root/apkenv/bin/python3
import argparse
import boto3
from boto3.s3.transfer import S3Transfer
import os
import sys
import oss2
import time

def get_s3_resource(ACCESS_KEY,SECRET_KEY,region):
    session=boto3.Session(
    region_name=region,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)
    resource=session.resource('s3')
    return resource

def get_s3_clinet(ACCESS_KEY,SECRET_KEY,region):
    client = boto3.client(
    's3',
    region_name=region,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY)
    return client

def check_file(file):
    if os.path.exists(file):
        file_name=os.path.basename(file)
        return file_name
    else:
        return False

def s3_copy_file(resurce,bucket,key):
    copy_source = {
        'Bucket': bucket,
        'Key': key
    }
    resurce.meta.client.copy(copy_source, bucket, key+"_"+time.strftime("%Y-%m-%d", time.localtime()))

def cmd_s3(args):
    s3_client=get_s3_clinet(ACCESS_KEY=args.id,SECRET_KEY=args.key,region=args.region)
    s3_resource=get_s3_resource(ACCESS_KEY=args.id,SECRET_KEY=args.key,region=args.region)
    transfer = S3Transfer(s3_client)
    file_name=check_file(args.file)
    if args.folder=="":
        dir=file_name
    else:
        dir=args.folder+'/'+file_name
    if file_name:
        if args.back:
            try:
                s3_copy_file(resurce=s3_resource,bucket=args.bucket,key=dir)
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- backup %s in S3 success" % file_name)
            except Exception as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- backup %s error in S3 for %s" % (file_name,e))
                pass
        try:
            transfer.upload_file(args.file, args.bucket, key=dir)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- upload %s to S3 success"% file_name)
        except Exception as e:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- upload %s to S3 error: %s" %(file_name,e))
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- no %s in your local dir"%(file_name))

def cmd_oss(args):
    auth = oss2.Auth(access_key_id=args.id,access_key_secret=args.key)
    bucket = oss2.Bucket(auth, "https://oss-"+args.region+".aliyuncs.com", args.bucket)
    file_name = check_file(args.file)
    if args.folder == "":
        dir = file_name
    else:
        dir = args.folder + '/' + file_name
    if file_name:
        if args.back:
            try:
                res=bucket.copy_object(source_bucket_name=args.bucket,source_key=dir,target_key=dir+"_"+time.strftime("%Y-%m-%d", time.localtime()))
                if res.status==200:
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- backup %s in oss success" % file_name)
            except oss2.exceptions.NoSuchKey as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), " -- backup %s error in oss for %s" % (file_name,e))
        try:
            res=bucket.put_object_from_file(dir, args.file)
            if res.status==200:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- upload %s to oss success" % file_name)
            else:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- upload %s to oss false" % file_name)
        except Exception as e:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())," -- upload %s to oss error: %s" % (file_name,e))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='update apk and back apk')
    parser.add_argument('-m',choices= ['oss','s3'],default='s3',help="choice s3 or oss default s3")
    parser.add_argument('-k','--key',help="access_key_secrets")
    parser.add_argument('-u','--id',help="access_key_id")
    parser.add_argument('-b','--bucket',help="bucket name")
    parser.add_argument('-f','--file',help="file name")
    parser.add_argument('--folder',help="which folder in bucket",default="")
    parser.add_argument('--back',help="backup your file in S3 or oss",action="store_true")
    parser.add_argument('--region',help="the bucket region")
    args = parser.parse_args()
    if len(sys.argv)==1:
        parser.print_usage()
        exit(1)
    if args.m=="s3":
        cmd_s3(args)
    if args.m=="oss":
        cmd_oss(args)
