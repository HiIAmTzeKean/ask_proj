# ask_proj
Aikido Shinjukai System Add On

Flask based model web application. Intent is to give easy infomation access to instructors via a web app to allow thme to function remotely and 
to provide a platform for parents to keep track of their child's progess. The application is currently hosted on https://ask-proj.herokuapp.com.
If you have any enquires please drop me an email @ ngtzekean600@gmail.com

Requirements
-------------------
- Python 3.x installation

Package Management
-------------------
This repository uses [pip-tools](https://github.com/jazzband/pip-tools) to synchronise python packages across computers. To add a new Python Package:

1. Insert the name of the python package in ``requirements.in``.
2. Then run `pip-compile` so that ``requirements.txt`` can be updated.
3. Finally, run `pip-sync` to download the new packages.
