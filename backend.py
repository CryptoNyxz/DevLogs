"""
Backend Implementation.

Where the back end is implemented.
"""
from os.path import exists, isfile
from threading import Thread
from time import time_ns, sleep
from typing import Optional
from secrets import token_bytes
from _sha256 import sha256
from exceptions import InvalidCredentials
from exceptions import InvalidAccountFormat
from exceptions import AccountExists, AccountNotFound
from exceptions import InvalidUsername
from exceptions import TooManyAttempts
from exceptions import SessionOngoing, NoSession
from globaldata import ACCOUNTS_DIRPATH, sep
from globaldata import __author__, __version__, __license__
from utils import AESEncrypt
from utils import bytes_to_num, num_to_bytes, bytes_fixlen
from utils import deletefile


__author__ = __author__
__version__ = __version__
__license__ = __license__


class Entry:
    """
    Entry class.
    Each entry is represented as an Entry object.
    :param title: The title of the entry.
    :param entry: The entry text.
    :param entry_num: The entry number.
    """

    @staticmethod
    def loads(raw_data: bytes):
        """
        Load Entry from a sequence of bytes.
        :param raw_data: The raw bytes data to be extracted.
        :return: Entry instance loaded from raw bytes data.
        """
        r = 0
        title_len = bytes_to_num(raw_data[r: r+1])
        r += 1
        title = raw_data[r: r+title_len].decode('utf-8')
        r += title_len
        entry_num = bytes_to_num(raw_data[r: r+4])
        r += 4
        time_created = bytes_to_num(raw_data[r: r+8])
        r += 8
        time_last_update = bytes_to_num(raw_data[r: r+8])
        r += 8
        entry = raw_data[r:].decode('utf-8')

        dummy_entry = Entry(None, None, None)
        dummy_entry.title = title
        dummy_entry.entry = entry
        dummy_entry.entry_num = entry_num
        dummy_entry.time_created = time_created
        dummy_entry.time_last_update = time_last_update

        return dummy_entry

    def dumps(self) -> bytes:
        """
        Dump Entry as a sequence of bytes.
        :return: Entry instance compressed into raw bytes.
        """
        # Next 1 byte
        title_len = num_to_bytes(len(self.title))
        title_len = bytes_fixlen(title_len, 1)

        # Next N bytes
        title = self.title.encode('utf-8')

        # Next 4 bytes
        entry_num = bytes_fixlen(num_to_bytes(self.entry_num), 4)

        # Next 8 bytes
        time_created = num_to_bytes(self.time_created)
        time_created = bytes_fixlen(time_created, 8)

        # Next 8 bytes
        time_last_update = num_to_bytes(self.time_last_update)
        time_last_update = bytes_fixlen(time_last_update, 8)

        # Remaining bytes
        entry = self.entry.encode('utf-8')

        data = b''.join([title_len, title, entry_num,
                         time_created, time_last_update,
                         entry])

        return data

    def __init__(self, title: str or None, entry: str or None,
                 entry_num: int or None):
        self.title = title
        self.entry = entry
        self.entry_num = entry_num

        self.time_created = time_ns()
        self.time_last_update = time_ns()

    def update(self, title: str, entry: str):
        """
        Update the entry.
        :param title: The title of the entry.
        :param entry: The entry text.
        """
        self.title = title
        self.entry = entry

        self.time_last_update = time_ns()


