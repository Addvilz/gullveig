---
title: Knowledge base
sidebar_label: Knowledge base
---

**Introduced in version:** 0.1.25

Gullveig ships with a built in documentation serving feature called "Knowledge base". It allows for your to serve
static documentation content directly from Gullveig web interface.

This feature is most useful to publish infrastructure and service operations related documentation.

![Gullveig](/img/screens/kb.png)

## Creating knowledge base

### Storage

Documentation files are stored on the host file system on the same server `gullveig-web` is installed on.

The default knowledge base data directory is located in `/var/lib/gullveig/kb/`. You can change the default path
using [web.conf](../configuration/web.conf#section-kb).

### Structure

Knowledge base is structured using Articles and Categories. An article is a markdown document that
contains knowledge base content. Categories are used to group related articles together.

### Categorization

Knowledge base allows for one level of nesting only - categories can not have sub-categories, etc. Articles without a 
category are placed in the knowledge base root and are shown independently from categories.

### Index article

The index article of the knowledge base root should be named either `index.md` or `readme.md`. Article categories does 
not have index articles.

### Display order

In root category, index article is always shown first, then other articles, sorted by their file name. Articles
in categories are sorted by their file name.

### Naming

Categories use their file system directory name as category title. Articles use the first level-1 heading
from the markdown document, using hash (`#`) as prefix. The heading must not be preceeded by any other
content, except for whitespace. If an article has no level-1 heading, the name of the file will be used,
without `.md` extension.

### Static files and attachments

Any static files you might want to link to can be placed directly in the knowledge base directory, and 
can be linked to from markdown files using image or anchor links. You can place static files anywhere within
the knowledge base root path. Files from outside of the knowledge base root path will not be resolved or
served. Where possible, use document-relative links to link to static files.

Access to the static files is protected using "download key" - a parameter attached to the public
URL of the file. **Anyone in possession of the file link with the key can download the file without any further
authentication to Gullveig web interface.**

### Updating knowledge base

Simply place the updated files in the knowledge base directory. You DO NOT need to restart Gullveig Web user
interface server for changes to take effect.

## Example directory and file structure

```text
/var/lib/gullveig/kb/

├── index.md
├── root-article1.md
├── root-article2.md
├── Category 1
│   ├─────────── article1.md
│   └─────────── article2.md
├── Category 2
│   ├─────────── article1.md
│   └─────────── article2.md
├── Category 3
│   ├─────────── article1.md
│   └─────────── article2.md
```
