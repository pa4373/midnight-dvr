#!/usr/bin/env python
import time
import base64
import hashlib
import urllib
import urlparse
import urllib2
import subprocess
from collections import OrderedDict

def gen_token(path, timestamp, ip_addr, token_ord):
    const_str = 'radio@himediaservice#t'
    cat_str = path + str(timestamp) + ip_addr + const_str + str(token_ord)
    hashed = hashlib.md5(unicode(cat_str)).digest()
    b64_md5hash = base64.b64encode(hashed)
    return b64_md5hash.replace('+', '-').replace('/', '_').replace('=', '')

def build_url():
    base_url = 'http://radio-hichannel.cdn.hinet.net/'
    ip_addr = urllib2.urlopen('http://ipinfo.io/ip').read().rstrip() # Get IP
    path = '/live/pool/hich-ra000009/ra-hls/'
    expire1 = int(time.time())
    expire2 = expire1 + (60 * 60 * 8)
    params = OrderedDict([
        ('token1', gen_token(path, expire1, ip_addr, 1)),
        ('token2', gen_token(path, expire2, ip_addr, 2)),
        ('expire1', expire1),
        ('expire2', expire2)
    ])
    params_str = urllib.urlencode(params)
    return urlparse.urljoin(base_url, path + 'index.m3u8') + '?' + params_str

def check_url_alive(url):
    try:                        return urllib2.urlopen(url) and True
    except urllib2.HTTPError:   return False

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
    is_alive = None
    while is_alive != True:
        url = build_url()
        is_alive = check_url_alive(url)

    out_filename = '{}.mp4'.format(datetime.datetime.now()
                                           .strftime("%B-%d-%Y"))
    record(url, out_filename, config.DURATION)
    mega_put(out_filename, config.MEGA_DST_URL + out_filename)
    mv_outfile(out_filename, config.LOCAL_DST_PATH)
