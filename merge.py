import sys
import os
import shutil
from pathlib import Path

# clean out the current pages
shutil.rmtree('Pages')

# copy over from export
shutil.copytree("export/Pages", "Pages")

# delete export
shutil.rmtree('export')

# return all good
sys.stdout.write('completed')