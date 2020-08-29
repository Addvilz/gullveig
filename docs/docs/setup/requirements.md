---
title: Gullveig environment requirements
sidebar_label: Requirements
---

Gullveig installation requires:

- Python 3.5+
- PIP for Python 3 (pip3)
- Python Setuptools
- Python development headers
- GCC or compatible compiler

These dependencies are shared between all Gullveig components - server, agents and web user interface.

GCC and Python development headers are required to build native code for reporting modules, such as `psutil`.
Python setuptools is used internally by Gullveig to lookup optional dependencies.

For APT based systems, dependencies can be obtained using a command similar to this:

```bash
apt install python3 \
    python3-pip \ 
    python3-setuptools \
    python3-dev \
    gcc
```

For systems using DNF, dependencies can be obtained using a command similar to this:

```bash
dnf install python3 \
    python3-pip \
    python3-setuptools \
    python3-devel \
    gcc
```

Before running above commands, refer to the manual of your particular operating system and / or package management tool
to determine the best way to install these dependencies.
