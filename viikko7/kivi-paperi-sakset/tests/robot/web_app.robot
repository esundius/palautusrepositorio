*** Settings ***
Library           SeleniumLibrary
Library           Process
Library           Collections
Library           OperatingSystem
Suite Setup       Setup Suite
Suite Teardown    Stop App Server
Test Teardown     Close All Browsers

*** Variables ***
${PORT}           5001
${BASE_URL}       http://127.0.0.1:${PORT}

*** Keywords ***
Start App Server
    ${env}=    Get Environment Variables
    Set To Dictionary    ${env}    PYTHONPATH    ${CURDIR}/../../src
    Run Process    poetry    run    flask    --app    src.web_app    run    --port    ${PORT}    env=${env}    alias=server    stdout=${TEMPDIR}/flask-server.log    stderr=STDOUT
    Wait For Server

Setup Suite
    Start App Server
    Ensure Chrome Available

Wait For Server
    Wait Until Keyword Succeeds    15s    1s    Ping App

Ping App
    ${_}=    Evaluate    __import__('urllib.request').request.urlopen('${BASE_URL}', timeout=2).read()

Stop App Server
    Run Keyword And Ignore Error    Terminate Process    server

Ensure Chrome Available
    ${paths}=    Create List    /Applications/Google Chrome.app/Contents/MacOS/Google Chrome    /usr/bin/google-chrome    /usr/bin/chromium    /usr/bin/chromium-browser
    FOR    ${p}    IN    @{paths}
        ${exists}=    Run Keyword And Return Status    File Should Exist    ${p}
        Run Keyword If    ${exists}    Set Suite Variable    ${CHROME_BIN}    ${p}
        Run Keyword If    ${exists}    Return From Keyword
    END
    ${status}=    Run Keyword And Return Status    Run And Return Stdout    which google-chrome
    Run Keyword If    ${status}    ${out}=    Run And Return Stdout    which google-chrome
    Run Keyword If    ${status}    Set Suite Variable    ${CHROME_BIN}    ${out.strip()}
    Run Keyword If    ${status}    Return From Keyword
    Skip    Chrome/Chromium not found; install Google Chrome to run browser tests.

Open Headless Chrome
    ${chromedriver}=    Evaluate    __import__('webdriver_manager.chrome', fromlist=['ChromeDriverManager']).ChromeDriverManager().install()    modules=webdriver_manager.chrome
    ${options}=    Evaluate    __import__('selenium.webdriver', fromlist=['ChromeOptions']).ChromeOptions()    modules=selenium.webdriver
    Call Method    ${options}    add_argument    --headless\=new
    Call Method    ${options}    add_argument    --no-sandbox
    Call Method    ${options}    add_argument    --disable-dev-shm-usage
    Call Method    ${options}    add_argument    --disable-gpu
    ${service}=    Evaluate    __import__('selenium.webdriver.chrome.service', fromlist=['Service']).Service(executable_path='${chromedriver}')    modules=selenium.webdriver.chrome.service
    Create Webdriver    Chrome    options=${options}    service=${service}

Go To Home
    Open Headless Chrome
    Go To    ${BASE_URL}

Check Move Button Disabled
    ${disabled}=    Execute Javascript    return document.querySelector("form[action='/move'] button[type='submit']").disabled;
    Should Be True    ${disabled}

Select Mode
    [Arguments]    ${mode}
    Select From List By Value    name:mode    ${mode}
    Wait Until Page Contains    Pelitilanne

Play Round
    [Arguments]    ${first}    ${second}=None
    Input Text    name:first_move    ${first}
    Run Keyword If    '${second}' != 'None'    Input Text    name:second_move    ${second}
    Click Button    Kirjaa siirrot

Expect Score Contains
    [Arguments]    ${text}
    Wait Until Page Contains    ${text}

*** Test Cases ***
AI Mode Records A Round
    Go To Home
    Select Mode    ai
    Play Round    k
    Expect Score Contains    Pelitilanne

Pvp Reaches Five Wins And Disables Moves
    Go To Home
    Select Mode    pvp
    FOR    ${i}    IN RANGE    5
        Play Round    k    s
    END
    Expect Score Contains    5 - 0
    Wait Until Page Contains    voitti
    Wait Until Keyword Succeeds    5s    0.5s    Check Move Button Disabled

Pvp Requires Second Move
    Go To Home
    Select Mode    pvp
    Play Round    k    
    Wait Until Page Contains    Toisen pelaajan siirto puuttuu
