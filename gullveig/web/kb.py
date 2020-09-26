import glob
import hashlib
import re
from os import DirEntry
from os import scandir, path
from re import Match
from typing import Optional


def get_file_md_title(file_path: str) -> Optional[str]:
    with open(file_path, 'r') as res:
        while True:
            line = res.readline()
            if not line:
                break

            # Skip empty
            if len(line.strip()) == 0:
                continue

            # First line that starts with # at the beginning of the file
            if line.startswith('# '):
                return line[2:].strip()

            # Break if not at the start of the file any more
            break

    return None


def entry_to_nav_item(root_path: str, item: DirEntry):
    rel_to_root = path.relpath(item.path, root_path)
    (path_name, _) = path.splitext(rel_to_root)
    (file_name, _) = path.splitext(item.name)
    md_title = get_file_md_title(item.path)

    if md_title is None:
        md_title = file_name

    return {
        'name': md_title,
        'uri': path_name
    }


def create_nav(root_path: str):
    nav = {
        'default': {
            'items': []
        },
        'categories': {}
    }

    scan_categories = []

    root_dir_contents = scandir(root_path)

    for item in root_dir_contents:
        if item.is_dir():
            scan_categories.append(item)
            continue
        if item.name.endswith('.md'):
            nav['default']['items'].append(entry_to_nav_item(root_path, item))

    for category in scan_categories:
        if category.name not in nav['categories']:
            nav['categories'][category.name] = {
                'name': category.name,  # TODO
                'items': []
            }
        category_dir_contents = scandir(category.path)

        for item in category_dir_contents:
            if item.is_file() and item.name.endswith('.md'):
                nav['categories'][category.name]['items'].append(entry_to_nav_item(root_path, item))

    nav['categories'] = sorted(list(nav['categories'].values()), key=lambda it: it['name'])
    nav['default']['items'] = sorted(nav['default']['items'], key=lambda it: it['uri'])

    i = 0
    for item in nav['default']['items']:
        if item['uri'] == 'index' or item['uri'].lower() == 'readme':
            del nav['default']['items'][i]
            nav['default']['items'].insert(0, item)
            break

        i = i + 1

    for category in nav['categories']:
        category['items'] = sorted(category['items'], key=lambda it: it['uri'])

    return nav


def preprocess(
        root_path: str,
        filename: str,
        text: str,
        public_path: str,
        static_path: str,
        secret: str
) -> str:
    def replace_each(a: Match):
        href = a.group(1)

        if href.startswith('//') or -1 != href.find('://'):
            return '](' + href + ')'

        url_hash = None
        url_query = None

        if -1 != href.find('#'):
            url_hash_i = href.index('#')
            url_hash = href[url_hash_i:]
            href = href[0:url_hash_i]

        if -1 != href.find('?'):
            url_query_i = href.index('?')
            url_query = href[url_query_i:]
            href = href[0:url_query_i]

        replacement = None
        candidate_file = path.abspath(path.join(path.dirname(filename), href))

        if path.isfile(candidate_file):
            replacement = path.relpath(candidate_file, root_path)

            if replacement.endswith('.md'):
                replacement = public_path + replacement[:-3]
            else:
                key_target = ('%s%s' % (secret, replacement)).encode('UTF-8')
                dl_key = hashlib.sha256(key_target).hexdigest()

                if url_query:
                    url_query = url_query + '&dl_key=' + dl_key
                else:
                    url_query = '?dl_key=' + dl_key

                replacement = static_path + replacement

            if url_query:
                replacement = replacement + url_query
            if url_hash:
                replacement = replacement + url_hash

        if replacement:
            return '](' + replacement + ')'

        return '](' + href + ')'

    link_link_match = r'\]\(\s*([^)]+)\s*\)'

    return re.sub(link_link_match, replace_each, text)


def read_article(root_path: str, article: str, secret):
    look_at = path.join(root_path, article + '.md')
    for filename in glob.iglob(root_path + '/**/*.md', recursive=True):
        if look_at == filename:
            with open(filename, 'r') as res:
                markdown = preprocess(
                    root_path,
                    filename,
                    res.read(),
                    '/kb/article/',
                    '/api/kb/file/',
                    secret
                )

                return {
                    'markdown': markdown
                }
    return None