class Account:
    """
    DevLogs Account class.
    :param username: The account username.
    :param raw_password: The account password.
    :param overwrite: Option to overwrite file data of another account if
    it already exists.
    """

    # The 256-bit pepper for the encrypted data
    # Note: Useless if application isn't compiled into a binary
    PEPPER = (b'\x8e\xa5H\r`\x1dD\xdam\xa0\xb2[?\x8e\xb0\xfe\xb6\xa6\xa5J'
              b'\xb6l\xc1P)\xdb\xda\x04|=RB')

    FILTEREDCHARS = '\\/:*?"<>|' + '%'

    @staticmethod
    def sanitize_fname(fname: str) -> str:
        """
        Sanitize the filename characters.
        :param fname: The filename.
        :return: The sanitized filename.
        """
        return ''.join(map(
            lambda c: f'%{hex(ord(c))[2:].upper()}'
            if c in Account.FILTEREDCHARS else c,
            fname
        ))

    @staticmethod
    def checks_auth(encrypted_data: bytes, raw_password: str) -> bytes or None:
        """
        Check if credentials are valid by checking encrypted_data.
        :param encrypted_data: The encrypted file data loaded directly
        from file.
        :param raw_password: The raw password to be used for decryption.
        :return: Decrypted account data bytes if password is valid or
        None if not.
        """
        if raw_password is None:
            return None
        if encrypted_data is None or len(encrypted_data) == 0:
            return ''  # Invalid format

        salt = encrypted_data[:32]
        password = sha256(Account.PEPPER + raw_password.encode('utf-8') + salt)
        del raw_password  # Remove raw_password data from RAM ASAP

        raw_data = AESEncrypt(password.digest()).decrypt(encrypted_data[32:])

        return raw_data

    @staticmethod
    def check_auth(username: str, raw_password: str) -> bytes or None:
        """
        Check if credentials are valid by checking account file.
        :param username: The username to be used for finding account file.
        :param raw_password: The raw password to be used for decryption.
        :return: Decrypted account data bytes if password is valid or
        None if not.
        """
        username = Account.sanitize_fname(username)
        filepath = f'{ACCOUNTS_DIRPATH}{sep}{username}.account'
        try:
            with open(filepath, 'rb') as file:
                return Account.checks_auth(file.read(), raw_password)
        except FileNotFoundError:
            return None

    @staticmethod
    def create_account(username: str, raw_password: str):
        """
        Create a new account.
        Basically sign up.
        :param username: The account username.
        :param raw_password: The account password.
        """
        Account(username, raw_password).dump()  # Save change in credentials

    @staticmethod
    def delete_account(username: str):
        """
        Delete an account, by deleting its file.
        :param username: The username to be used for finding account file.
        """
        username = Account.sanitize_fname(username)
        filepath = f'{ACCOUNTS_DIRPATH}{sep}{username}.account'
        deletefile(filepath)

    @staticmethod
    def loads(encrypted_data: bytes, raw_password: str):
        """
        Load Account from an encrypted sequence of bytes.
        :param encrypted_data: The encrypted data to be imported.
        :param raw_password: The raw password to be used for decryption.
        :return: Account instance loaded from encrypted bytes data.
        """
        raw_data = Account.checks_auth(encrypted_data, raw_password)

        if raw_data is None:
            raise InvalidCredentials("Wrong credentials were provided")
        elif len(raw_data) < 32+32+8+2:
            raise InvalidAccountFormat

        salt = token_bytes(32)  # Change salt everytime
        password = sha256(Account.PEPPER + raw_password.encode('utf-8') + salt)
        del raw_password  # Remove raw_password data from RAM ASAP

        try:
            r = 0
            username = raw_data[r: r+32].decode('utf-8').strip('\x00')
            r += 32
            r += 32
            time_created = bytes_to_num(raw_data[r: r+8])
            r += 8
            num_entries = bytes_to_num(raw_data[r: r+2])
            r += 2
            entries = []
            for entry in range(num_entries):
                entry_size = bytes_to_num(raw_data[r: r+3])
                r += 3
                entries.append(Entry.loads(raw_data[r: r+entry_size]))
                r += entry_size
        except IndexError:
            raise InvalidAccountFormat
        except UnicodeDecodeError:
            raise InvalidAccountFormat

        account = Account(None, None)
        account.username = username
        account.salt = salt
        account.password = password.digest()
        account.time_created = time_created
        account.entries = entries

        return account

    @staticmethod
    def load(username: str, raw_password: str):
        """
        Load Account from a account file.
        :param username: The username to be used for finding account file.
        :param raw_password: The raw password to be used for decryption.
        :return: Account instance loaded from file.
        """
        username = Account.sanitize_fname(username)
        filepath = f'{ACCOUNTS_DIRPATH}{sep}{username}.account'
        try:
            with open(filepath, 'rb') as file:
                return Account.loads(file.read(), raw_password)
        except FileNotFoundError:
            raise AccountNotFound

    def dumps(self):
        """Dump Account as an encrypted sequence of bytes."""
        # Next 32 bytes
        username = self.username.encode('utf-8')
        username = bytes_fixlen(username, 32)

        # Next 32 bytes
        password = self.password

        # Next 8 bytes
        time_created = num_to_bytes(self.time_created)
        time_created = bytes_fixlen(time_created, 8)

        # Next 2 bytes
        num_entries = num_to_bytes(len(self.entries))
        num_entries = bytes_fixlen(num_entries, 2)

        # Final N of (3 + M[n]) bytes
        entries = list(map(lambda e: e.dumps(), self.entries))
        entry_sizes = list(map(lambda raw_e: num_to_bytes(len(raw_e)),
                               entries))
        entry_sizes = list(map(lambda e_size: bytes_fixlen(e_size, 3),
                               entry_sizes))
        entries_data = b''.join([entry_sizes[i] + entries[i]
                                 for i in range(len(entries))])
        raw_data = b''.join([username, password, time_created,
                             num_entries, entries_data])

        # Next 32 bytes
        salt = self.salt

        encrypted_data = b''.join([
            salt,
            AESEncrypt(password).encrypt(raw_data)
        ])

        return encrypted_data

    def dump(self):
        """Dump Account into a account file."""
        username = Account.sanitize_fname(self.username)
        filepath = f'{ACCOUNTS_DIRPATH}{sep}{username}.account'
        with open(filepath, 'bw') as file:
            file.write(self.dumps())

    def __init__(self, username: str or None, raw_password: str or None,
                 overwrite: Optional[bool] = False):
        if username is raw_password is not None:

            if len(username.encode('utf-8')) > 32:
                raise InvalidUsername('Username is too long (>32)')

            salt = token_bytes(32)
            password = sha256(Account.PEPPER + raw_password.encode('utf-8')
                              + salt)

            _username = Account.sanitize_fname(username)
            filepath = f'{ACCOUNTS_DIRPATH}{sep}{_username}.account'

            if not overwrite:
                acc_exists = exists(filepath) and isfile(filepath)
                check_auth = Account.check_auth(username, raw_password)

                if acc_exists:
                    if check_auth is None:
                        raise InvalidAccountFormat
                    else:
                        raise AccountExists

            self.username = username
            self.password = password.digest()
            self.salt = salt

            self.time_created = time_ns()

            self.entries = []

    def add_entry(self, title: str, entry: str):
        """
        Add an entry.
        :param title: The title of the entry.
        :param entry: The entry text.
        """
        self.entries.append(Entry(title, entry, len(self.entries)))

    def del_entry(self, entry: Entry):
        """
        Delete an entry.
        :param entry: The Entry instance.
        """
        index = self.entries.index(entry)
        self.entries.pop(index)
        for e in range(index, len(self.entries)):
            self.entries[e].entry_num -= 1

    def move_entry_up(self, entry: Entry):
        """
        Move entry up.
        :param entry: The Entry instance.
        """
        index = self.entries.index(entry)
        if index > 0:
            entry.entry_num -= 1
            self.entries.insert(index-1, self.entries.pop(index))
            self.entries[index].entry_num += 1

    def move_entry_down(self, entry: Entry):
        """
        Move entry up.
        :param entry: The Entry instance.
        """
        index = self.entries.index(entry)
        if index < len(self.entries) - 1:
            entry.entry_num += 1
            self.entries.insert(index+1, self.entries.pop(index))
            self.entries[index].entry_num -= 1


