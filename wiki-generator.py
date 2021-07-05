import getopt
import markdown
import sys

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, 'w:s:i:r:')

print(f'Options Tuple is {opts}')

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