# QA Functional Automation beans

## Pre-requisites
 - Python 3
 - Pip

## Purpose
Testing framework for beans feature (to expand ;)

## Requirements

### Using chrome driver
[Chromedriver](https://chromedriver.chromium.org/downloads) file is required to execute UI selenium tests.
Unzip downloaded file and place it in folder listed in system path.

### Using Browserstack
[BrowserStackLocal](https://www.browserstack.com/local-testing) file is required to execute tests on company's private network.
Unzip downloaded file and place it in folder listed in system path.

[Available environments](https://www.browserstack.com/list-of-browsers-and-platforms/live)

[Python desired capabilities](https://www.browserstack.com/automate/python)

### PIP ini file
Some of the common code is located on magic_repo storage. 
For python to know where it is pip.ini file must be populated with
additional entry:

```[global]
trusted-host = pypi.python.org
               pypi.org
               files.pythonhosted.org
```

File location (must be created if does not exists): %APPDATA%\pip

### Usage

Example flags:
   
    -c stands for config - this is a must
    -r is only specified if you want an email report to be generated and mailed, this is optional

    --luf - executes in a loop until first failure
    --browser_stack - executes test on browser stack
    --headless - executes tests in headless mode without spawning browser

    -class <class names>- is only used if you want to run a class of tests. This uses partial string matching. All matched classes are executed.
    -t <test_ids> - is only used if you want to run a specific test(s), separate test ids with a blank space

### Other help