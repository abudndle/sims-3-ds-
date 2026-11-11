#!/usr/bin/env python3
"""Calibrate relative camera rates from paired, measured gameplay observations.

CSV columns: game,axis,duration_seconds,delta
axis: pan, yaw, zoom; game: ds, pets3ds.
Delta must be measured in the SAME world-space or screen-space units for each axis.
Do not estimate motion from camera-start presets or menu string tables.
"""
import argparse,csv,json,math,statistics,sys
from collections import defaultdict
AXES=('pan','yaw','zoom')
def analyze(rows):
    values=defaultdict(list)
    for ix,r in enumerate(rows,2):
        game=r['game'].strip().lower();axis=r['axis'].strip().lower()
        if game not in ('ds','pets3ds') or axis not in AXES:raise ValueError(f'line {ix}: invalid game or axis')
        dt=float(r['duration_seconds']);delta=float(r['delta'])
        if not (math.isfinite(dt) and dt>0 and math.isfinite(delta)):raise ValueError(f'line {ix}: invalid time/delta')
        values[(game,axis)].append(abs(delta)/dt)
    result={}
    for axis in AXES:
        ds=values.get(('ds',axis),[]);pets=values.get(('pets3ds',axis),[])
        if not ds or not pets:raise ValueError(f'missing paired DS and Pets 3DS data for {axis}')
        a=statistics.median(ds);b=statistics.median(pets)
        if a==0:raise ValueError(f'zero DS baseline for {axis}')
        result[axis]={'ds_units_per_second':a,'pets3ds_units_per_second':b,
                      'ds_to_pets_multiplier':b/a,'samples_ds':len(ds),'samples_pets3ds':len(pets)}
    return result

def write_header(result,path):
    with open(path,'w') as f:
        f.write('/* Derived from real matched gameplay measurements, not fixed ROM constants. */\n#ifndef SIMS3_PETS_CALIBRATION_H\n#define SIMS3_PETS_CALIBRATION_H\n')
        for axis in AXES:
            # Q16 avoids truncated fractional multipliers.
            n=round(result[axis]['ds_to_pets_multiplier']*65536)
            if n<=0 or n>0xffffffff:raise ValueError(f'{axis} multiplier outside Q16 range')
            f.write(f'#define PETS3DS_{axis.upper()}_MULTIPLIER_Q16 {n}u\n')
        f.write('#endif\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('samples_csv');p.add_argument('--report',required=True);p.add_argument('--header',required=True)
    args=p.parse_args()
    with open(args.samples_csv,newline='') as f:r=analyze(csv.DictReader(f))
    with open(args.report,'w') as f:json.dump(r,f,indent=2)
    write_header(r,args.header)
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
