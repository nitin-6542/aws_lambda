import json
import boto3
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

print("here")
# AWS Config
S3_BUCKET_NAME = "instareelsupload"
DYNAMODB_TABLE_NAME = "instagram_variable"
COOKIES_FILE_KEY = "Cookies/cookies.json"
VIDEOS_FOLDER = "videos/"

# Set up S3 and DynamoDB
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def get_start_value():
    """Fetch the current `start` value from DynamoDB."""
    response = table.get_item(Key={"start": "start"})  # 'start' is the partition key
    # print(response)  # For debugging
    # Ensure the value is properly extracted and converted
    return int(response.get("Item", {}).get("value", 1))


def save_start_value(start):
    """Save the updated `start` value to DynamoDB."""
    table.put_item(Item={"start": "start", "value": start})  # Use 'start' as the partition key


def load_cookies(driver):
    """Load cookies from S3."""
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=COOKIES_FILE_KEY)

        # Check if the content length is zero
        if response['ContentLength'] == 0:
            print(f"Error: The file {COOKIES_FILE_KEY} is empty.")
            return []

        # Read and decode the response body, then load it as JSON
        cookies = json.loads(response["Body"].read().decode())
        print(cookies)

        for cookie in cookies:
            driver.add_cookie(cookie)

    except Exception as e:
        print(e)

def save_cookies(driver):
    """Save cookies to S3."""
    cookies = driver.get_cookies()
    s3.put_object(Bucket=S3_BUCKET_NAME, Key=COOKIES_FILE_KEY, Body=json.dumps(cookies))

def get_videos_from_s3():
    """Fetch the list of videos from S3."""
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=VIDEOS_FOLDER)
    return [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].endswith(".mp4")]

def download_video_from_s3(video_key, local_path="/tmp"):
    """Download a video from S3 to Lambda's /tmp directory."""
    local_file = os.path.join(local_path, os.path.basename(video_key))
    s3.download_file(S3_BUCKET_NAME, video_key, local_file)
    return local_file

def upload_reel(driver, video_path, description):
    """Automate Instagram Reel upload."""
    driver.get("https://www.instagram.com")
    time.sleep(7)
    load_cookies(driver)
    time.sleep(8)
    driver.get("https://www.instagram.com/ai_fantasy_world_/reels/")
    time.sleep(6)
    driver.find_element(By.XPATH,"//span[contains(text(),'Create')]").click()
    time.sleep(5)
    # save_cookies(driver,'cookies.json')
    # exit()
    driver.find_element(By.XPATH,"//div[@class='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1pi30zi x1swvt13 xwib8y2 x1y1aw1k x1uhb9sk x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1 xn3w4p2']//div[@class='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1uhb9sk x1plvlek xryxfnj x1iyjqo2 x2lwn1j xeuugli xdt5ytf xqjyukv x1cy8zhl x1oa3qoh x1nhvcw1']").click()

    # input=driver.find_element(By.XPATH,"//button[normalize-space()='Select From Computer']")
    # input.click()
    time.sleep(7)
    driver.find_element(By.XPATH, "//input[@accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']").send_keys(video_path)
    time.sleep(6)
    count= driver.find_elements(By.XPATH,"//button[contains(text(),'OK')]") 
    if len(count)>=1:
        count[0].click()
    

    time.sleep(6)

    
    driver.find_element(By.XPATH,"(//div[@class='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1y1aw1k x1sxyh0 xwib8y2 xurb0ha x1n2onr6 x1plvlek xryxfnj x1c4vz4f x2lah0s x1q0g3np xqjyukv x6s0dn4 x1oa3qoh xl56j7k'])[1]").click()    
    driver.find_element(By.XPATH,"(//div[@class='x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x16n37ib x150jy0e x1e558r4 x1n2onr6 x1plvlek xryxfnj x1iyjqo2 x2lwn1j xeuugli x1q0g3np xqjyukv x6s0dn4 x1oa3qoh x1nhvcw1'])[3]").click()
    time.sleep(3)
   
    driver.find_element(By.XPATH,"//div[contains(text(),'Next')]").click()
    time.sleep(3)
    driver.find_element(By.XPATH,"//div[contains(text(),'Next')]").click()
    time.sleep(3)
    driver.find_element(By.XPATH,"//div[@aria-label='Write a caption...']").send_keys(description)
    share_button = driver.find_element(By.XPATH, "//div[contains(text(),'Share')]")  # Update as needed
    share_button.click()
    # time.sleep(300)
    count=driver.find_elements(By.XPATH,"//img[@alt='Animated tick']")
    count2=driver.find_elements(By.XPATH,"//div[@class='x92rtbv x10l6tqk x1tk7jg1 x1vjfegm']")
    if len(count2)>=1:
        count2[0].click()
    c=10
    while c>0:
        time.sleep(5)
        count=driver.find_elements(By.XPATH,"//img[@alt='Animated tick']")
        count2=driver.find_elements(By.XPATH,"//div[@class='x92rtbv x10l6tqk x1tk7jg1 x1vjfegm']")
        print(count)
        if len(count2)>=1:
            count2[0].click()
            break
        if len(count)==1:
            break
        print(c)
        c-=1

    save_cookies(driver)


def lambda_handler():
    # Get current `start` value from DynamoDB
    start = get_start_value()
    print(start)
    
    # Fetch videos from S3
    video_keys = sorted(get_videos_from_s3(), key=lambda x: int(x.split("/")[-1].split(".")[0][5:]))
    print(video_keys)
    # Find the video with the `start` number
    video_key = next((key for key in video_keys if int(key.split("/")[-1].split(".")[0][5:]) == start), None)
    print(video_key)
    if not video_key:
        return {"statusCode": 200, "body": f"No video found for number {start}"}

    # Download the video
    local_video_path = download_video_from_s3(video_key)
    print("Download")
    description = f"Leo Part  #{start} "

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1280x1696')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-dev-tools')
    options.add_argument('--no-zygote')
    options.add_argument('--remote-debugging-port=9222')



    driver = uc.Chrome(options=options)
    print("Driver")
    try:
        upload_reel(driver, local_video_path, description)
        save_start_value(start + 1)  # Increment to the next video number
    finally:
        driver.quit()

    return {"statusCode": 200, "body": f"Uploaded video #{start}"}

# event, context
lambda_handler()
# driver=1
# print(load_cookies(driver))
