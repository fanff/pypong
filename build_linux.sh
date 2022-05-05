#!/bin/bash

rm -rf dist

pyinstaller main.py --onefile --noconsole

cp -r assets dist/

rm -rf nf_pong_linux.zip
zip -r fanf_pong_linux.zip  dist
