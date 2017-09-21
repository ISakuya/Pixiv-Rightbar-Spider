#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
import extention to add set proxy(if you need)
'''
from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def create_modheaders_plugin(plugin_path=None, remove_headers=None, add_or_modify_headers=None):
    """Create modheaders extension

    kwargs:
        plugin_path (str): absolute plugin path
        remove_headers (list): headers name to remove
        add_or_modify_headers (dict): ie. {"Header-Name": "Header Value"}

    return str -> plugin path
    """
    import string
    import zipfile

    if plugin_path is None:
        plugin_path = '/tmp/vimm_chrome_modheaders_plugin.zip'

    if remove_headers is None:
        remove_headers = []

    if add_or_modify_headers is None:
        add_or_modify_headers = {}        

    assert isinstance(remove_headers, list), "remove_headers must be a list"
    assert isinstance(add_or_modify_headers, dict), "add_or_modify_headers must be dict"

    # only keeping the unique headers key in remove_headers list
    remove_headers = list(set(remove_headers))


    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome HeaderModV",
        "permissions": [
            "webRequest",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
    """
    function callbackFn(details) {
        var remove_headers = ${remove_headers};
        var add_or_modify_headers = ${add_or_modify_headers};

        function inarray(arr, obj) {
            return (arr.indexOf(obj) != -1);
        }

        // remove headers
        for (var i = 0; i < details.requestHeaders.length; ++i) {
            if (inarray(remove_headers, details.requestHeaders[i].name)) {
                details.requestHeaders.splice(i, 1);
                var index = remove_headers.indexOf(5);
                remove_headers.splice(index, 1);
            }
            if (!remove_headers.length) break;
        }

        // modify headers
        for (var i = 0; i < details.requestHeaders.length; ++i) {
            if (add_or_modify_headers.hasOwnProperty(details.requestHeaders[i].name)) {
                details.requestHeaders[i].value = add_or_modify_headers[details.requestHeaders[i].name];
                delete add_or_modify_headers[details.requestHeaders[i].name];
            }
        }

        // add modify
        for (var prop in add_or_modify_headers) {
            details.requestHeaders.push(
                {name: prop, value: add_or_modify_headers[prop]}
            );
        }

        return {requestHeaders: details.requestHeaders};
    }

    chrome.webRequest.onBeforeSendHeaders.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking', 'requestHeaders']
    );
    """
    ).substitute(
        remove_headers=remove_headers,
        add_or_modify_headers=add_or_modify_headers,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path
Cookie = ''
mod_headers_plugin_path = create_modheaders_plugin(
    remove_headers=[],
    add_or_modify_headers={
        "User-Agent": 'Chrome driver',
        'X-Vimm': 'Vimmaniac Pvt. Ltd.',
        'refer': 'http://www.pixiv.net',
        'Cookie': Cookie,
    },
)


co = Options()
co.add_argument("--start-maximized")
co.add_extension(mod_headers_plugin_path)
#co.add_extension("/SwitchyOmega.crx")


"""from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 600))
display.start()"""


"""driver = webdriver.Chrome(chrome_options=co)
driver.get("http://httpbin.org/headers")
try:
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
except:
    import sys
    sys.exit("Can't fetech desired content")
else:
    print(driver.page_source)
finally:
    driver.quit()"""