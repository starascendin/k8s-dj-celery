from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
# Create a new instance of the Firefox driver

from selenium import webdriver
import geckodriver_autoinstaller
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

geckodriver_autoinstaller.install()

profile = webdriver.FirefoxProfile(
    '/Users/bryanliu/Library/Application Support/Firefox/Profiles/hd8gxqcw.default-release')

profile.set_preference("dom.webdriver.enabled", False)
profile.set_preference('useAutomationExtension', False)
profile.update_preferences()
desired = DesiredCapabilities.FIREFOX

driver = webdriver.Firefox(firefox_profile=profile,
                           desired_capabilities=desired)


# driver = webdriver.Firefox()

# Navigate to the page
# url = "https://typeshare.co/templates/type/atomic-essay"

content_types = [{
    "name": "tweet",
    "url": "https://typeshare.co/templates/type/tweet",
    "output": "typeshare_tweets.csv",
}, {
    "name": "thread",
    "url": "https://typeshare.co/templates/type/thread",
    "output": "typeshare_threads.csv",
}, {
    "name": "subatomic-essay",
    "url": "https://typeshare.co/templates/type/subatomic-essay",
    "output": "typeshare_subatomic_essays.csv",
},
# {
#     "name": "atomic-essay",
#     "url": "https://typeshare.co/templates/type/atomic-essay",
#     "output": "typeshare_atomic_essays.csv",
# },
]


for content_type in content_types:


    url = content_type['url']
    driver.get(url)

    # Wait for the page to load
    wait = WebDriverWait(driver, 20)

    # Find the buttons with the "Previewed Template" data-track attribute
    sleep(10)
    buttons = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[data-track='Previewed Template']")))


    contents = []

    # Iterate through each button
    for button in buttons:
        # Click the button
        button.click()

        # div of modal title

        # div_preview_blob= ''
        # # flex flex-row flex-wrap items-center justify-start
        div_preview = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.flex-row.flex-wrap.items-center.justify-start")))
        div_preview_blob = div_preview.text

        print("#div_preview_blob ", div_preview_blob)

        # # Wait for the h1 with class "lg-blog" to load
        # h1_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.mt-4")))
        # h1_blob = h1_title.text
        h1_blob = ''

        # Wait for the div with class "lg-blog" to load
        lg_blog = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.lg-blog")))

        # Extract the data from the div
        body_blob = lg_blog.text

        # Press the Escape key
        content = {
            "title": str(h1_blob),
            "body": str(body_blob),
            "preview": str(div_preview_blob),
        }
        print("#content ", content)

        # driver.find_element_by_tag_name('body').send_keys(Keys.ESCAPE)
        sleep(1)
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        print("Waiting for 3 seconds before clicking the next butto")
        wait = WebDriverWait(driver, 5)
        sleep(5)
        print("Done waiting")
        contents.append(content)


    # write contents to a csv file
    import csv
    with open(content_type['output'], 'w') as csvfile:
        fieldnames = ['title', 'body', 'preview']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for content in contents:
            writer.writerow(content)



