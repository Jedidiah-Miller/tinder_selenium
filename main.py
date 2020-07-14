from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from secrets import email, password
import requests, os

from hotness_predictor import scores


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class TinderBot():

  base_url = 'https://tinder.com'

  swipe_screen_url = f'{base_url}/app/recs'

  fb_button_xpath = '//*[@id="modal-manager"]/div/div/div[1]/div/div[3]/span/div[2]/button'

  liked = []
  disliked = []


  def __init__(self, threshold=6.5):
    self.driver = webdriver.Chrome()
    self.threshold = threshold
    self.begining = True
    self.base_window = self.driver.window_handles[0]

  def navigate_to_login(self):
    self.driver.get(self.base_url)


  def navigate_home(self):
    self.driver.get(self.swipe_screen_url)

  def login(self):

    sleep(1.5)

    fb_button = self.driver.find_element_by_xpath(self.fb_button_xpath)
    fb_button.click()
    # switch to login popup
    self.driver.switch_to_window(self.driver.window_handles[1])

    email_in = self.driver.find_element_by_xpath('//*[@id="email"]')
    email_in.send_keys(email)

    pw_in = self.driver.find_element_by_xpath('//*[@id="pass"]')
    pw_in.send_keys(password)

    submit_in = self.driver.find_element_by_xpath('//*[@id="u_0_0"]')
    submit_in.click()

    self.driver.switch_to_window(self.base_window)
    sleep(2)
    self.handle_allow_location()


  def handle_allow_location(self):

    allow_btn = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div/div/div[3]/button[1]')
    allow_btn.click()

    enable_btn = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div/div/div[3]/button[1]')
    enable_btn.click()



  def like(self):
    like_btn = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[2]/div[4]/button')
    like_btn.click()

    self.liked.append(1)


  def dislike(self):
    dislike_btn = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[2]/div[2]/button')
    dislike_btn.click()

    self.disliked.append(1)

  def auto_swipe(self):
    while True:
      sleep(0.1)
      try:
        self.like()
      except Exception:
        try:
          self.close_add_popup()
        except Exception:
          self.close_match()
      self.display_history()

  def display_history(self):
    print('liked:', sum(self.liked), 'disliked:', sum(self.disliked))


  def close_match(self):
    ks_btn = self.driver.find_element_by_xpath('')

  def close_add_popup(self):
    ni_btn = self.driver.find_element_by_xpath('//*[@id="modal-manager"]/div/div/div[2]/button[1]')
    ni_btn.click()


# AI bits


  def choose(self):
    scrs = self.current_scores()
    choice = "DISLIKE"
    if len(scrs) == 0:
      self.dislike()
    elif [scr > self.threshold for scr in scrs] == len(scrs) * [True]:
      self.like() # if there are several faces, they must all have
      choice = "LIKE" # better score than threshold to be liked
    else:
      self.dislike()

    print("Scores : ",
          scrs,
          " | Choice : ",
          choice,
          " | Threshold : ",
          self.threshold)


  def ai_swipe(self):
    sleep(0.1)
    try:
      self.choose()
    except Exception as err:
      try:
        self.close_add_popup()
      except Exception:
        try:
          self.close_match()
        except Exception:
          print('--------------------------------------')
          print("Error: {0}".format(err))

    self.ai_swipe()


  def get_image_path(self):
    body = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[1]/div[3]/div[1]/div[1]/div/div[1]/div')
    bodyHTML = body.get_attribute('innerHTML')

    startMarker = 'background-image: url(&quot;'
    endMarker = '&quot;);'

    start = bodyHTML.find(startMarker) + len(startMarker)
    end = bodyHTML.find(endMarker)
    result = bodyHTML[start:end]
    return result


  def current_scores(self):
    url = self.get_image_path()
    outPath = os.path.join(APP_ROOT, 'images', os.path.basename(url))
    download_image(url, outPath)
    return scores(outPath)


# --------------------------------------------------------------------------------
def download_image(source, destination):
  img_data = requests.get(source).content
  with open(destination, 'wb') as out:
    out.write(img_data)




bot = TinderBot()
bot.navigate_to_login()
bot.login()