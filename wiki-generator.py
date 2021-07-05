from bs4 import BeautifulSoup
import getopt
import markdown
from markdown.extensions.toc import TocExtension
import os
import sys

def make_dir(folder_path):
    dir = folder_path.split("/")
    dir.pop()
    dir = "/".join(map(str, dir))
    os.makedirs(dir, exist_ok=True)

def append_toc(text):
    return "[TOC]\n"+text

def append_stylesheet(soup):
    stylesheet_file = stylesheet_path.split("/").pop()
    stylesheet_link_tag = BeautifulSoup('<link rel="stylesheet" href="{0}"/>'.format(webroot+stylesheet_file), "html.parser")
    soup.head.insert(0, stylesheet_link_tag)

def append_images_ref(text):
    a=1/0
    
def append_search_and_index(text):
    a=1/0

def make_doc_from_body(body):
    return "<html><head><title>Title</title></head><body>{0}</body></html>".format(body)

def convert_and_save_file(src_path, target_path):
    with open(src_path, 'r') as f:
        text = f.read()

    text = append_toc(text)

    body = markdown.markdown(text, extensions=[TocExtension(baselevel=2, title='Contents')])
    html = make_doc_from_body(body)
    soup = BeautifulSoup(html, "html.parser")

    append_stylesheet(soup)
    append_images_ref(soup)
    append_search_and_index(soup)

    make_dir(target_path)

    with open(target_path, 'w') as f:
        f.write(soup.prettify())

### Argument parsing

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, 'w:s:i:r:')

input_wiki_path = None
stylesheet_path = None
images_path = None
webroot = None

for k, v in opts:
    if k == "-w":
        input_wiki_path = v
    if k == "-s":
        stylesheet_path = v
    if k == "-i":
        images_path = v
    if k == "-r":
        webroot = v

if not input_wiki_path:
    print("Specify argument: -w for path to input wiki")
    exit()
if not webroot:
    print("Specify argument: -r for webroot")
    exit()

### Convert markdown to html, file by file

for root, dirs, files in os.walk(input_wiki_path, topdown=False):
   for name in files:
       if(name.endswith(".md")):
            source_path = os.path.join(root, name)
            target_path = "{0}{1}.html".format(webroot, source_path.replace(input_wiki_path, '', 1).replace(".md", '', 1))
            convert_and_save_file(source_path, target_path)
