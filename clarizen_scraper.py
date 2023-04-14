"""
"""
import ast
import csv
import json
import os
import pdb
import time
from concurrent.futures import ThreadPoolExecutor

import urllib.request
import requests
from bs4 import BeautifulSoup

import task_constants
from clarizen_client import ClarizenClient


def download_files(c_client, task_ident_list, download_folder):
    """Try to download all files
    """
    download_list = []
    errored_task_ids = []
    task_counter = 0
    for task_ident in task_ident_list:

        task_id = task_ident.split('.')[1]

        try:
            is_approved = c_client.is_task_approved(task_id)

            relative_path = f'{download_folder}/{task_id}'
            if not is_approved:
                relative_path = f'{download_folder}/NOT-APPROVED-NO-DOWNLOAD-{task_id}'

            # make folder
            absolute_path = os.path.dirname(__file__)
            folder = os.path.join(absolute_path, relative_path)
            if not os.path.exists(folder):
                os.makedirs(folder)

            # download files if approved
            print()
            if is_approved:
                print(f'Processing files for approved task: {task_id}')
                task_files_info_list = c_client.fetch_files_list(task_ident)
                for file_info in task_files_info_list:
                    file_name = file_info['file_name']
                    doc_id = file_info['doc_id']

                    print('-- fetching files')

                    if os.path.exists(f'{folder}/{file_name}'):
                        print(f' -- file exists: skipping - {folder}/{file_name}')
                    else:
                        download_list.append({
                            'doc_id': doc_id,
                            'file_name': file_name,
                            'folder': folder,
                        })
            else:
                print(f'Skipping unapproved task: {task_id}')

            if len(download_list) >= 8:
                c_client.run_downloads(download_list)
                download_list = []
        except Exception as e:
            print(f'Exception: {str(e)}')
            errored_task_ids.append(task_id)
        task_counter += 1

        # login periodically
        if task_counter % 300 == 0:
            c_client.login()

    c_client.run_downloads(download_list)
    download_list = []

    print(f'**** Errored task ids: {errored_task_ids}')


def audit_tasks_with_file(c_client, task_ident_list):
    """Audit tasks via Clarizen and print out csv file

    For each task:
    * Mark if approved
    * If approved, get file list and check if in downloads folder
    * If in downloads folder, get md5 sum
    * If approved files missing, mark as missing

    list of dicts with task and file info
    [{
        'task_id': task_id,
        'file_name': file_name,
        'doc_id': doc_id
    }]
    """
    checked_files = {}
    audit_fname = 'audit_output_file.csv'
    audit_fields = ['is_approved', 'task_ident', 'task_id', 'file_name', 'doc_id']

    with open(audit_fname, 'r+') as fp:

        reader = csv.DictReader(fp, fieldnames=audit_fields)
        last_task_id = ''
        for row in reader:
            last_task_id = row['task_id']
            checked_files[last_task_id] = True
        # Remove last record from dictionary because there may have been an exception going half way through the task
        checked_files.pop(last_task_id)

    print(f'num_tasks already done: {len(checked_files)}')

    with open(audit_fname, 'a+') as fp:
        writer = csv.DictWriter(fp, fieldnames=audit_fields)
        if not checked_files:
            writer.writeheader()

        task_counter = 1
        for task_ident in task_ident_list:
            task_id = task_ident.split('.')[1]

            if task_id not in checked_files:
                task_files_info_list = c_client.fetch_files_list(task_ident)
                is_approved = c_client.is_task_approved(task_id)

                for file_info in task_files_info_list:
                    file_name = file_info['file_name']
                    doc_id = file_info['doc_id']
                    writer.writerow({
                        'is_approved': str(is_approved),
                        'task_ident': task_ident,
                        'task_id': task_id,
                        'file_name': file_name,
                        'doc_id': doc_id
                    })

                # login periodically
                if task_counter % 500 == 0:
                    c_client.login()
            task_counter += 1


def get_ids_to_idents(task_idents):
    """Turn list of task idents into map of ids to idents

    idents have ids in the middle
    """
    ids_to_idents = {}
    for ident in task_idents:
        tid = ident.split('.')[1]
        ids_to_idents[tid] = ident
    return ids_to_idents


def run_main():
    """
    TODO

    ---- ONLY 1 file dl'd ----
    Processing files for approved task: 12964106305
    -- num docs: 2
    -- fetching files
    -- fetching files
    approved? True
    """

    print('-------------------------')
    print('~marketing scraper start~')
    print('-------------------------')

    # setup the download folder
    absolute_path = os.path.dirname(__file__)
    relative_path = "downloads-new"
    folder = os.path.join(absolute_path, relative_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    task_ident_list = []
    with open('task_idents.txt', 'r') as fp:
        idents_str = fp.read()
        task_ident_list = ast.literal_eval(idents_str)

    c_client = ClarizenClient()
    c_client.login()

    # download_files(c_client, task_ident_list, relative_path)
    audit_tasks_with_file(c_client, task_ident_list)


if __name__ == '__main__':
    run_main()


