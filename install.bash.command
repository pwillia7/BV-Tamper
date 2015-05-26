#!/bin/bash

# Attempt to catch people running the script via sudo and abort
[[ $(whoami) == "root" ]] && echo "This script should not be run as root or via the 'sudo' command; aborting..." && exit

# Make sure the Command-Line Tools have been installed
[[ ! -r /usr/bin/svn ]] && echo "You need to install the Command-Line Tools in Xcode first; aborting..." && echo "See: http://stackoverflow.com/a/9329325" && exit

function installTamper {
	 sudo easy_install python
	 sudo ln -s /Applications/Sublime\ Text.app/Contents/SharedSupport/bin/subl /usr/bin/subl
	 cp ~/Downloads/BV-Tamper-master/bv_st_plugins/* ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/User/
	 sudo easy_install mitmproxy
	 sudo python ~/Downloads/BV-Tamper-master/mitm-extension/setup.py install

}

installTamper