#!/usr/bin/env python3
import argparse, hashlib
import numpy as np
from PIL import Image

# --- Key utilities ---
def key_to_byte(key_str: str) -> int:
    return hashlib.sha256(key_str.encode("utf-8")).digest()[0]

def rng_from_key(key_str: str) -> np.random.Generator:
    seed = int.from_bytes(hashlib.sha256(key_str.encode("utf-8")).digest(), "big") % (2**63 - 1)
    return np.random.default_rng(seed)

# --- Image I/O ---
def open_image(path):
    img = Image.open(path).convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    return arr

def save_image(arr, out_path):
    Image.fromarray(arr.astype(np.uint8), mode="RGB").save(out_path)

# --- Ops ---
def parse_ops(op_string):
    if not op_string: return []
    return [o.strip().lower() for o in op_string.split(",") if o.strip()]

def apply_ops(arr, keybyte, ops, keystr, mode):
    out = arr.copy()
    h, w, _ = out.shape
    flat = h * w

    rng = rng_from_key(keystr)
    perm = invperm = None

    for op in ops:
        if op == "xor":
            out = np.bitwise_xor(out, keybyte)

        elif op == "add":
            if mode == "encrypt":
                out = (out.astype(np.uint16) + keybyte) % 256
            else:
                out = (out.astype(np.uint16) - keybyte) % 256
            out = out.astype(np.uint8)

        elif op.startswith("channels="):
            spec = op.split("=", 1)[1]
            if spec == "rotate":
                order = (2, 0, 1)  # RGB->BRG
            elif spec.startswith("rgb->"):
                mapping = {"r": 0, "g": 1, "b": 2}
                order = tuple(mapping[ch] for ch in spec.split("->", 1)[1])
                if len(order) != 3:
                    raise ValueError("Bad channels order")
            else:
                raise ValueError("Use channels=rotate or channels=rgb->brg")

            # invert the permutation when decrypting
            if mode == "decrypt":
                inv = [0, 0, 0]
                for i, p in enumerate(order):
                    inv[p] = i
                order = tuple(inv)

            out = out[..., list(order)]

        elif op == "shuffle":
            if perm is None:
                perm = rng.permutation(flat)
                invperm = np.empty_like(perm)
                invperm[perm] = np.arange(flat)
            resh = out.reshape((-1, 3))
            if mode == "encrypt":
                resh = resh[perm]
            else:
                resh = resh[invperm]
            out = resh.reshape((h, w, 3))

        else:
            raise ValueError(f"Unknown op: {op}")
    return out

# --- CLI ---
def main():
    p = argparse.ArgumentParser(description="Simple pixel-manipulation image encryptor (educational).")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("-i","--input", required=True)
        sp.add_argument("-o","--output", required=True)
        sp.add_argument("-k","--key", required=True, help="Secret key/passphrase")
        sp.add_argument("--ops", default="xor,channels=rotate,shuffle",
                        help="Comma-separated: xor | add | channels=rotate | channels=rgb->brg | shuffle")

    pe = sub.add_parser("encrypt"); common(pe)
    pd = sub.add_parser("decrypt"); common(pd)

    args = p.parse_args()
    arr = open_image(args.input)
    keybyte = key_to_byte(args.key)
    ops = parse_ops(args.ops)

    if args.cmd == "encrypt":
        out = apply_ops(arr, keybyte, ops, args.key, mode="encrypt")
    else:
        out = apply_ops(arr, keybyte, ops, args.key, mode="decrypt")

    save_image(out, args.output)
    print(f"Done: {args.output}")

if __name__ == "__main__":
    main()
