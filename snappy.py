#!/usr/bin/env python3
"""Snappy-like fast compression (LZ77 variant, speed over ratio)."""
import sys

def compress(data):
    if isinstance(data,str): data=data.encode()
    result=bytearray(); result.extend(len(data).to_bytes(4,'little'))
    i=0; window={}
    while i<len(data):
        # Try to find a match in recent window
        best_off=best_len=0
        if i+3<=len(data):
            key=data[i:i+3]
            if key in window:
                j=window[key]
                if i-j<65536:
                    length=0
                    while i+length<len(data) and data[j+length]==data[i+length] and length<64:
                        length+=1
                    if length>=4: best_off=i-j; best_len=length
            window[data[i:i+3]]=i
        if best_len>=4:
            result.append(0x80|((best_len-1)&0x3f))
            result.extend(best_off.to_bytes(2,'little'))
            i+=best_len
        else:
            result.append(data[i]); i+=1
    return bytes(result)

def decompress(data):
    orig_len=int.from_bytes(data[:4],'little')
    result=bytearray(); i=4
    while i<len(data):
        b=data[i]; i+=1
        if b&0x80:
            length=(b&0x3f)+1
            offset=int.from_bytes(data[i:i+2],'little'); i+=2
            start=len(result)-offset
            for j in range(length): result.append(result[start+j])
        else:
            result.append(b)
    return bytes(result)

if __name__ == "__main__":
    texts=["Hello World! "*50, "AAAA"*200, "The quick brown fox "*30]
    for text in texts:
        data=text.encode()
        comp=compress(data); decomp=decompress(comp)
        print(f"  {len(data):5d}B -> {len(comp):5d}B ({len(comp)/len(data)*100:.0f}%) match={data==decomp}")
