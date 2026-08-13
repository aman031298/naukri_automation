"""
Naukri.com CSS selectors
"""
class Selectors:
    """Naukri.com element selectors"""
    
    # Login
    LOGIN_BTN = "a:has-text('Login')"
    USERNAME = "input#usernameField, input[name='username']"
    PASSWORD = "input#passwordField, input[name='password']"
    SUBMIT_BTN = "button[type='submit']"
    
    # Search
    SEARCH_INPUT = "input[title='Search'], input.search-job"
    LOCATION_INPUT = "input[title='Location'], input.location"
    SEARCH_BTN = "button[type='submit']"
    
    # Job cards
    JOB_CARD = "article.jobTuple, .jobCard, .job-list-card"
    JOB_TITLE = ".title a, .job-title, h2 a"
    COMPANY_NAME = ".subTitle, .company, .job-company"
    JOB_LOCATION = ".loc, .location, .job-location"
    
    # Application
    APPLY_BTN = "button:has-text('Apply')"
    VIEW_APPLY = "button:has-text('View & Apply')"