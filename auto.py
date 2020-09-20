import schedule
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import datetime
import os
import argparse

parser = argparse.ArgumentParser(description='Auto-Whatsapp Guide')
parser.add_argument('-p', '--chrome_driver_path', action='store', type=str, default='./chromedriver.exe', help='chromedriver executable path (MAC and Windows path would be different)')
parser.add_argument('-m', '--message', action='store', type=str, default='', help='Enter the msg you want to send')
# parser.add_argument('-r', '--remove_cache', action='store', type=str, default='False', help='Remove Cache | Scan QR again or Not')
args = parser.parse_args()



browser = None
Contact = None
message = None if args.message == '' else args.message
Link = "https://web.whatsapp.com/"
wait = None
choice = None




def input_contacts():
    global Contacts

    # List of Contacts
    Contacts = []


    while True:
        filename = input('Enter the name of the file:')
        column = input('Enter the name of the column which contains the Contact Numbers\n\nNote: Contact number should contain country code(integer):\n\nValid input: 91943xxxxx12\nInvalid input: +91943xxxxx12\n')
        # Example use: 919899123456, Don't use: +919899123456
        # Reference : https://faq.whatsapp.com/en/android/26000030/
        print()

        try:
            if '.xlsx' in filename:
                df = pd.read_excel(filename)
            else:
                df = pd.read_excel(filename + '.xlsx')

            try:
                for index in df.index:
                    inp = str(df.loc[index,column])
                    # print (inp)
                    Contacts.append(inp)
            except:
                print('Invalid Column Name')
        except:
            print('Invalid File Name')


        choi = input("Do you want to add more contacts(y/n)->")
        if choi == "n":
            break

    # if len(Contacts) != 0:
    #     print("\nContacts entered list->", Contact)
    print('%s number of contacts will recieve messages')
    input("\n Press ENTER to continue...")



def input_message():
    global message

    # Enter the message
    print('\n\nEnter the message and use "~" symbol to end the message.\n\nFor example:\n"Hello Everyone\nThis is a test message.~\n\nEnter your Message:\n')
    message = []
    temp = ''
    done = False

    while not done:
        temp = input()
        if len(temp) != 0 and temp[-1] == "~":
            done = True
            message.append(temp[:-1])
        else:
            message.append(temp)

    message = "\n".join(message)
    print()
    print('\n This is the message\n', message)
    print('\n\n')


def whatsapp_login(chrome_path):
    global wait, browser, Link
    chrome_options = Options()
    # chrome_options.add_argument('--user-data-dir=./User_Data')
    browser = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
    wait = WebDriverWait(browser,600)
    browser.get(Link)
    browser.maximize_window()
    print("QR Scanned")



def send_message():
    global message
    try:
        time.sleep(7)
        input_box = browser.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        for ch in message:
            if ch == "\n":
                ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.BACKSPACE).perform()
            else:
                input_box.send_keys(ch)
        input_box.send_keys(Keys.ENTER)
        return 1
    except NoSuchElementException:
        return 0



def sender():
    global Contacts, choice, docchoice

    for i in Contacts:
        link = "https://web.whatsapp.com/send?phone={}&text&source&data&app_absent".format(i)
        browser.get(link)
        f = send_message()
        if f==0:
            print('Failed to send to number %s' %(i))
        time.sleep(2)



def scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == '__main__':

    print('Web Page Open')

    # Append the contacts as input to send messages
    input_contacts()

    # Enter the message you want to send
    if message == None:
        input_message()

    # Login and Scan
    print('Scan the QR Code to login')
    whatsapp_login(args.chrome_driver_path)
    time.sleep(10)

    # Should the message be scheduled to a particular time
    isSchedule = input('Do you want to schedule your Message(yes/no):')

    # send the message
    if(isSchedule == "yes"):
        jobtime = input('input time in 24 hour (HH:MM) format: ')
        schedule.every().day.at(jobtime).do(sender)
    else:
        sender()

    # Task over
    print("Task Completed. Press ctrl + c to exit")

# Comment this piece incase you dont want to schedule
    if(isSchedule == "yes"):
        scheduler()
