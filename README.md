# Image Encryptor (Educational)

A simple Python CLI tool that encrypts and decrypts images using reversible pixel-based operations.
This project demonstrates basic cybersecurity concepts such as XOR masking, channel manipulation, and deterministic pixel shuffling.

This tool is designed for learning purposes only and is not meant for serious cryptographic protection.

## Features
- Pixel-wise XOR encryption using a key
- ADD (mod 256) reversible operation
- Color channel rotation or custom reordering (RGB → BRG)
- Key-based deterministic pixel shuffle (fully reversible)
- Simple command-line interface
- Supports PNG and JPG images

## Setup

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Usage

Encrypt an image:
./imgcrypt.py encrypt -i input.png -o secret.png -k "MyKey" --ops "xor,channels=rotate,shuffle"

Decrypt an image:
./imgcrypt.py decrypt -i secret.png -o restored.png -k "MyKey" --ops "xor,channels=rotate,shuffle"

Important:
- Use the same key for decryption
- Use the exact same --ops list for decryption

## Notes
- Output format is based on the extension you specify in -o.
- This project is for educational cybersecurity practice.
- Pixel shuffle is deterministic: same key → same permutation.

## License
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files…

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND.
