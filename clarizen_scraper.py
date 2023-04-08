"""
"""
import pdb
import os
import time
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import urllib.request
import requests
from bs4 import BeautifulSoup

import task_constants
from clarizen_client import ClarizenClient


def login_and_get_cookies():

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome(options=chrome_options)

    login_url = "https://app2.clarizen.com/Clarizen/Pages/Service/Login.aspx"
    # The user credentials
    username = os.environ["CLARIZEN_USERNAME"]
    password = os.environ["CLARIZEN_PASSWORD"]

    # Navigate to the login page
    browser.get(login_url)

    # Find the username and password input fields
    username_field = browser.find_element(By.NAME, "txtLogin")
    password_field = browser.find_element(By.NAME, "txtPassword")

    # Set the values of the input fields to the user credentials
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Submit the login form
    password_field.send_keys(Keys.RETURN)

    # Wait for the login to complete
    time.sleep(2)

    # Check if the login was successful
    all_cookies = {}
    if "Partner Home Marketing" in browser.page_source:
        clist = browser.get_cookies()
        for cdict in clist:
            all_cookies[cdict['name']] = cdict['value']
    return all_cookies


def download_files(c_client, task_ident_list, download_folder):
    """Try to download all files
    """
    download_list = []
    errored_task_ids = []
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

    c_client.run_downloads(download_list)
    download_list = []

    print(f'**** Errored task ids: {errored_task_ids}')


def audit_tasks(c_client, task_ident_list):
    """Audit tasks via Clarizen

    For each task:
    * Mark if approved
    * If approved, get file list and check if in downloads folder
    * If in downloads folder, get md5 sum
    * If approved files missing, mark as missing
    """
    audit_json = {}




    return audit_json


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

    print('Trying to login')
    all_cookies = login_and_get_cookies()
    if not all_cookies:
        print('No cookies returned. Login probably failed')
        return
    else:
        print('Got cookies. Login successful...probably')
    c_client = ClarizenClient(cookies=all_cookies)

    # task_ident_list = sorted(task_constants.ALL_TASKS)
    ids_to_idents = get_ids_to_idents(task_constants.ALL_TASKS)
    task_ident_list = [ids_to_idents[tid] for tid in task_constants.ERRORED_IDS]

    download_files(c_client, task_ident_list, relative_path)
    # audit_json = audit_tasks(c_client, task_ident_list)


if __name__ == '__main__':
    run_main()


