#!/bin/bash
docker run --rm -v /`pwd`://app -w //app omniac-setup python s/dec.py s/.secrets s/.config.encrypted s/.decrypted-config.json
