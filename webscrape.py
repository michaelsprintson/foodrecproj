import selenium 
from selenium import webdriver
import json 
import re
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pickle 
import os
from tqdm import tqdm
import numpy as np
from multiprocessing.pool import ThreadPool, Pool
import threading
import ast

def checkExistsClass(classname, driver): 
    try:
        driver.find_element(By.CLASS_NAME, classname)
    except NoSuchElementException:
        return False
    return True

threadLocal = threading.local()

# DRIVER_PATH = "C:/Users/danjc/Downloads/chromedriver_win32/chromedriver.exe"
DRIVER_PATH = "chromedriver"
print(os.path.isfile(DRIVER_PATH))


def get_driver():
  driver = getattr(threadLocal, 'driver', None)
  if driver is None:
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('--disable-notifications')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--headless')
    driver = webdriver.Chrome(
            service = Service(DRIVER_PATH),
            options = options
        )
    setattr(threadLocal, 'driver', driver)
  return driver


# failed_titles = []
# r = open('recipe_reviews.txt', 'w')
# open all of the reviews first
# get the reviews. 

# Opening JSON file
# f = open('allrecipes-recipes.json')
# allrecipes_list = f.readlines()
start = time.time()
# all_reviews = []

def get_reviews(x): 
    num, recipesDict = x
    driver = get_driver()
    oldUrl = recipesDict[0]
    title = recipesDict[1]
    newtitle = title.replace(",", "")
    newtitle = newtitle.replace("'", "")
    newtitle = newtitle.lower()
    newtitle = newtitle.replace(" ", "-")
    newUrl = oldUrl+newtitle
    driver.get(newUrl)
    time.sleep(3)
    #click new recipes buttons. 
    # newReviews = checkExistsClass("feedback-list__load-more-button", driver)
    newReviews = True
    review_store = []
    fail_flag = 0
    while newReviews:
        try:
            
            reviews = driver.find_elements(By.CLASS_NAME, "feedback-list__item")
            # print(len(reviews))
            for review in reviews[-9:]:
                reviewer_name= review.find_element(By.CLASS_NAME, "feedback__display-name")
                reviewer_feedback = review.find_element(By.CLASS_NAME, "feedback__text")
                stars = review.find_elements(By.CLASS_NAME, "feedback__stars")
                count = 0
                for star in stars:
                    group = star.find_elements(By.CLASS_NAME, "feedback__star")
                    for item in group: 
                        x = item.find_element(By.XPATH, ".//*[name()='svg']")
                        if x.get_attribute("class") == "icon ugc-icon-star ugc-icon-avatar-null":
                            count += 1 

                review_total = [str(num), reviewer_name.text, reviewer_feedback.text, str(count) ]
                # all_reviews.append(review_total)
                # review_store.append(review_total[0]+"; "+review_total[1]+"; "+review_total[2]+"; "+review_total[3])
                file_write = open('test.txt', 'a')
                file_write.write(review_total[0]+"; "+review_total[1]+"; "+review_total[2]+"; "+review_total[3])
                file_write.write("\n")
            
            
            newReviews = checkExistsClass("feedback-list__load-more-button", driver)
            if newReviews:
                driver.find_element(By.CLASS_NAME, "feedback-list__load-more-button").click()
                # print('clicked')
                time.sleep(3)

        except:
            fail_flag =+ 1
            pass
    if fail_flag == 0:
        file_write = open('finished_reviews.txt', 'a')
        file_write.write(f"{num},")
    else:
        file_write = open('failed_reviews.txt', 'a')
        file_write.write(f"{num}-{fail_flag},")
    return num

e_f = []
with open("allrecipes-recipes.json") as f:
    for jsonOb in tqdm(f):
        recipesDict = json.loads(jsonOb)
        oldUrl = recipesDict["url"]
        title = recipesDict["title"]
        e_f.append((oldUrl,title))
enum_e_f = enumerate(e_f[:100_000])

with open("finished_reviews.txt",'r') as fr:
    finished_reviews = set(ast.literal_eval("[" + fr.readline() + "]"))

final_e_f = [(i,k) for i,k in enum_e_f if i not in finished_reviews]

start = time.time()
if __name__ == '__main__':
  l = len(final_e_f)
  for _ in tqdm(ThreadPool(None).imap_unordered(get_reviews,final_e_f), total=l):
    pass
  
print(np.around(time.time() - start, decimals= 2))

# pi1 = open('allreviews.obj', 'wb')
# pi2 = open('failed_titles.obj', 'wb')

# pickle.dump(all_reviews, pi1)
# pickle.dump(failed_titles, pi2)

# print(end-start)



  
f.close()