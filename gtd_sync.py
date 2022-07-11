#!/usr/bin/env python3
# 	1. 功能
# 		gtd的多终端数据同步
#
# 	2. 步骤
# 		check remote version
# 			pull
# 		check local version
# 			push
#
#	3. 补充说明
# 		1. 唯一标识符: 时间戳
# 		2. 直接覆盖, 时间戳更大的, 有一票否决权/至高权力
#
import requests
import json
import os
import datetime
import filecmp
import shutil
try:
	from qcloud_cos import CosConfig
	from qcloud_cos import CosS3Client
except:
	from qcloud_cos_v5 import CosConfig
	from qcloud_cos_v5 import CosS3Client
import re

secret_id = 'AKIDb3UjhOpZ3GCsHPGqBG4bsugCSSAblfId'
secret_key = '5vTkkUx83g39xUllUw83g27wUll0zh8I'
region = 'na-siliconvalley'
bucket = 'cos-1259633509'

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)

isExist = lambda path: client.object_exists(Bucket=bucket, Key=path)
listFile = lambda path: [x['Key'] for x in client.list_objects(Bucket=bucket, Prefix=path + '/', Delimiter="/").get('Contents', [])[1:]]

remotePath='sync/content.md'
localPath='content.md'

# -------------------------------- common functions --------------------------------


def upload(src, dst):
	for i in range(0, 10):
		try:
			response = client.upload_file(Bucket=bucket, Key=dst, LocalFilePath=src)
			break
		except CosClientError or CosServiceError as e:
			print(e)


def download(src, dst):
	for i in range(0, 10):
		try:
			response = client.download_file(Bucket=bucket, Key=src, DestFilePath=dst)
			break
		except CosClientError or CosServiceError as e:
			print(e)


def getRemoteTimestamp(path):
	response = client.head_object(Bucket=bucket, Key=path)
	s=response.get('Last-Modified')
	return int(datetime.datetime.strptime(s, "%a, %d %b %Y %H:%M:%S GMT").timestamp())

def getLocalTimestamp(path):
	return int(datetime.datetime.fromtimestamp(os.path.getmtime(path)).timestamp())-8*3600


# -------------------------------- Run --------------------------------

if __name__ == "__main__":
	remoteTimestamp=getRemoteTimestamp(remotePath)
	localTimestamp=getLocalTimestamp('content.md')
	if remoteTimestamp>localTimestamp:
		download(remotePath, '_content.md')
		if not filecmp.cmp('content.md', '_content.md'):
			shutil.copy('_content.md', 'content.md')
			print('pull')
		os.remove('_content.md')
	else:
		download(remotePath, '_content.md')
		if not filecmp.cmp('content.md', '_content.md'):
			upload(localPath, remotePath)
			print('upload')
		os.remove('_content.md')
