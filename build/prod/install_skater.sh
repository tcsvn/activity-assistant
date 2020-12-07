#!/bin/bash
git clone https://github.com/oracle/Skater
cd Skater
python3.7 $(which pip3) install -U .
cp -r skater /usr/local/lib/python3.7/site-packages/skater
cd ..
rm -rf Skater
