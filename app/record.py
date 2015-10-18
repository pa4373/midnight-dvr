#!/usr/bin/env python
import subprocess
import urllib
import re
import datetime
import os
import shutil

import config

def get_hls_playlist_url():
    s = urllib.urlopen(config.HICHANNEL_URL).read()
    p = re.compile("var\surl\s=\s'(\S+)';")
    m = p.search(s)
    if m:
        url = m.group(1).replace('\/', '/')
        return url
    else:
        raise Exception("Couldn't parse HLS URL.")

def record(hls_playlist_url, out_filename, duration):
    _cmd = ['ffmpeg', '-re', '-i', hls_playlist_url, '-c', 'copy', '-bsf:a',
            'aac_adtstoasc', '-t', str(duration), out_filename]
    subprocess.call(_cmd)

def mega_put(out_filename, remote_dst_url):
    _cmd = ['megaput', '-u', config.MEGA_USERNAME, '-p', config.MEGA_PASSWD,
            '--path={}'.format(remote_dst_url), out_filename]
    subprocess.call(_cmd)

def mv_outfile(out_filename, local_dst_url):
    shutil.move(out_filename, local_dst_url)

if __name__ == '__main__':
    url = get_hls_playlist_url()
    out_filename = '{}.mp4'.format(datetime.datetime.now()
                                           .strftime("%B-%d-%Y"))
    record(url, out_filename, config.DURATION)
    mega_put(out_filename, config.MEGA_DST_URL + out_filename)
    mv_outfile(out_filename, config.LOCAL_DST_PATH)
