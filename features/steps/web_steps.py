######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
import time
from os import getenv
from behave import when, then
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

BASE_URL = getenv('BASE_URL', 'http://localhost:8080')

@when('I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(BASE_URL)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')

@when('I switch to the "Item page"')
def step_impl(context):
    lis = context.driver.find_elements_by_xpath(
        "//ul[@class='el-menu-demo el-menu--horizontal el-menu']/li")

    for li_item in lis:
        if "Items" in li_item.text:
            li_item.click()
            break

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    error_msg = "I should not see '%s' in '%s'" % (text_string, element.text)
    ensure(text_string in element.text, False, error_msg)

# use for checking the option in Query
# text: Customer ID; element_name: Query
# eg. id -> customer_id_query
@when('I check the "{text}" in the "{element_name}" Area')
def step_impl(context, text, element_name):
    element_id = text.lower().replace(' ', '_') + '_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.click()

# element_name: query; text_string: 4352
@when('I set the "{element_id}" to "{text_string}"')
def step_impl(context, element_id, text_string):
    element_id = element_id.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = element_name.lower().replace(' ', '_')
    WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    lis = context.driver.find_elements_by_xpath(
        "//ul[@class='el-scrollbar__view el-select-dropdown__list']/li")

    for li_item in lis:
        if text in li_item.text:
            li_item.click()
            break

@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = element_name.lower().replace(' ', '_')
    # context.driver.find_element_by_id(element_id).click()
    WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    lis = context.driver.find_elements_by_xpath(
        "//ul[@class='el-scrollbar__view el-select-dropdown__list']/li")

    for li_item in lis:
        if li_item.is_selected():
            expect(lis.text).to_equal(text)
            break

@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(' ', '_')
    element = context.driver.find_element_by_id(element_id)
    expect(element.get_attribute('value')).to_be(u'')

##################################################################
# These two function simulate copy and paste
##################################################################

@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute('value')
    logging.info('Clipboard contains: %s', context.clipboard)

@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(' ', '-') + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should see "{name}" in the Item results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'search_results_item'),
            name
        )
    )
    expect(found).to_be(True)

@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('I should not see "{name}" in the Item results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results_item')
    error_msg = "I should not see '%s' in '%s'" % (name, element.text)
    ensure(name in element.text, False, error_msg)

@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, 'flash_message'),
            message
        )
    )
    expect(found).to_be(True)

@then('I should see the Item message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, 'flash_message_item'),
            message
        )
    )
    expect(found).to_be(True)

##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# We can then lowercase the name and prefix with order_ to get the id
##################################################################

@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = element_name.lower().replace(' ', '_')
    found = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id),
            text_string
        )
    )
    expect(found).to_be(True)

@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = element_name.lower().replace(' ', '_')
    element = WebDriverWait(context.driver, context.WAIT_SECONDS).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)
