#!/usr/bin/env python3
"""Apply a BPS patch. Verifies both input and output CRC32. Standard library only."""
import sys, struct, zlib
from pathlib import Path

def apply_bps(src, patch):
    if patch[:4] != b"BPS1": raise ValueError("Not a BPS patch")
    if zlib.crc32(patch[:-4]) != struct.unpack_from("<I",patch,len(patch)-4)[0]: raise ValueError("BPS integrity check failed")
    p=4
    def num():
        nonlocal p
        data=0;shift=1
        while True:
            x=patch[p];p+=1
            data+=(x&127)*shift
            if x&128:return data
            shift <<=7;data+=shift
    src_size=num();tgt_size=num();meta=num();p+=meta
    if len(src)!=src_size:raise ValueError(f"Incorrect ROM size: expected {src_size}, got {len(src)}")
    src_crc,tgt_crc=struct.unpack_from('<II',patch,len(patch)-12)
    if zlib.crc32(src)!=src_crc:raise ValueError("Incorrect source ROM (CRC32 mismatch). Requires the exact USA VS3E Rev 0 dump.")
    target=bytearray();src_rel=tgt_rel=0
    def signed(n):return -(n>>1) if n&1 else (n>>1)
    while len(target)<tgt_size:
        code=num();action=code&3;length=(code>>2)+1
        if action==0:
            a=len(target);target+=src[a:a+length]
        elif action==1:
            target+=patch[p:p+length];p+=length
        elif action==2:
            src_rel+=signed(num());target+=src[src_rel:src_rel+length];src_rel+=length
        else:
            tgt_rel+=signed(num())
            for _ in range(length):target.append(target[tgt_rel]);tgt_rel+=1
    if len(target)!=tgt_size or zlib.crc32(target)!=tgt_crc:raise ValueError("Patched ROM verification failed")
    return bytes(target)

if __name__=='__main__':
    if len(sys.argv)!=4:
        print('Usage: python3 apply_bps.py original.nds Sims3_DS_Japanese_Title_Logo_v1.bps patched.nds');sys.exit(2)
    output=apply_bps(Path(sys.argv[1]).read_bytes(),Path(sys.argv[2]).read_bytes())
    Path(sys.argv[3]).write_bytes(output)
    print('Patch applied and CRC32 verified:',sys.argv[3])
