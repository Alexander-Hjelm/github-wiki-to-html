from enum import EnumMeta
from bs4 import BeautifulSoup
import getopt
import markdown
from markdown.extensions.toc import TocExtension
import os
import sys
import glob
from github import Github

# Config
gh_users_cache = {}

class github_user:
    def __init__(self, img_url, name, username, email):
        self.img_url = img_url
        self.name = name
        self.username = username
        self.email = email

def query_github_user(username):
    if username in gh_users_cache:
        return gh_users_cache[username]
    token = os.getenv('GITHUB_TOKEN', gh_token)
    g = Github(token)
    user = g.get_user(username)
    gh_user = github_user(user.avatar_url, user.name, user.login, user.email)
    gh_users_cache[username] = gh_user
    return gh_user

def append_codeowners(wiki_path, file_path):
    with open(wiki_path+"CODEOWNERS", 'r') as f:
        text = f.readlines()
    # Find most specific file path match
    d = {}
    for line in text:
        if(line == '' or line.startswith('#') or line.startswith('\n')):
            continue
        selector = line.split(' ')[0]
        users = []
        for word in line.split(' '):
            if word.startswith('@'):
                users.append(word[1:].rstrip())
                d[selector] = users
    longest_match = 0
    codeowners_out = None
    for k in d:
        matches = glob.glob(wiki_path+k)
        for m in matches:
            m_formatted = m.replace("//", '/')
            if file_path.startswith(m_formatted) and len(m_formatted) > longest_match:
                longest_match = len(m_formatted)
                codeowners_out = d[k]
    
    # Generate div
    div = BeautifulSoup("<div></div>", 'html.parser').div
    div['id']="codeowners"

    for user in codeowners_out:
        p = BeautifulSoup("<p></p>", 'html.parser').p
        a = BeautifulSoup("<a></a>", 'html.parser').a
        gh_user = query_github_user(user)
        a["href"] = "https://github.com/{}".format(gh_user.username)
        a.append(gh_user.name+" (" + gh_user.username +")")
        if gh_user.email != None:
            a.append("- "+gh_user.email)
        p.append(a)
        div.append(p)
        img = BeautifulSoup("<img></img>", 'html.parser').img
        img["src"] = gh_user.img_url
        img["class"] = "gh_avatar"
        div.append(img)

    return div

def make_dir(folder_path):
    dir = folder_path.split("/")
    dir.pop()
    dir = "/".join(map(str, dir))
    os.makedirs(dir, exist_ok=True)

def append_toc(text):
    return ("[TOC]\n"+text).replace("[[_TOC_]]", "")

def append_head_links(soup, webroot, stylesheet_path, script_path):
    stylesheet_link_tag = BeautifulSoup('<link rel="stylesheet" href="{0}"/>'.format(webroot+stylesheet_path), "html.parser")
    script_link_tag = BeautifulSoup('<script src="{0}"/>'.format(webroot+script_path), "html.parser")
    soup.head.insert(0, stylesheet_link_tag)
    soup.head.insert(0, script_link_tag)

def append_attachments_ref(soup, webroot, attachments_path):
    for a in soup.findAll('img'):
        a['src'] = a['src'].replace('.attachments/', webroot+attachments_path+'/')
    for a in soup.findAll('a'):
        a['href'] = a['href'].replace('.attachments/', webroot+attachments_path+'/')

def build_index_html(index, ul, level, webroot):
    for k in index.keys():
        li = BeautifulSoup("<li class=element_index_{0}></li>".format(level), 'html.parser').li
        li['id'] = "index_element"
        a = BeautifulSoup("<a></a>", 'html.parser').a
        a['href'] = webroot + k + ".html"
        file_name = k
        if(k.endswith('/')):
            file_name = k[:-1]
        a.string = file_name.split('/')[-1]
        li.append(a)
        ul.append(li)
        build_index_html(index[k], ul, level+1, webroot)

def append_search_and_index(input_wiki_path, webroot):
    #Generate index
    index = {}
    for root, dirs, files in os.walk(input_wiki_path, topdown=False):
        for name in files:
            if(name.endswith(".md")):
                path = (os.path.join(root, name)+'/').replace(input_wiki_path, "")
                current_level = index
                i = 0
                while '/' in path[i:]:
                    i = path.find('/', i)+1
                    part = path[:i]
                    part = part.replace(".md/", '')
                    if part.endswith('/'):
                        part = part[:-1]
                    if not part in current_level.keys():
                        current_level[part] = {}
                    current_level = current_level[part]
    div = BeautifulSoup("<div></div>", 'html.parser').div
    ul = BeautifulSoup("<ul></ul>", 'html.parser')
    input = BeautifulSoup('<input type="text" oninput="search(this.value);"></input>', 'html.parser')

    div['id']="index"
    build_index_html(index, ul, 0, webroot)
    div.append(input)
    div.append(ul)
    return div
    
def make_doc_from_body(body):
    return "<html><head><title>Title</title></head><body><table><tr><td id='main_content_td' class='content_td'><div id=main_content>{0}</td><td id='sidebar_td' class='content_td'></td></tr></table></div></body></html>".format(body)

def convert_and_save_file(src_path, target_path, input_wiki_path, stylesheet_path, script_path, attachments_path, webroot):
    with open(src_path, 'r') as f:
        text = f.read()

    text = append_toc(text)

    body = markdown.markdown(text, extensions=[TocExtension(baselevel=2, title='Contents')])
    html = make_doc_from_body(body)
    soup = BeautifulSoup(html, "html.parser")

    append_head_links(soup, webroot, stylesheet_path, script_path)
    append_attachments_ref(soup, webroot, attachments_path)
    codeowners_div = append_codeowners(input_wiki_path, src_path)
    search_index_div = append_search_and_index(input_wiki_path, webroot)

    sidebar_td = soup.find("td", {"id": "sidebar_td"})
    sidebar_td.append(codeowners_div)
    sidebar_td.append(search_index_div)
    make_dir(target_path)
    with open(target_path, 'w') as f:
        f.write(soup.prettify())

### Argument parsing

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, 'w:s:i:r:j:p:')

input_wiki_path = None
stylesheet_path = None
script_path = None
attachments_path = None
webroot = None
gh_token = None

for k, v in opts:
    if k == "-w":
        input_wiki_path = v
    if k == "-s":
        stylesheet_path = v
    if k == "-j":
        script_path = v
    if k == "-i":
        attachments_path = v
    if k == "-r":
        webroot = v
    if k == "-p":
        gh_tkoen = v


if not input_wiki_path:
    print("Specify argument: -w for path to input wiki")
    exit()
if not webroot:
    print("Specify argument: -r for webroot")
    exit()

### Convert markdown to html, file by file

written_index_file = False

for root, dirs, files in os.walk(input_wiki_path, topdown=False):
   for name in files:
       if(name.endswith(".md")):
            source_path = os.path.join(root, name)
            if not written_index_file:
                target_path = "{0}index.html".format(webroot)
                written_index_file = True
            else:
                target_path = "{0}{1}.html".format(webroot, source_path.replace(input_wiki_path, '', 1).replace(".md", '', 1))
            print(target_path)
            convert_and_save_file(source_path, target_path, input_wiki_path, stylesheet_path, script_path, attachments_path, webroot)
