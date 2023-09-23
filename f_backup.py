# Firefox configuration required:
# about:config - browser.bookmarks.autoExportHTML - true

# CHANGE THE FOLOWING:
ftp_server = '127.0.0.1'
ftp_login = 'user'
ftp_pass = '123'
ftp_subdir = 'pub'

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
  if os.path.isfile('bookmarks.html'): # local copy for track of changes
    if filecmp.cmp(found_bookmarks, 'bookmarks.html'):
      print('no changes in bookmarks, so do abort')
      break
  print('not exist or differ, so do backup')
  
  print('converting bookmarks to clean HTML')
  now = datetime.now() # current date and time
  locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
  ts = now.strftime('%A, ').title() + now.strftime('%-d %B %Yг.')

  shutil.copyfile(found_bookmarks, 'bookmarks.html')
  in_file  = open("bookmarks.html", "r")
  out_file = open("index.html", "w")

  out_file.write('<html>\n<head>\n')
  for line in in_file:
    if '<meta http-equiv="Content-Security-Policy"' in line:
      continue
    if '</meta>' in line:
      continue
    if '<H1>Bookmarks Menu</H1>' in line:
      line = line.replace('Bookmarks Menu', ts)
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
  
  print('uploading bookmarks to FTP')
  ftp = ftplib.FTP(ftp_server, ftp_login, ftp_pass)
  ftp.cwd(ftp_subdir)
  file = open('index.html','rb')
  ftp.storbinary('STOR index.html', file)
  file.close()
  ftp.quit()
print('waiting 5 seconds')
time.sleep(5)