class Session:
    """
    DevLogs Session class.
    Class for Account sessions.
    :param account: The Account instance to create a session of.
    """

    def __init__(self, account):
        self.account = account

        self.time_created = time_ns()

    def __del__(self):
        """When session is terminated."""
        self.account.dump()

    def lock_account(self):
        """Prevent any changes to account object and file."""
        NotImplemented

    def add_new_entry(self, title: str, entry: str):
        """
        Add new entry to account entries.
        :param title: The title of the entry.
        :param entry: The entry text.
        """
        self.account.add_entry(title, entry)


class SessionManager:
    """
    DevLogs Session Manager class.
    Manages Sessions.
    """

    MAX_FAILED_ATTEMPTS = 5
    INIT_HARDLOCK_DELAY = 20
    HARDLOCK_DELAY_INCR = 10

    def __init__(self):
        self.current_session = None

        # Lock when too many attempts are made
        self.session_hardlock = False
        # Current amount of failed attempts
        self.failed_attempts = 0
        # Current amount of seconds delay for hardlock
        self.hardlock_delay = SessionManager.INIT_HARDLOCK_DELAY

    def hardlock(self):
        """Prevent any attempts from starting a session."""
        def override():
            orig_create_session = self.create_session

            def new_create_session(username: str, raw_password: str):
                """
                Alternate function if hardlocked.
                :param username: The account username.
                :param raw_password: The account password.
                """
                raise TooManyAttempts

            self.create_session = new_create_session
            self.session_hardlock = True

            sleep(self.hardlock_delay)
            self.hardlock_delay += SessionManager.HARDLOCK_DELAY_INCR

            self.create_session = orig_create_session
            self.session_hardlock = False

        Thread(target=override, daemon=True).start()

    def create_session(self, username: str, raw_password: str):
        """
        Attempt to create a new session.
        Basically the equivalent of Login.
        :param username: The account username.
        :param raw_password: The account password.
        """
        if self.current_session is not None:
            raise SessionOngoing

        try:
            account = Account.load(username, raw_password)
        except InvalidCredentials:
            self.failed_attempts += 1
            if self.failed_attempts >= SessionManager.MAX_FAILED_ATTEMPTS:
                self.hardlock()
            raise
        except InvalidAccountFormat:
            self.failed_attempts += 1
            if self.failed_attempts >= SessionManager.MAX_FAILED_ATTEMPTS:
                self.hardlock()
            raise

        self.failed_attempts = 0
        self.hardlock_delay = SessionManager.INIT_HARDLOCK_DELAY

        self.current_session = Session(account)

    def stop_session(self):
        """
        Stop the current session.
        Basically the equivalent of Logout.
        """
        del self.current_session
        self.current_session = None

    def save_account(self):
        """Save account data to account file."""
        try:
            self.current_session.account.dump()
        except AttributeError:
            raise NoSession
