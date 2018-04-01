#!/bin/bash
docker run --rm -v /`pwd`://app -w //app omniac-setup python s/enc.py s/.secrets s/.config.json s/.config.encrypted
