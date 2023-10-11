# Firefox configuration required:
# about:config - browser.bookmarks.autoExportHTML - true

# CHANGE THE FOLOWING:
ftp_server = '127.0.0.1'
ftp_login = 'guest'
ftp_pass = '123'
ftp_subdir = 'site_data'

# for Python get Integrated Development and Learning Environment
# sudo apt install idle3

# ~/.local/share/applications/Firefox_backup.desktop
# [Desktop Entry]
# Type=Application
# Version=1.1
# Name=Firefox backup
# Comment=Backup bookmarks and launch Firerox
# Path=/home/YOUR_USER_NAME/firefox_backup
# Exec=python3 /home/YOUR_USER_NAME/firefox_backup/f_backup.py
# Icon=firefox
# Terminal=true
# Categories=Network;

import subprocess
import os
import filecmp
from datetime import datetime
import locale
import shutil
import re
import ftplib
import time

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# https://stackoverflow.com/questions/6011235/run-a-program-from-python-and-have-it-continue-to-run-after-the-script-is-kille
subprocess.Popen(['firefox'], preexec_fn=os.setpgrp)
root = os.path.join(os.path.expanduser('~'), 'snap/firefox/common/.mozilla/firefox/') # ubuntu
for item in os.listdir(root):
  profile_dir = os.path.join(root, item)
  if not os.path.isdir(profile_dir):
    continue
  found_bookmarks = os.path.join(profile_dir, 'bookmarks.html')
  if not os.path.isfile(found_bookmarks):
    continue
  print(found_bookmarks)
  
  if os.path.isfile('interim_old.html'):
    os.remove('interim_old.html')
  if os.path.isfile('interim.html'):
    shutil.copyfile('interim.html', 'interim_old.html')
    os.remove('interim.html')
  
  print('converting bookmarks to clean HTML')  
  in_file  = open(found_bookmarks, "r")
  out_file = open("interim.html", "w")
  for line in in_file:
    if '<meta http-equiv="Content-Security-Policy"' in line:
      continue
    if '</meta>' in line:
      continue
    if '<!DOCTYPE NETSCAPE-Bookmark-file-1>' in line:
      out_file.write('<!DOCTYPE html>\n<html>\n<head>\n')
      continue
    if '<H1>Bookmarks Menu</H1>' in line:
      out_file.write('<style>UL {font-family: sans-serif;}</style>\n')
      out_file.write('</head>\n\n<body>\n')
    line = re.sub('(<A HREF=".*?").*?(>.*?</A>)', '\\1\\2', line)
    line = re.sub('<(/?)DL>(<p>)?', '<\\1UL>', line)
    line = line.replace('<DT>', '<LI>')
    line = re.sub('<(/?)H3.*?>', '<\\1b>', line)
    out_file.write(line)
  out_file.write('</body>\n</html>')
  in_file.close()
  out_file.close()

  if os.path.isfile('interim_old.html'):
    if filecmp.cmp('interim.html', 'interim_old.html'):
      print(color.RED + 'no changes in bookmarks, so do abort' + color.END)
      break
  print(color.GREEN + 'not exist or differ, so do backup' + color.END)

  # final replace to add current date to the heading
  now = datetime.now()
  locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
  ts = now.strftime('%A, ').title() + now.strftime('%-d %B %Yг.')
  in_file  = open("interim.html", "r")
  out_file = open("index.html", "w")
  for line in in_file:
    if '<H1>Bookmarks Menu</H1>' in line:
      line = line.replace('Bookmarks Menu', ts)
    out_file.write(line)
  in_file.close()
  out_file.close()
  
  print('uploading bookmarks to FTP')
  ftp = ftplib.FTP(ftp_server, ftp_login, ftp_pass)
  ftp.cwd(ftp_subdir)
  file = open('index.html','rb')
  ftp.storbinary('STOR index.html', file)
  file.close()
  ftp.quit()
print('waiting 5 seconds')
time.sleep(5)
