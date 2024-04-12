import bs4 as bs
from urllib.request import Request, urlopen
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
import selenium.common.exceptions

import os
import re
import sys
website = 'https://www.thecarconnection.com'
template = 'https://images.hgmsites.net/'


def fetch(page, addition=''):
    return bs.BeautifulSoup(urlopen(Request(page + addition,
                            headers={'User-Agent': 'Opera/9.80 (X11; Linux i686; Ub'
                                     'untu/14.10) Presto/2.12.388 Version/12.16'})).read(),
                                     'lxml')


def all_makes():
    car_makes = []
    soup = fetch(website, "/new-cars")
    for i in range(1, 7):  # 1 to 6 inclusive
        selector = f"#by-make > div.block-inner > div:nth-child({i})"
        by_make_div = soup.select_one(selector)
        car_make_links = by_make_div.find_all("a")

        for link in car_make_links:
            car_make_url = link['href']
            car_makes.append(car_make_url)

    return car_makes


def make_menu(listed):
    make_menu_list = []
    for make in listed: 
        for div in fetch(website, make).find_all("div", {"class": "name"}):
            make_menu_list.append(div.find_all("a")[0]['href'])

    return make_menu_list


def model_menu(listed, selenium_driver):
    model_menu_list = []
    for make in listed:
        soup = fetch(website, make)
        selenium_driver.get(website + make)
        ul_element = soup.select_one("#left-column > div > div.year-selector > ul")
        if ul_element is not None:
            for a in ul_element.find_all('a'):
                model_menu_list.append(a['href'])
        try:
            dropdown = selenium_driver.find_element(By.CLASS_NAME, 'dropdown')
            dropdown.click()
            options = dropdown.find_elements(By.ID, 'moreYmm')  # get the options
            for option in options:
                model_menu_list.append(option.get_attribute("href"))
        except selenium.common.exceptions.NoSuchElementException:
            continue

    # Filter out unreleased vehicles. For that _2025
    model_menu_list = [i for i in model_menu_list if i is not None and not i.endswith('_2025')]
    model_menu_list = [i.replace('overview', 'specifications') for i in model_menu_list if i is not None]
    return model_menu_list

def specs_and_pics(listed):
    picture_tab = [i.replace('overview', 'photos') for i in listed if i is not None]
    specifications_table = pd.DataFrame()
    for row, pic in zip(listed, picture_tab):
        try:
            soup = fetch(website, row)
            specifications_df = pd.DataFrame(columns=[soup.find_all("title")[0].text[:-15]])
        except Exception as e:
            print('Error with {}.'.format(website + row))
            continue

        try:
            specifications_df.loc['Make', :] = soup.find_all('a', {'id': 'a_bc_1'})[0].text.strip()
            specifications_df.loc['Model', :] = soup.find_all('a', {'id': 'a_bc_2'})[0].text.strip()
            specifications_df.loc['Year', :] = soup.find_all("title")[0].text[:4].strip()
        except:
            print('Problem with {}.'.format(website + row))

        for div in soup.find_all("div", {"class": "specs-set-item"}):
            row_name = div.find_all("span")[0].text
            row_value = div.find_all("span")[1].text
            specifications_df.loc[row_name] = row_value

        fetch_pics_url = str(fetch(website, pic))

        try:
            match = re.findall('lrg.+?_l.jpg', fetch_pics_url)
            if match:
                photo = match[0].replace('\\', '')
                specifications_df.loc['Picture', :] = photo
            specifications_table = pd.concat([specifications_table, specifications_df], axis=1, sort=False)
        except:
            print('Error with {}.'.format(template + photo))
    return specifications_table


def run(directory):
    options = ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)

    os.chdir(directory)
    a = all_makes()
    b = make_menu(a)
    c = model_menu(b, driver)
    pd.DataFrame(c).to_csv('c.csv', header=None)
    d = pd.read_csv('c.csv', index_col=0, header=None).values.ravel()
    e = specs_and_pics(d)
    e.to_csv('specs-and-pics.csv')

    driver.quit()


if __name__ == '__main__':
    if not os.path.isdir(sys.argv[1]):
        os.mkdir(sys.argv[1])

    print('%s started running.' % os.path.basename(__file__))
    run(sys.argv[1])
    print('%s finished running.' % os.path.basename(__file__))
