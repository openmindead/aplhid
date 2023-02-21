#!/usr/bin/env python3
#
#       alphid (apple hid)
#
#       Copyright 2013 Canonical Ltd.
#       Original author: Alberto Milone <alberto.milone@canonical.com>
#       Modified by: Vladimir Yerilov <openmindead@gmail.com>
#
#       Script to switch between 2 modes of Fn keys on Apple keyboards that make most sense. Mode strings are set in switch_mode function, adjust if necessary.
#
#       Usage:
#           place in /usr/local/bin
#           run alphid   media|func|auto|query
#           media: media keys as designed by Apple
#           func: standard Fn keys
#           auto: switches to another mode (there are only 2 anyway)
#           query: checks which version is currently active and writes
#                  "media", "func" or "unknown" to the
#                  standard output
#
#       Permission is hereby granted, free of charge, to any person
#       obtaining a copy of this software and associated documentation
#       files (the "Software"), to deal in the Software without
#       restriction, including without limitation the rights to use,
#       copy, modify, merge, publish, distribute, sublicense, and/or sell
#       copies of the Software, and to permit persons to whom the
#       Software is furnished to do so, subject to the following
#       conditions:
#
#       The above copyright notice and this permission notice shall be
#       included in all copies or substantial portions of the Software.
#
#       THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#       EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#       OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#       NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#       HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#       WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#       FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#       OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import subprocess
import itertools
import time

class Switcher(object):

    def __init__(self):
        self._hid_config_path = '/etc/modprobe.d/hid_apple.conf'

    def _get_mode(self):

        try:
            settings = open(self._hid_config_path, 'r')
        except:
            return 'unknown'

        config = settings.read().strip()
        if 'fnmode=1' in config:
            return 'media'
        elif 'fnmode=2' in config:
            return 'func'
        else:
            return 'disabled'

    def print_mode(self):
        mode = self._get_mode()
        if mode == 'unknown':
            return False

        print('%s' % mode)
        return True

    def _write_mode(self, hid_text):

        # Write the settings to the file
        settings = open(self._hid_config_path, 'w')
        settings.write(hid_text)
        settings.close()

    def switch_mode(self, mode):
        
        media_string = '''options hid_apple iso_layout=0 swap_opt_cmd=1 fnmode=1'''
        func_string = '''options hid_apple iso_layout=0 swap_opt_cmd=1 fnmode=2'''
        
        match mode:
            case 'media':
                hid_text = media_string
            case 'func':
                hid_text = func_string
            case 'auto':
                mode = self._get_mode()
                if mode == 'media':
                    mode = 'func'
                    hid_text = func_string
                else:
                    mode = 'media'
                    hid_text = media_string
            case _:
                mode = self._get_mode()
                if mode == 'media':
                    mode = 'func'
                    hid_text = func_string
                else:
                    mode = 'media'
                    hid_text = media_string
                
        sys.stdout.write('Info: selecting the %s mode\n' % (mode))
        self._write_mode(hid_text)
        initramfs = input("Rebuild initramfs to make %s mode permanent? (yes/no): " % (mode))
        if initramfs.lower() == 'yes' or initramfs.lower() == 'y':
            self._update_initramfs()
            print("You might need to run sbupdate or similar tool to refresh your unified kernel image")
        else:
            print("This mode is valid only until the next boot")
        
        subprocess.Popen(['rmmod', 'hid_apple'])
        time.sleep(1)
        subprocess.Popen(['modprobe', 'hid_apple'])

        return True
    
    def _update_initramfs(self):
        # Create spinner to give feed back on the
        # operation
        spinner = itertools.cycle ( ['-', '/', '|', '\\'])
        if os.path.isfile('/bin/dracut'):
            proc = subprocess.Popen(['dracut', '-f', '--regenerate-all'],stdout=subprocess.PIPE)
        elif os.path.isfile('/bin/mkinitcpio'):
            proc = subprocess.Popen(['mkinitcpio', '-P'],stdout=subprocess.PIPE)
        elif os.path.isfile('/bin/update-initramfs'):
            proc = subprocess.Popen(['update-initramfs', '-u', '-k', 'all'],stdout=subprocess.PIPE)
        else:
            print("Unsupported distro, please update initramfs manually")
        
        print('Updating the initramfs. Please wait for the operation to complete:')

        # Check if process is still running
        while proc.poll()==None:
            try:
                # Print the spinner
                sys.stdout.write(spinner.__next__())
                sys.stdout.flush()
                sys.stdout.write('\b')
                time.sleep(0.2)
            except BrokenPipeError:
                return False

        print('Done')

        # Print out the output
        output=proc.communicate()[0]

def check_root():
    if not os.geteuid() == 0:
        sys.stderr.write("This operation requires root privileges\n")
        exit(1)

def handle_query_error():
    sys.stderr.write("Error: no mode can be found\n")
    exit(1)

def usage():
    sys.stderr.write("Usage: %s media|func|auto\n" % (sys.argv[0]))

if __name__ == '__main__':
    try:
        arg = sys.argv[1]
    except IndexError:
        arg = None

    #if len(sys.argv[1:]) != 1:
    #    usage()
    #    exit(1)

    switcher = Switcher()

    if arg in ['media', 'func', 'auto', None]:
        check_root()
        switcher.switch_mode(arg)
    elif arg == 'query':
        if not switcher.print_mode():
            handle_query_error()
    else:
        usage()
        sys.exit(1)

    exit(0)
