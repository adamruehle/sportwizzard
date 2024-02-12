import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import time
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from datetime import datetime

def login(driver):
    driver.get("https://underdogfantasy.com/pick-em/higher-lower/all/nba")
    driver.maximize_window()
    time.sleep(3)
    email_input = driver.find_element(By.CSS_SELECTOR, '.styles__field__Q6LKF [data-testid="email_input"]')
    email_input.send_keys("adamruehle@live.com")
    password_input = driver.find_element(By.CSS_SELECTOR, '.styles__field__Q6LKF [data-testid="password_input"]')
    password_input.send_keys("mT4zt2sJaYT88BPb@KG!WG_YK")
    sign_in_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="sign-in-button"]')
    sign_in_button.click()
    time.sleep(2)
    # driver.get("https://underdogfantasy.com/pick-em/higher-lower/all/nba")
    driver.get("https://underdogfantasy.com/pick-em/higher-lower/pre-game/nba")

def find_player_and_props(driver, player_prop_div):
    more_picks_button = WebDriverWait(player_prop_div, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button")))[-1]
    try:
        more_picks_span = more_picks_button.find_element(By.CSS_SELECTOR, 'span')
        if "More picks" in more_picks_span.text:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", more_picks_button)
            more_picks_button.click()
    except:
        None
    player_name_element = WebDriverWait(player_prop_div, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.styles__playerName__jW6mb')))
    player_name = player_name_element.text
    props = []
    stat_line_elements = player_prop_div.find_elements(By.CSS_SELECTOR, 'div.styles__overUnderListCell__tbRod')
    player_data = {'Name': player_name}
    for stat_line_element in stat_line_elements:
        prop = stat_line_element.find_element(By.CSS_SELECTOR, 'p').text
        if "1H" in prop or "1Q" in prop:
            continue
        prop_name, value = prop.split(' ', 1)  # Split by the first space
        player_data[prop_name] = value
        props.append(prop)

    return player_name, props

def write_to_csv(data):
    current_date = datetime.now().strftime("%Y-%m-%d")
    csv_file_path = f'betonline_scripts/underdog-lines/player_data_{current_date}.csv'
    directory = os.path.dirname(csv_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Extract all unique property names from data
    all_props = [prop for player_data in data for prop in player_data.keys() if prop != 'Name']
    unique_props = list(set(all_props))
    # Define fieldnames including 'Name' and unique properties
    fieldnames = ['Name'] + unique_props
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        # Write data to CSV file
        for player_data in data:
            # Create dictionary with all properties and their corresponding values
            player_dict = {'Name': player_data['Name']}
            for prop in unique_props:
                player_dict[prop] = player_data.get(prop, '')
            writer.writerow(player_dict)

def do_logic():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    login(driver)
    player_prop_divs_containers = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.styles__content___R51k")))
    player_prop_divs = []

    for player_prop_divs_container in player_prop_divs_containers:
        current_player_prop_divs = player_prop_divs_container.find_elements(By.CSS_SELECTOR, "div.styles__overUnderCell__KgzNn")
        for player_prop_div in current_player_prop_divs:
            player_prop_divs.append(player_prop_div)

    data = []
    for player_prop_div in player_prop_divs:
        player_name, props = find_player_and_props(driver, player_prop_div=player_prop_div)
        player_data = {'Name': player_name}
        for prop in props[1:]:
            prop_name = prop.replace(" + ", "").split(" ")[1].strip()
            if "PtsRebsAsts" in prop_name:
                prop_name = f"PointsReboundsAssists"
            if "3-Pointers" in prop_name:
                prop_name = f"Threes"
            prop_name = prop_name + "_Line"
            value = prop.split(" ")[0].strip()
            player_data[prop_name] = value
        data.append(player_data)
    write_to_csv(data)
    driver.quit()