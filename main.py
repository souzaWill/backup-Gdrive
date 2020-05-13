#!/usr/bin/env python3

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, time, glob, shutil, sys

def delete_all_on_cloud(Gdrive):
    """ delete all files in cloud storage """
    uploaded_file_list = Gdrive.ListFile({'q': "'root' in parents"}).GetList()
    for f in uploaded_file_list:
        print('[ Delete ] >> ', f['title'])
        f.Delete()
        time.sleep(3)
def upload_file(Gdrive, file,folder_id):
    """ upload file with same archive name on cloud"""
    print('[ Upload ] >> ', os.path.abspath(file))
    file1 = Gdrive.CreateFile({'title': os.path.basename(file), "parents": [{"kind": "drive#fileLink","id": folder_id}]})
    file1.SetContentFile(file)
    file1.Upload()
def having(file_local, files_cloud):
    """ compare local files and files on cloud and return true case find files in both """
    for file_cloud in files_cloud:
        if file_cloud['title'] == os.path.basename(file_local):
            return True
    return False
def auth():
    """ authenticate on Gdrive with client_secrets.json need settings.yaml file to get credentials"""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    Gdrive = GoogleDrive(gauth)
    return Gdrive
def get_all_files_local(path):
    """ return files[] content all files on directories recursively """

    files = [f for f in glob.glob(path + "**/*.*", recursive=True)]
    return files
def move_to_processed(file):
    """ move file o processed directoy  """
    # define the directory of destine replacing the folder "storage" to "processed"
    dest = file.replace(os.path.basename(file), '')
    dest = dest.replace("storage", "processed")

    # make directory if dont exists   
    if os.path.isdir(dest) == False:
        os.makedirs(dest)

    #move file to destine
    print('[ Moving File ] >> ', dest)
    shutil.move(os.path.abspath(file), dest)


def get_id_folder(Gdrive):
    root_files = Gdrive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for files in root_files:
        if files['title'] == 'photos' :
            return files['id']

def main(argv):
    # path = '/home/will/python-dev/teste/storage/'
    path = argv

    Gdrive = auth()

    id_folder = get_id_folder(Gdrive)

    local_files = get_all_files_local(path)
    cloud_files = Gdrive.ListFile({'q': "'"+str(id_folder)+"' in parents and trashed=false"}).GetList()

    # delete_all_on_cloud(Gdrive)

    count = 0

    for file in local_files:
        if having(file, cloud_files) != True:
            print('[ New File ] >> ', file)
            upload_file(Gdrive, file,id_folder)
            move_to_processed(file)
            time.sleep(2)
            os.system('clear')
            count += 1

    if len(local_files) != count:
        print("Something is Wrong!!!",len(local_files), count)
    else:
        print('all files as uploaded!!')

if __name__ == "__main__":
    main(sys.argv[1])