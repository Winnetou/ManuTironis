#! /usr/bin/python
# coding:utf-8
from behave import *

@given('user is on page with lists of texts')
def step_impl(context):
    context.browser.get("http://localhost:8000/edit")

@when('user clicks on a text')
def step_impl(context):
    ''' '''
    context.browser.find_element
@then('user is redirected to the first page contaning incorrect words')
def step_impl(context):
    ''' ''' 
    #assert the url is correct
    assert context.browser.current_url ==
    #assert at least one incorrect words
    assert context.browser.find_element_

#---------------------
# BELOW: Editing text steps
#_____________________

@given('user is on text page')
def step_impl(context):
    context.execute_steps('''
        given user is on page with lists of texts
        when user clicks on a text
        ''')

@when('user click on an incorrect word')
def step_impl(context):
    ''' Incorrect word:corr="0" '''
    context.browser.find_element_by() is not None

@then('right pane is populated with correction suggestions')
def step_impl(context):
    ''' '''
    right_pane = context.browser.find_element_
    
@when('')
def step_impl(context):
    pass

@when('')
def step_impl(context):
    pass

