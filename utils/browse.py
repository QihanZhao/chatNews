import importlib
import json
import os
import subprocess
import sys
import tempfile

import markdownify
import playwright
from playwright.async_api import async_playwright
from readabilipy import simple_json_from_html_string, simple_tree_from_html_string
from readabilipy.extractors import extract_title, extract_date
from readabilipy.simple_json import have_node, plain_content, extract_text_blocks_as_plain_text
from playwright.sync_api import sync_playwright, Page, ElementHandle

from utils.logger import logger


def simple_json_from_html_string(html, content_digests=False, node_indexes=False, use_readability=False):
    if use_readability and not have_node():
        print(
            "Warning: node executable not found, reverting to pure-Python mode. Install Node.js v10 or newer to use Readability.js.",
            file=sys.stderr)
        use_readability = False

    if use_readability:
        temp_dir = tempfile.gettempdir()
        # Write input HTML to temporary file so it is available to the node.js script
        html_path = os.path.join(temp_dir, "full.html")
        with open(html_path, 'w', encoding="utf-8") as f:
            f.write(html)

        # Call Mozilla's Readability.js Readability.parse() function via node, writing output to a temporary file
        article_json_path = os.path.join(temp_dir, "article.json")
        spec = importlib.util.find_spec('readabilipy')
        readabilipy_location = os.path.dirname(spec.origin)
        jsdir = os.path.join(readabilipy_location, 'javascript')
        old_cwd = os.getcwd()
        os.chdir(jsdir)
        subprocess.check_call(["node", "ExtractArticle.js", "-i", html_path, "-o", article_json_path])
        os.chdir(old_cwd)
        # Read output of call to Readability.parse() from JSON file and return as Python dictionary
        with open(article_json_path, encoding="utf-8") as f:
            input_json = json.loads(f.read())
    else:
        input_json = {
            "title": extract_title(html),
            "date": extract_date(html),
            "content": str(simple_tree_from_html_string(html))
        }

    # Only keep the subset of Readability.js fields we are using (and therefore testing for accuracy of extraction)
    # NB: Need to add tests for additional fields and include them when we look at packaging this wrapper up for PyPI
    # Initialise output article to include all fields with null values
    article_json = {
        "title": None,
        "byline": None,
        "date": None,
        "content": None,
        "plain_content": None,
        "plain_text": None
    }
    # Populate article fields from readability fields where present
    if input_json:
        if "title" in input_json and input_json["title"]:
            article_json["title"] = input_json["title"]
        if "byline" in input_json and input_json["byline"]:
            article_json["byline"] = input_json["byline"]
        if "date" in input_json and input_json["date"]:
            article_json["date"] = input_json["date"]
        if "content" in input_json and input_json["content"]:
            article_json["content"] = input_json["content"]
            article_json["plain_content"] = plain_content(article_json["content"], content_digests, node_indexes)
            article_json["plain_text"] = extract_text_blocks_as_plain_text(article_json["plain_content"])

    return article_json


def browse_web_page_in_reader_mode(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
        )
        page = browser.new_page()
        try:
            page.goto(url)
        except TimeoutError:
            logger.warning("Browse TimeoutError: %s Ignored", url)

        content = page.content()
        article_json = simple_json_from_html_string(content, use_readability=True)
        try:
            return markdownify.markdownify(article_json['content'])
        except KeyError:
            return article_json['content']

async def abrowse_web_page_in_reader_mode(url: str):
    logger.info("Browse: %s", url)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
        )
        page = await browser.new_page()
        try:
            await page.goto(url)
        except TimeoutError:
            logger.warning("Browse TimeoutError: %s Ignored", url)

        content = await page.content()
        article_json = simple_json_from_html_string(content, use_readability=True)
        try:
            return markdownify.markdownify(article_json['content'])
        except:
            return article_json['content']
