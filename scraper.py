from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import bs4
from convertHumanTime import converTime
import csv

urls = open("sample_urls.txt")
for url in urls:

    # convert to language english instead of local language 
    url += "?hl=en"

    # check if url is valid
    if "https://www.google.co.uk/maps/place/" not in url:
        continue


    # getting the place name from url
    locationName = url.split("/")[5].replace("+", "_")
    # print(locationName)

    # chromedriver options
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_experimental_option("detach", True)
    # uncomment bellow urgument if don't want to see chrome browser poping up
    # opts.add_argument("--headless")

    # initializing chrome driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)

    # opening url from chromedriver. adjust waiting time depending internet speed 
    driver.get(url)
    time.sleep(10)

    # height variable for scrolling
    last_height = 0
    while True:
        # using javascript to scroll at the bottom
        driver.execute_script("document.getElementsByClassName('m6QErb')[4].scrollTo(0, document.getElementsByClassName('m6QErb')[4].scrollHeight)")
        time.sleep(5)

        new_height = driver.execute_script("return document.getElementsByClassName('m6QErb')[4].scrollHeight")
        # print('new_height:', new_height)

        # will continue scrolling until reach bottom
        if new_height == last_height:
            break
        else:
            last_height = new_height

    # this one not necessary but sometimes it helps
    time.sleep(5)

    # parsing review data using bs4
    soup = bs4.BeautifulSoup(driver.page_source, 'lxml')
    reviews = soup.find_all("div", attrs={"data-review-id":True})

    reviewIdList = []

    # generating outputfile 
    outputFile = open(f"{locationName}.csv", 'w')
    writer = csv.writer(outputFile)

    csvHeader = ['Reviewer_Name', 'Reviewer_Type', 'Review_Time', 'Num_of_Review', 'Stars', 'Review_Comment']
    writer.writerow(csvHeader)

    for review in reviews:
        dataReviewId = review['data-review-id']

        if dataReviewId in reviewIdList:
            pass
        else:
            try:
                reviewIdList.append(dataReviewId)

                reviewDivs = review.find_all("div")[3]

                reviewDivsSub = reviewDivs.find_all("div")[3]

                titles = reviewDivsSub.find_all("span")

                reviewer = titles[0].text
                guide_type = titles[1].text
                numOfReviews = titles[2].text.replace("·", "")

                reviewTextFull = reviewDivs.findChildren("div", recursive=False)[-1]

                reviewSpans = reviewTextFull.find_all("span")
                reviewStar = reviewSpans[1]["aria-label"]
                reviewTime = converTime(reviewSpans[2].text)

                # try to find review comment if not found that means user didn't leave any comment
                try:
                    reviewText = reviewTextFull.find("div", {"id":dataReviewId})
                    reviewText = reviewText.find_all("span")[1].text
                except:
                    reviewText = ""

                # print(f"reviewer: {reviewer}| guide_type: {guide_type}| reviews:{numOfReviews}| reviewStar:{reviewStar}| reviewTime:{reviewTime}| reviewText: `{reviewText}` ")
                # print("\n")

                # adding data to outputFile
                writer.writerow([
                    reviewer,
                    guide_type,
                    reviewTime,
                    numOfReviews,
                    reviewStar,
                    reviewText
                ])
            except:
                pass

    # print(len(reviewIdList))
    
    # exiting chromedriver
    driver.quit()

    # break