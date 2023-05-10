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
import ray
import numpy as np

ray.init(dashboard_port=9008)

def checkExistsClass(classname, driver): 
    try:
        driver.find_element(By.CLASS_NAME, classname)
    except NoSuchElementException:
        return False
    return True

# DRIVER_PATH = "C:/Users/danjc/Downloads/chromedriver_win32/chromedriver.exe"
DRIVER_PATH = "chromedriver"
print(os.path.isfile(DRIVER_PATH))
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('--disable-notifications')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--headless')


failed_titles = []
r = open('recipe_reviews.txt', 'w')
# open all of the reviews first
# get the reviews. 

# Opening JSON file
# f = open('allrecipes-recipes.json')
# allrecipes_list = f.readlines()
start = time.time()
all_reviews = []

def get_reviews(driver, num, recipesDict): 
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
    newReviews = checkExistsClass("feedback-list__load-more-button", driver)
    review_store = []
    while newReviews:
        driver.find_element(By.CLASS_NAME, "feedback-list__load-more-button").click()
        # print('clicked')
        time.sleep(3)
        newReviews = checkExistsClass("feedback-list__load-more-button", driver)

        try:
            reviews = driver.find_elements(By.CLASS_NAME, "feedback-list__item")
            for review in reviews:
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
                all_reviews.append(review_total)
                review_store.append(review_total[0]+"; "+review_total[1]+"; "+review_total[2]+"; "+review_total[3])
                # file_write.write()
                # file_write.write("\n")
        except:
            pass
    return review_store

@ray.remote
def mega_work(start, end, e_f, options):
    
    driver = webdriver.Chrome(
            service = Service(DRIVER_PATH),
            options = options
        )
    results = []
    for x in (pbar:= tqdm(range(start, end))):
        # if x<894:
            # print(int(np.around((x-start)/(end-start), decimals=2)*100))
        results.append(get_reviews(driver, x, e_f[x]))
        pbar.set_description(f"start: {start}")
    return [i for j in results for i in j]




e_f = []
with open("allrecipes-recipes.json") as f:
    for jsonOb in tqdm(f):
        recipesDict = json.loads(jsonOb)
        oldUrl = recipesDict["url"]
        title = recipesDict["title"]
        e_f.append((oldUrl,title))
        
e_f_ray = ray.put(e_f)
options_ray = ray.put(options)

start = time.time()
result_ids = []
[result_ids.append(mega_work.remote(x*5, (x+1)*5, e_f_ray, options_ray)) for x in range(3)]
results = ray.get(result_ids)
results_flat = [i for j in results for i in j]
print(results_flat)
print("duration =", time.time() - start)


end = time.time()


print('failed titles')
print(failed_titles)


pi1 = open('allreviews.obj', 'wb')
pi2 = open('failed_titles.obj', 'wb')

pickle.dump(all_reviews, pi1)
pickle.dump(failed_titles, pi2)

print(end-start)



  
f.close()