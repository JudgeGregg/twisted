#!/usr/bin/env python

# Twisted, the Framework of Your Internet
# Copyright (C) 2001 Matthew W. Lefkowitz
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys
import os.path
from distutils import sysconfig
import twisted.copyright
from twisted.python.runtime import platform
from twisted.python.shortcut import Shortcut
try:
    import win32api
    import win32con
except ImportError:
    pass # a warning will be generated at runtime

if 'file_created' not in dir(__builtins__):
    def noop(foo):
        pass
    file_created=directory_created=noop


def getProgramsMenuPath():
    """getProgramsMenuPath() -> String|None
    @return the filesystem location of the common Start Menu.
    """
    if not platform.isWinNT():
        return "C:\\Windows\\Start Menu\\Programs"
    keyname='SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders'
    hShellFolders=win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, 
                                        keyname, 0, win32con.KEY_READ)
    return win32api.RegQueryValueEx(hShellFolders, 'Common Programs')[0]

def getShell32DLLPath():
    """getShell32DLLPath() -> String|None
    @return the filesystem location of shell32.dll
    """
    if platform.isWinNT():
        return os.path.join(os.getenv("SYSTEMROOT"), 
                            "system32", "shell32.dll")
    else:
        return "C:\\windows\\system\\shell32.dll"

def getBatFilename():
    """getBatFilename() -> String|None
    @return the location of the environment setup script.
    """
    python_dir=sysconfig.get_config_var("prefix")
    return os.path.join(python_dir,
                              'lib', 'site-packages', 'twisted', 'twistenv.bat')

def run():
    if sys.argv[1] == "-install": 
        whocares=install()
    elif sys.argv[1] == "-remove": 
        remove()
    else: 
        sys.stderr.write("This script is meant to be run by the Windows installer, not directly from the command line.\n")

def remove():
    pass

def install():
    """@return a list of files/directories created"""
    files_created=[]
    if platform.type != "win32":
        pass
    else:
        print "Installing environment script...",
        python_dir=sysconfig.get_config_var("prefix")
        scripts_dir=os.path.join(python_dir, "scripts")
        # FIXME - this list needs some work
        advertised_scripts=" ".join(["twistd", "mktap", "generatelore",
                                     "hlint", "manhole", "tapconvert",
                                     "html2latex", "ckeygen", "trial",
                                     "coil",
                                     ])
        # The following scripts are not advertised for the following reasons
        # conch - issues an exception when run with no arguments
        # websetroot - issues an exception when run with no args
        # im, t-im - issue exceptions for missing gtk when run
        # tap2deb - platform-specific
        # tk* - the ones that work have icons in the start menu, no need
        pathdict={'scripts_dir': scripts_dir,
                  'advertised_scripts': advertised_scripts}
        batch_script="""@echo off
set PATHEXT=%%PATHEXT%%;.py
set PATH=%(scripts_dir)s;%%PATH%%
set PATH
echo -:- -:- -:- -:- -:--:- -:- -:- -:- -:--:- -:- -:- -:- -:-
echo Commands available in twisted: %(advertised_scripts)s
echo -:- -:- -:- -:- -:--:- -:- -:- -:- -:--:- -:- -:- -:- -:-
""" % pathdict
        bat_location=getBatFilename()
        bat_file=open(bat_location, 'w')
        bat_file.write(batch_script)
        bat_file.close()
        file_created(bat_location)
        files_created.append(bat_location)
        print "Done."

        if not sys.modules.has_key('win32api'):
            warntext="""((( Warning )))
win32all is not available on your system, so no icons have 
been installed for Twisted.

We recommend installing win32all to get the most out of 
Twisted. This package is available at the URL: 

%(url)s

If you want icons to appear in the Start menu, you must:
1) Download & install win32all from the URL above
2) Run the Twisted installer (this program) again.
"""
            warn_dict={'url': "http://starship.python.net/crew/mhammond/win32/Downloads.html"}
            print warntext % warn_dict
        else:
            print 'Installing Icons for Twisted...',
            sys.stdout.flush()
            menu_path=os.path.join(getProgramsMenuPath(),
                                     "Twisted %s" %twisted.copyright.version)
            try:
                os.mkdir(menu_path)
                directory_created(menu_path)
                files_created.append(menu_path)
            except OSError:
                pass

            # command prompt
            shortcut=Shortcut(os.getenv("ComSpec"),
                                "/k %s" % bat_location,
                                workingdir="C:\\")
            cp_shortcut_path=os.path.join(menu_path, "Twisted Command Prompt.lnk")
            shortcut.save(cp_shortcut_path)
            file_created(cp_shortcut_path)
            files_created.append(cp_shortcut_path)

            # tkmktap
            exec_dir=sysconfig.get_config_var("exec_prefix")
            shortcut=Shortcut(os.path.join(exec_dir, "pythonw.exe"),
                              os.path.join(scripts_dir, "tkmktap.py"),
                              workingdir="C:\\")
            mktap_shortcut_path=os.path.join(menu_path, "Application Maker.lnk")
            shortcut.save(mktap_shortcut_path)
            file_created(mktap_shortcut_path)
            files_created.append(mktap_shortcut_path)
# FIXME - tktwistd doesn't actually work on Windows. No icon until fixed.
#            # tktwistd
#            shortcut=Shortcut(os.path.join(exec_dir, "pythonw.exe"),
#                              os.path.join(scripts_dir, "tktwistd.py"),
#                              workingdir="C:\\")
#            twistd_shortcut_path=os.path.join(menu_path, "Application Runner.lnk")
#            shortcut.save(twistd_shortcut_path)
#            file_created(twistd_shortcut_path)
#            files_created.append(twistd_shortcut_path)

            # tkconch
            shortcut=Shortcut(os.path.join(exec_dir, "pythonw.exe"),
                              os.path.join(scripts_dir, "tkconch.py"),
                              workingdir="C:\\")
            conch_shortcut_path=os.path.join(menu_path, "TkConch (ssh).lnk")
            shortcut.save(conch_shortcut_path)
            file_created(conch_shortcut_path)
            files_created.append(conch_shortcut_path)

            # uninstall
            remove_exe=os.path.join(python_dir, "RemoveTwisted.exe")
            remove_log=os.path.join(python_dir, "Twisted-wininst.log")
            icon_dll=getShell32DLLPath()
            icon_number=64 # trash can on win2k.. may be different on other OS
            remove_args='-u "%s"' % remove_log
            shortcut=Shortcut(remove_exe, 
                              remove_args, 
                              iconpath=icon_dll,
                              iconidx=icon_number)
            uninstall_shortcut_path=os.path.join(menu_path, "Uninstall Twisted.lnk")
            shortcut.save(uninstall_shortcut_path)
            file_created(uninstall_shortcut_path)
            files_created.append(uninstall_shortcut_path)
            print "Done."
        print "Post-install successful!"
    return files_created

if __name__=='__main__':
    run()
