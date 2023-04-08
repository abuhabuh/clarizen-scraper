import os
import time
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import urllib.request
import requests
from bs4 import BeautifulSoup

import http_constants


class ClarizenClient:

    def __init__(self):
        return

    def login(self):
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

        if not all_cookies:
            raise Exception('ClarizenClient - no cookies. Login probably failed')
        else:
            print('Got cookies. Login successful.')

        self._cookies = all_cookies

    def get_params(self):
        return {
            '__aftoken': 'JDewBrUbREO0q4mZWr3Xfw',
        }

    def is_task_approved(self, task_id):
        task_url = f'https://app2.clarizen.com/Clarizen/Task/{task_id}'
        response = requests.get(
            task_url,
            params=self.get_params(),
            cookies=self._cookies,
            headers=http_constants.headers,
            data={}
        )
        soup = BeautifulSoup(response.text, "html.parser")
        info_table = soup.body.div.nextSibling.div.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.nextSibling.div.div.div.div.div.nextSibling.div.div.div.nextSibling.div.table

        approval_str = info_table.find_all('tr')[4].find_all('td')[-1].text

        approved = approval_str == 'Phase 4(a) Approved'
        print('approved? ' + str(approved))
        return approved


    def fetch_file(self, info_dict):
        # https://app2.clarizen.com/Clarizen/Pages/FileHandling/OpenDocument.aspx?po=34.570811649.24350977
        document_id = info_dict['doc_id']
        file_name = info_dict['file_name']
        folder = info_dict['folder']

        response = requests.get(
            f'https://app2.clarizen.com/Clarizen/Pages/FileHandling/OpenDocument.aspx?po={document_id}',
            params=self.get_params(),
            cookies=self._cookies,
            headers=http_constants.headers,
            data={}
        )

        open(f'{folder}/{file_name}', 'wb').write(response.content)


    def fetch_files_list(self, task_ident):
        # session specific cookies
        data = {
        'request': '{"htmlBuilder":"ExtendedRelation","htmlBuilderState":{"Id":"extended-relation-popup-ATTDOCS","DataProvider":"ObjectRelations","Action":"SingleRelation","ContextId":"TS.GenericTask.ObjectRelations.ATTDOCS","LocalContextId":"TS.GenericTask.ObjectRelations.ATTDOCS.ExtendedRelation","NotifyTo":"Collaboration_ObjectRelations_RelationController_ATTDOCS","NotifyAction":"refresh","ExternalParams":["selectedIdentifiers"],"ExpandedMode":true},"parameters":{"selectedIdentifiers":["' + task_ident + '"],"relationName":"ATTDOCS","viewMode":2,"pageNumber":1,"viewId":"354.11997121.0","addRibbonData":true,"isMaximized":true},"internalContextParams":["relationName","pageNumber","viewMode","filtersInfo","sortInfo","viewId","globalFiltersSessionKey","fetchCount"]}',
        'stateId': 'babe4a62-46c1-4052-8349-307ba77ca224_1',
    }

        response = requests.post(
            'https://app2.clarizen.com/Clarizen/Ajax',
            params=self.get_params(),
            cookies=self._cookies,
            headers=http_constants.headers,
            data=data)
        soup = BeautifulSoup(response.json()['results'][0]['html'], "html.parser")
        file_rows = soup.div.div.div.nextSibling.div.div.nextSibling.nextSibling.div.div.div.div.table.find_all('tr')
        doc_info_list = []
        for row in file_rows:
            if 'data-doc' in row.attrs:
                file_name = row.td.nextSibling.div.span.nextSibling.a.text
                doc_info_list.append({
                    'doc_id': row.attrs['data-doc'],
                    'file_name': file_name
                })
        print(f'-- num docs: {len(doc_info_list)}')

        return doc_info_list



    def get_all_task_idents(self):
        """Run fetch_task_page over and over to get list of all task 'ids'"""
        got_more_tasks = True
        page_number = 1
        all_tasks = []
        while got_more_tasks:
            got_more_tasks = False
            tasks = self.fetch_task_page(page_number)
            if len(tasks) > 0:
                got_more_tasks = True
                all_tasks += tasks
            print(f'fetched {page_number} of tasks')

            page_number += 1
        print(all_tasks)


    def fetch_task_page(self, page_number):

        data = {
                'request': '{"htmlBuilder":"GridRowsCollection","htmlBuilderState":{"NotifyTo":"Pager,Filter,Ribbon_Grid,ItemCounter","StickyContainer":"","ElementId":"","ScrollBarWidth":0,"ScrollBarHeight":0,"Title":"50 Tasks","ParentControl":"DisplayView","SupportCustomScrollbars":true,"Mode":33580,"Draggable":true,"Level":0,"Containment":"contentWrapper","ClientId":0,"IsFilterable":true,"IsSortble":true,"OnChange":"updateObject","OnDrop":"linkObjectsOnDrop","SemiSelection":true,"AllowScrollToObject":true,"SupportContextualMenu":true,"SelectOnInit":true,"SupportSelection":true,"Id":"Grid","ContextId":"TS.GenericTask","DataProvider":"ObjectsCollection","Action":"GetItems","StateAdded":true,"Visible":true,"IsCCCSupported":true},"parameters":{"className":"GenericTask","queryName":"Subsystem","viewId":"354.11997121.0","userList":["9.183072769.24350977"],"timePeriod":{"fromDate":null,"toDate":null,"shortCut":null,"count":null},"pageNumber":' + str(page_number) + ',"fetchCount":-1,"pagingInfo":null,"sortInfo":{"Direction":0,"ColumnName":"PEDT","Alias":"","Order":0},"filtersInfo":{"filters":{"FLTTSK":{"Alias":null,"ReadOnlyOperator":false,"QueryName":null,"ChartAxisType":null,"Op":0,"Order":0,"IsPredefined":false,"Value":{"$type":"BCS.Presentation.View.SimpleFilterValue, BCS.Presentation.GenericLogic","Data":"true","IsEmptyValue":false},"ChartId":null,"IsEmptyValue":false,"ReadOnlyFilter":true,"Mandatory":true,"IsVisible":false,"ID":"FLTTSK","RuntimeValue":false,"DisplayName":null,"OverrideDisplayName":false,"IgnoreOpAndValueOnDisplayName":false,"FieldName":"FLTTSK","ClassName":"GenericTask"},"Role":{"Alias":null,"ReadOnlyOperator":false,"QueryName":null,"ChartAxisType":null,"Op":2,"Order":100,"IsPredefined":true,"Value":{"$type":"BCS.Presentation.View.PicklistFilterValue, BCS.Presentation.GenericLogic","Collection":[{"Data":"AnyRoleIndirect","IsEmptyValue":false}],"IgnoreConvertShortcutIdentifier":false,"IsEmptyValue":false,"MatchAll":false},"ChartId":null,"IsEmptyValue":false,"ReadOnlyFilter":null,"Mandatory":true,"IsVisible":false,"ID":"Role","RuntimeValue":false,"DisplayName":"Role","OverrideDisplayName":false,"IgnoreOpAndValueOnDisplayName":false,"FieldName":"Role","ClassName":"GenericTask"}},"searchFilter":null},"showAllTasks":false,"hasTeamPanel":false,"teamIdentifier":"9.183072769.24350977","layoutFilter":0,"timesheetShowWBD":false}}',
        'stateId': 'd3bc16a8-e2e1-4b7a-8ba6-c61fe032a1a5_1',
    }

        response = requests.post(
            'https://app2.clarizen.com/Clarizen/Ajax',
            params=self.get_params(), cookies=self._cookies, headers=http_constants.headers,
            data=data)

        soup = BeautifulSoup(response.json()['results'][0]['html'], "html.parser")
        # Each task element is:
        # <tr class="content-row draggable-parent drop-files-area" data-clientid="566" data-ident="8.9657719041.24350977"></tr>
        task_el_list = soup.table.find_all('tr')[0].find_all('tr')
        data_ident_list = []
        for el in task_el_list:
            if 'data-ident' in el.attrs:
                data_ident_list.append(el.attrs['data-ident'])

        return data_ident_list


    def run_downloads(self, download_list):

        print(f'*** fetching file group: num dls {len(download_list)} ***')
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(self.fetch_file, download_list)
        print('    done with fetch')


    def filter_approved_only(self, all_tasks):
        """Temporary utility function - not really used"""
        task_id_list = [t.split('.')[1] for t in all_tasks]

        with ThreadPoolExecutor(max_workers=30) as executor:
            results = list(executor.map(self.is_task_approved, task_id_list))

        tups = zip(results, task_id_list)
        approved_ids = []
        for t in tups:
            if t[0]:
                approved_ids.append(t[1])

        return approved_ids



