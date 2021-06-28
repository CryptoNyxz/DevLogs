"""
Utility Classes and Functions for DevLogs sub modules.

All the utility functions and classes are defined here.
"""
from os import remove
from time import ctime, strftime, strptime
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Random import new
from globaldata import __author__, __version__, __license__


__author__ = __author__
__version__ = __version__
__license__ = __license__
import Crypto
print(Crypto.__dict__)


def hex_to_bytes(hexstr: str) -> bytes:
    """
    Convert hexadecimal string to bytes.
    :param hexstr: The hexadecimal string.
    :return: The byte sequence.
    """
    try:
        if len(hexstr) % 2:
            hexstr = '0' + hexstr
        return b''.fromhex(hexstr) if hexstr not in '0123456789abcdef' \
            else bytes([int(hexstr, 16)])
    except Exception:
        raise


def bytes_to_hex(byteseq: bytes) -> str:
    """
    Convert bytes into hexadecimal string.
    :param byteseq: The byte sequence to be converted to hex.
    :return: The hexadecimal string
    """
    return byteseq.hex()


def num_to_bytes(num: int) -> bytes:
    """
    Convert an integer to bytes.
    :param num: The integer to be converted to bytes.
    :return: The bytes equivalent of the integer.
    """
    return hex_to_bytes(hex(num)[2:])


def bytes_to_num(byteseq: bytes) -> int:
    """
    Convert bytes to integer.
    :param byteseq: The byte sequence to be converted.
    :return: The integer equivalent of the byte sequence.
    """
    return int(bytes_to_hex(byteseq), 16)


def bytes_fixlen(byteseq: bytes, length: int) -> bytes:
    """
    Fix the length of a byte sequence.
    :param byteseq: The byte sequence to fix the length of.
    :param length: The length of the sequence.
    :return: The byte sequence with fixed length.
    """
    if len(byteseq) > length:
        return byteseq[:length]
    else:
        return (b'\x00' * (length - len(byteseq))) + byteseq


def timestamp(seconds: Optional[int] = None) -> str:
    """
    Give the timestamp.
    :param seconds: The time in seconds after Unix Epoch.
    :return: The timestamp string.
    """
    return strftime('%a - %m/%d/%Y %I:%M:%S %p',
                    strptime(ctime(seconds), '%a %b %d %H:%M:%S %Y'))


# OS Functions


def deletefile(fpath: str):
    """
    Delete a file.
    :param fpath: The path to the file.
    """
    # Remove contents
    with open(fpath, 'bw') as file:
        pass
    # Unlink
    remove(fpath)


# Classes


class AESEncrypt:
    """
    AES Cipher class.
    :param hashed_key: The key string hashed with SHA-256 to be used
    during encryption.
    :param self_destruct: If it will self-destruct after encryption or
    decryption to preserve security.
    """

    def __init__(self, hashed_key: bytes,
                 self_destruct: Optional[bool] = True):
        self.passkey = hashed_key

        self.self_destruct = self_destruct

    def encrypt(self, string: str or bytes) -> bytes:
        """
        Encrypt message.
        :param string: The string to be encrypted.
        :return: The encrypted message.
        """
        padded = self.__pad(string)
        if not isinstance(padded, bytes):
            padded = padded.encode('utf-8')

        iv = new().read(16)
        cipher = AES.new(self.passkey, AES.MODE_CBC, iv)

        if self.self_destruct:
            del self.passkey

        # return b64encode(iv + cipher.encrypt(padded))
        return iv + cipher.encrypt(padded)

    def decrypt(self, encrypted: bytes) -> bytes:
        """
        Decrypt message.
        :param encrypted: The bytes to be decrypted.
        :return: The decrypted message.
        """
        # raw_encrypted = b64decode(encrypted)
        raw_encrypted = encrypted

        iv = raw_encrypted[:16]
        cipher = AES.new(self.passkey, AES.MODE_CBC, iv)
        padded = cipher.decrypt(raw_encrypted[16:])

        if self.self_destruct:
            del self.passkey

        result = self.__unpad(padded)
        if result:
            return result

    def __pad(self, msg: bytes or str) -> bytes or str:
        """
        Pad bytes to make length a multiple of block size.
        :param msg: Message to be padded.
        :return: The padded message.
        """
        if isinstance(msg, bytes):
            return msg + ((16 - len(msg) % 16) *
                          chr(16 - len(msg) % 16)).encode('utf-8')
        else:
            return msg + (16 - len(msg) % 16) * chr(16 - len(msg) % 16)

    def __unpad(self, msg):
        """
        Unpad bytes to transform it back to its original length.
        :param msg: Message to be unpadded.
        :return: The unpadded message.
        """
        return msg[:-ord(msg[len(msg) - 1:])]
