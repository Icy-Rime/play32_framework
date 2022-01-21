# Play32 Framework
useing [mpypack](https://github.com/Dreagonmon/mpypack) to pack up code.

This is the base software framework for Play32 game console.

## Install
- [flash firmware.bin](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)
- connect to wifi Play32AP with password 123456
- access ftp via 192.168.4.1:21 (recommand FileZilla with utf-8 coding)
- upload framework.pack and framework.pack.sha256 to /tmp
- keep A and B pressed at the sametime
- wait the board reboot itself
- press B at app_selector, enter normal ftp mode
- upload apps to test
