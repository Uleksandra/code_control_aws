
import boto3
import os
import pandas
from traceback import print_exc

#Крок1
#Створення ключовоъ пари

def create_key_pair():
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    key_pair = ec2_client.create_key_pair(KeyName="test_key_pair3")
    private_key = key_pair["KeyMaterial"]
    with os.fdopen(os.open("tmp/aws_ec2_key.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(private_key)
    print('Key pair was successfully created')
#Крок2
#створення EC2 інстансу засобами boto3
def create_instance():
    name_instances = str(input("Please enter name for your new EC2: "))
    try:
        ec2_client = boto3.client("ec2", region_name="eu-north-1")
        instances = ec2_client.run_instances(
            ImageId="ami-01a7573bb17a45f12",
            MinCount=1,
            MaxCount=1,
            InstanceType="t3.micro",
            KeyName="test_key_pair3",
                TagSpecifications=[
                    {
                        "ResourceType":"instance",
                        "Tags":[
                            {
                                "Key": "Name",
                                "Value": f"{name_instances}"
                            }
                        ]
                    }
                ]
        )
        print(f'\nInstans was succesfully created with name:{name_instances}')
        print(f'InstansID is: {instances["Instances"][0]["InstanceId"]}')
    except:
        print("Name is`t correct")

#Крок3
# Cписок активних інстансів

def get_running_instances():
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running"],
        }
    ]).get("Reservations")
    for reservation in reservations: 
        try:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                instance_type = instance["InstanceType"]
                try:
                    public_ip = instance["PublicIpAddress"]
                    private_ip = instance["PrivateIpAddress"]
                except:
                    public_ip, private_ip = '-', '-'
                print(f"{instance_id}, {instance_type}, {public_ip},{private_ip}")
        except:
            continue



#Отримання IP інстансу

def get_public_ip():
    instance_id = str(input("Please enter InstansID: "))
    ec2_client = boto3.client("ec2", region_name="eu-north-1")

    try:
        reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
        for reservation in reservations:
            for instance in reservation['Instances']:
                print(instance.get("PublicIpAddress"))
    except:
        print(f'{instance_id} is not correct')

#Крок4
#Зупинка/старт інстансу

def stop_instance():
    instance_id = str(input("Please enter InstansID: "))
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        print('Instance was successfully stopped')
    except:
        if instance_id not in create_list_instances():
            print(f'{instance_id} is not in your instances list. Maybe you write incorrect ID. Try again')
        elif write_status(instance_id) == "stopped":
            print(f'{instance_id} is stopped yet')
        elif write_status(instance_id) == "terminated":
            print(f'{instance_id} is terminated yet')
    print(response)
    
def start_instance():
    instance_id = str(input("Please enter InstansID: "))
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        print('Instance was successfully started')
    except:
        if instance_id not in create_list_instances():
            print(f'{instance_id} is not in your instances list. Maybe you write incorrect ID. Try again')
        elif write_status(instance_id) == "Running":
            print(f'{instance_id} is running yet')        
        elif write_status(instance_id) == "terminated":
            print(f'{instance_id} is terminated yet')
    print(response)

#Виведення статусу інстансу

def write_status(ID):
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-id",
            "Values": [ID],
        }
    ]).get("Reservations")
    for reservation in reservations: 
        try:
            for instance in reservation["Instances"]:
                instance_status = instance["State"]["Name"]
        except:
            print(f'{ID} was not found')
        return instance_status
    
#Видалення інстансу

def terminate_instance():
    instance_id = str(input("Please enter InstansID: "))
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    try:
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        print(response)
        print('Instance was successfully terminated')
    except:
        if instance_id not in create_list_instances():
            print(f'{instance_id} is not in your instances list. Maybe you write incorrect ID. Try again')
        elif write_status(instance_id) == "terminated":
            print(f'{instance_id} was terminated yet')
        

#Створимо список всіх інстансів для регулювання помилок для інших команд

def create_list_instances():
    instance_list = []
    ec2_client = boto3.client("ec2", region_name="eu-north-1")
    reservations = ec2_client.describe_instances(Filters=[
    ]).get("Reservations")
    for reservation in reservations: 
        try:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                instance_list.append(instance_id)
        except:
            continue    
    return instance_list

# Бакет
# Створеннябакету
def create_bucket():
    bucket_name = str(input("Please enter Bucket name: "))
    s3_client = boto3.client('s3', region_name="eu-north-1")
    location = {'LocationConstraint': "eu-north-1"}
    try:
        response = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print(response)
        print(f'Bucket {bucket_name} was successfully created')
    except:
        print(f'{bucket_name} is already exist. Try another name please 🤷‍♀️')

