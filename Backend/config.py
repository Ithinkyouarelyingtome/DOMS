import os
KNOWN_DEVICES = [
    ("127.0.0.1", 6001),
    ("127.0.0.1", 6002),
]

STORAGE_QUOTA = 200 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "device_storage")
DH_PARAMETERS_PEM = b"""-----BEGIN DH PARAMETERS-----
MIIBCAKCAQEAsqDUueTwSFriFM2CYQkGxwqZ3X/2nBF2TPgRi7AoDRJLStQ5wWIN
Rb/Pog6I2Ni+JekvnJljKoexbsxHy/xg4Ud+M0gJ8Jj/rpNZhLSYmc/WP3ziZRZF
yzfa2ZhZu+aK2URiI/fbsxKv78Hz0seOPqi7d7CH+O97yE5GrOuCgZJ7vL7Ry9eB
aR91LbIcgPDMFI1BMWk6HMBX2HwwsnIwMr3vLYBILsYQ6dluTzF2MvLXkdKA0R7o
YKk916Y+nT9SHDmPHtHiMisL8NEh2puxraeq2l0WhIvBNtCcFY1mEXZhmmTWiN4Z
pd6SdaJHHg+Ysjt8CNDk1ro0n7JqresT5wIBAg==
-----END DH PARAMETERS-----"""
