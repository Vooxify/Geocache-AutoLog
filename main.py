import re
import loading as L
import sys
from winotify import Notification
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import requests
import tkinter as tk
from requests.exceptions import ConnectionError

gc_codes = {}
bad_gc_codes = []

LOGIN = input("Enter your username : ")
PASSWORD = input("Enter your password : ")

driver = webdriver.Firefox()
driver.implicitly_wait(10)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/58.0.3029.110 Safari/537.3'
}


def write_on_multiple_lines(msg):

    print(msg)
    input_text = ""
    while True:
        line = input()
        input_text += line + "\n"
        if line == "":
            break

    return input_text


def take_geocache_gc_codes():
    geocache_url = "https://www.geocaching.com/geocache/"
    log_type = input("You want to log with list or manual ? ").lower()
    while True:
        if log_type == "list":
            geocache_list = link_list_input()
            driver.get(geocache_list)
            # Impossible de recup les noms dans une list, aucune class...
            time.sleep(5)  # Attendre le chargement de la page
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            gc_occurrences = find_gc_text(soup)
            print("This step can take some time...")
            load1 = L.Loading(type_load=['Taking all GC codes'])

            load1.animate_loading()
            for gc_names in gc_occurrences:
                driver.get(f"{geocache_url}{gc_names}")
                try:
                    L.Loading(type_load=['Searching geocache name from GC code', "Scanning"]).animate_loading()

                    geocache_name_element = locate_element(id_or_class='class', tag='tex2jax_ignore')

                    L.Loading(type_load=['Getting infos', "Adding to script list"]).animate_loading()

                    geocache_name = geocache_name_element.text
                    gc_codes[gc_names] = geocache_name
                except:
                    gc_occurrences = text_in_html(f'{geocache_url}{gc_names}', 'Error 404: DNF')
                    if gc_occurrences:
                        bad_gc_codes.append(gc_names)
            L.Loading(type_load=['Finishing', 'Checking GC codes', "Validating", "Closing"]).animate_loading()


        elif log_type == 'manual':
            # gc_code without 's' !!!!
            print("Input the code of the geocaches PAY ATTENTION TO YOUR CODES !"
                  "\n------------------------------------"
                  "\nEnter 'STOP' when you have finished\n")
            i = 1
            while True:
                gc_code = input(f"{i} - ")
                if gc_code == 'STOP':

                    break
                gc_url = "https://www.geocaching.com/geocache/" + gc_code
                driver.get(gc_url)
                try:
                    geocache_name_element = locate_element(id_or_class='class', tag='tex2jax_ignore')
                    L.Loading(type_load=["Taking name form GC code", 'Adding to script list']).animate_loading()
                    geocache_name = geocache_name_element.text
                    gc_codes[gc_code] = geocache_name
                except:
                    gc_occurrences = text_in_html(gc_url, 'Error 404: DNF')
                    if gc_occurrences:
                        bad_gc_codes.append(gc_code)

                i += 1
        else:
            log_type = input("Error, entrer a correct string ! ")
            continue

        print(f"There is {len(gc_codes)} geocaches to log. {len(bad_gc_codes)} bad geocache(s) code(s)")
        break


def locate_element(id_or_class, tag):
    if id_or_class == "class":
        locate_class_element = driver.find_element(By.CLASS_NAME, tag)
        return locate_class_element
    elif id_or_class == "id":
        locate_id_element = driver.find_element(By.ID, tag)
        return locate_id_element
    elif id_or_class == "xpath":
        locate_xpath_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{tag}')]")
        return locate_xpath_element
    else:
        print("ERROR in locate_element function !")


def link_list_input():
    while True:
        link_list = input("Enter a correct list link : ")
        try:
            r = requests.get(link_list, headers=headers)
            r.raise_for_status()
            break
        except requests.exceptions.MissingSchema:
            print("Link incorrect !")
    return link_list


def input_log_type():
    while True:
        log_type = input(f"How you want to log these {len(gc_codes)} geocaches ?"
                         "\n 1 - Chose all messages for all geocaches."
                         "\n 2 - 1 global message for all geocaches."
                         "\n     Select the code (1 or 2): ")
        if log_type == str(1):
            messages = log_geocache_step_by_step_manual()
            break
        elif log_type == str(2):
            messages = log_geocache_step_by_step_one_for_all()
            break
        else:
            print("ERROR, enter a correct number")
    return messages


# Custom message for any cache
def log_geocache_step_by_step_manual():
    messages = []
    for i in gc_codes.values():
        message = write_on_multiple_lines(f'Write your message for "{i}"\nTo finish, press Enter 2 times :')
        messages.append(message)

    return [element.strip() for element in messages]


def log_geocache_step_by_step_one_for_all():
    messages = []
    message = write_on_multiple_lines("Write the general message (applied to all logs !)")
    messages.append(message)

    return messages


def find_gc_text(soup):
    page_text = soup.get_text()
    gc_occurrences = re.findall(r'GC\w+', page_text)
    return [occurrence.replace('Modifier', '') for occurrence in gc_occurrences]


def text_in_html(url, search_text):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Vérifie si le code de statut est dans la plage 200-399
        html_content = response.text
        if search_text in html_content:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la vérification de l'URL : {e}")
        return True

def stock_logs(messages):
    associate_code_with_message = {}

    if len(messages) == 1:
        for g_code, g_msg in gc_codes.items():
            associate_code_with_message[g_code] = messages
    elif len(messages) >= 2:
        i = 0
        for g_code, g_msg in gc_codes.items():
            associate_code_with_message[g_code] = messages[i]
            i += 1
    return associate_code_with_message


def log(list):
    for k, v in list.items():
        geocache_url_without_code = "https://www.geocaching.com/geocache/"
        geocache_code = k
        geocache_url = f'{geocache_url_without_code}{geocache_code}'
        driver.get(geocache_url)
        log_button = locate_element(id_or_class="id", tag='ctl00_ContentBody_GeoNav_logButton')
        log_button.click()

        input("Chose the log mothod (founded, not founded, etc... on the web page. Then press enter key...)")
        input_type = locate_element(id_or_class="id", tag='gc-md-editor_md')
        input_type.send_keys(v)

        send_button = locate_element(id_or_class="class", tag='submit-button')
        input('You can modify the log, then press enter.')
        send_button.click()



def lunch_script(url_chosen):
    global occurrence

    driver.get(url_chosen)

    accept_cookies = locate_element(id_or_class="id", tag='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
    accept_cookies.click()

    connect_button = locate_element(id_or_class="class", tag='sign-in-link')
    connect_button.click()

    login_username_mail_tag = locate_element(id_or_class='id', tag='UsernameOrEmail')
    login_password_tag = locate_element(id_or_class="id", tag='Password')

    login_username_mail_tag.send_keys(LOGIN)
    login_password_tag.send_keys(PASSWORD)

    send_connection_tags = locate_element(id_or_class='id', tag="SignIn")
    send_connection_tags.click()

    take_geocache_gc_codes()
    msg = input_log_type()



    list_geocache_logs = stock_logs(msg)
    log(list_geocache_logs)



lunch_script("https://www.geocaching.com/")
driver.quit()