# Крок 2 – лістинг існуючих бакетів облікового запису

def buckets_list():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    list_all_buckets = []
    for bucket in response['Buckets']:
        list_all_buckets.append(bucket["Name"])
        # print(f' {bucket["Name"]}')
    return list_all_buckets

def write_list():
    my_list = buckets_list()
    print('Existing buckets:')
    for i in my_list:
        print(f'Bucket:         {i}')

#Крок 3 – завантаження файлу
def upload():
    bucket_name = str(input("Please enter Bucket name: "))
    if bucket_name not in buckets_list():
        print(f'{bucket_name} is not already exist')
    try:
        file_name = str(input("Please enter File name: "))
        s3_obj_name = file_name
        s3_client = boto3.client('s3')
        responce = s3_client.upload_file(Filename=file_name, Bucket=bucket_name, Key=s3_obj_name)
        print(f'File {file_name} was successfully uploaded')
    except:
        print_exc()
        # print(f'File {file_name} is not exist')

# Крок 4– читання даних з s3
def files_list(bucket_name):
    #bucket_name = str(input("Please enter Bucket name: "))
    if bucket_name not in buckets_list():
        print(f'{bucket_name} is not already exist')
    else:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        files = []
        for obj in bucket.objects.all():
            files.append(obj.key)
        return files

# завантаження файлу з бакету
def download_file():
    files = []
    bucket_name = str(input("Enter bucket name: "))
    if bucket_name not in buckets_list():
        return print(f'{bucket_name} is not already exist')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    files = files_list(bucket_name)
    s3_file_path = str(input("Enter file name: "))
    if s3_file_path not in files:
        print(f"File {s3_file_path} is not exist in bucket {bucket_name}")
    bucket.download_file(s3_file_path, s3_file_path)
    print(f"File {s3_file_path} was successfully downloaded")

# Видалення файлу з бакету

def delete_file():
    bucket_name = str(input("Enter bucket name: "))
    if bucket_name not in buckets_list():
        return print(f'{bucket_name} is not already exist')
    files = files_list(bucket_name)
    s3_file_path = str(input("Enter file name: "))
    if s3_file_path not in files:
        print(f"File {s3_file_path} is not exist in bucket {bucket_name}")
        return
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    object = bucket.Object(s3_file_path)
    object.delete()
    print(f"File {s3_file_path} was successfully deleted")

# Видалення бакету

def destroy_bucket():
    bucket_name = str(input("Please enter Bucket name: "))
    s3_client = boto3.client('s3')
    if bucket_name not in buckets_list():
        print(f'{bucket_name} is not already exist')
    else:
        response = s3_client.delete_bucket(Bucket=bucket_name)
        print(f'{bucket_name} was successfulle destroy')
    

# Menu

def menu():
    while True:
        try:
            request = int(input("""
Write 1 or 2 to make your choise
[1] Control EC2
[2] Control S3
[0] Exit
"""))
            if request == 1:
                while True:
                    try:
                        command = int(input("""
Write number 0-9 to make your choise
[1] Create instance
[2] Create key pair
[3] Get list running instances
[4] Get instance public IP
[5] Start instance
[6] Stop instance
[7] Terminate instance
[8] Get status instance
[9] Get list all instances
[0] Return
"""))
                        if command == 0: break
                        elif command == 1: create_instance()
                        elif command == 2: create_key_pair()
                        elif command == 3: get_running_instances()
                        elif command == 4: get_public_ip()
                        elif command == 5: start_instance()
                        elif command == 6: stop_instance()
                        elif command == 8:
                            get_id = str(input("Please enter InstansID: ")) 
                            print(write_status(get_id))
                        elif command == 7: terminate_instance()
                        elif command == 9: print(create_list_instances())
                        else: print("Command not found")
                    except:
                        print("Command not found")
            elif request == 2:
                while True:
                    try:
                        command = int(input("""
Write number 0-9 to make your choise
[1] Create Bucket
[2] Get Buckets list
[3] Unload file
[4] Get file list
[5] Download file
[6] Delete file
[7] Destroy bucket
[0] Return

"""))
                        if command == 0: break
                        elif command == 1: create_bucket()
                        elif command == 2: write_list()
                        elif command == 3: upload()
                        elif command == 4:
                            bucket_name = str(input("Please enter Bucket name: "))
                            print(files_list(bucket_name))
                        elif command == 5: download_file()
                        elif command == 6: delete_file()
                        elif command == 7: destroy_bucket()
                        else: print("Command not found")
                    except:
                        print("Problem with command")
            elif request == 0: break
            else: print("Command not found")
        except:
            print("Command not found")    

menu()    