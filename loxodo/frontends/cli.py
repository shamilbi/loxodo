#
# Loxodo -- Password Safe V3 compatible Password Vault
# Copyright (C) 2008 Christoph Sommer <mail@christoph-sommer.de>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

# pylint: disable=unused-argument,line-too-long,no-self-use

import os
import sys
from getpass import getpass
import readline
import cmd
import re
import csv

try:
    import pygtk
    import gtk
except ImportError:
    pygtk = None
    gtk = None

from loxodo.vault import (
    Vault,
    BadPasswordError,
    VaultFormatError,
    VaultVersionError,
    Record,
)
from loxodo.config import config
from loxodo import PY3


def print_arr(*args):
    if PY3:
        print(''.join(args))
    else:
        print(''.join([i.encode('utf-8', 'replace') for i in args]))


def print_s(s, *args):
    if args:
        if PY3:
            print(s % args)
        else:
            print(s % [i.encode('utf-8', 'replace') for i in args])
    else:
        print(s)


class InteractiveConsole(cmd.Cmd):
    def __init__(self):
        self.vault = None
        self.vault_file_name = None
        self.vault_password = None
        self.vault_modified = False

        cmd.Cmd.__init__(self)
        if sys.platform == "darwin":
            readline.parse_and_bind('bind ^I rl_complete')
        self.intro = 'Ready for commands. Type "help" or "help <command>" for help, type "quit" to quit.'
        self.prompt = "[none]> "

    def open_vault(self):
        print("Opening " + self.vault_file_name + "...")
        try:
            self.vault_password = getpass("Vault password: ")
            if not isinstance(self.vault_password, bytes):
                # PY3
                self.vault_password = self.vault_password.encode('utf-8')
        except EOFError as e:
            print("\n\nBye.")
            raise RuntimeError("No password given") from e
        try:
            self.vault = Vault(self.vault_password, filename=self.vault_file_name)
            self.prompt = "[" + os.path.basename(self.vault_file_name) + "]> "
        except BadPasswordError:
            print("Bad password.")
            raise
        except VaultVersionError:
            print("This is not a PasswordSafe V3 Vault.")
            raise
        except VaultFormatError:
            print("Vault integrity check failed.")
            raise
        print("... Done.\n")

    def postloop(self):
        print()

    def emptyline(self):
        pass

    def do_quit(self, line):
        """
        Exits interactive mode.
        """
        self.do_save()
        return True

    def do_save(self, line=None):
        'Save the vault'
        if self.vault_modified and self.vault_file_name and self.vault_password:
            self.vault.write_to_file(self.vault_file_name, self.vault_password)
            self.vault_modified = False
            print("Changes Saved")

    def do_EOF(self, line):
        """
        Exits interactive mode.
        """
        return True

    def do_add(self, line):
        """
        Adds a user to the vault

        Example: add USERNAME [TITLE, [GROUP]]
        """
        if not line:
            cmd.Cmd.do_help(self, "add")
            return

        line = line.split(" ")
        entry = Record.create()
        entry.user = line[0]
        if len(line) >= 2:
            entry.title = line[1]
        if len(line) >= 3:
            entry.group = line[2]

        passwd = getpass("Password: ")
        passwd2 = getpass("Re-Type Password: ")
        if passwd != passwd2:
            print("Passwords don't match")
            return

        entry.passwd = passwd

        self.vault.records.append(entry)
        self.vault_modified = True
        print("User Added, but not saved")

    def do_import(self, line):
        """
        Adds a CSV importer, based on CSV file

        Example: /home/user/data.csv
        Columns: Title,User,Password,URL,Group
        """
        if not line:
            cmd.Cmd.do_help(self, "import")
            return

        data = csv.reader(open(line, 'rb'))
        try:
            for row in data:
                entry = Record.create()
                entry.title = row[0]
                entry.user = row[1]
                entry.passwd = row[2]
                entry.url = row[3]
                entry.group = row[4]
                self.vault.records.append(entry)
            self.vault_modified = True
            print("Import completed, but not saved.")
        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (line, data.line_num, e))

    def do_ls(self, line):
        """
        Show contents of this Vault. If an argument is added a case insensitive
        search of titles is done, entries can also be specified as regular expressions.
        """
        if not self.vault:
            raise RuntimeError("No vault opened")

        if line is not None:
            vault_records = self.find_titles(line)
        else:
            vault_records = self.vault.records[:]
            vault_records.sort(key=lambda e1: e1.title)

        if vault_records is None:
            print("No matches found.")
            return

        for record in vault_records:
            print_arr(record.title, ' [', record.user, ']')

    def do_show(self, line, echo=True, passwd=False):
        """
        Show the specified entry (including its password).
        A case insenstive search of titles is done, entries can also be specified as regular expressions.
        """
        if not self.vault:
            raise RuntimeError("No vault opened")

        matches = self.find_titles(line)

        if matches is None:
            print('No entry found for "%s"' % line)
            return

        for record in matches:
            if echo is True:
                print_s(
                    """
%s.%s
Username : %s
Password : %s""",
                    record.group,
                    record.title,
                    record.user,
                    record.passwd,
                )
            else:
                print_s(
                    """
%s.%s
Username : %s""",
                    record.group,
                    record.title,
                    record.user,
                )

            if record.notes.strip():
                print_arr(
                    "Notes    :\n\t :", record.notes.replace("\n", "\n\t : "), "\n"
                )

            print("")

            if pygtk is not None and gtk is not None:
                cb = gtk.clipboard_get()
                if cb is not None:
                    cb.set_text(record.passwd)
                    cb.store()

    def complete_show(self, text, line, begidx, endidx):
        if not text:
            completions = [record.title for record in self.vault.records]
        else:
            fulltext = line[5:]
            lastspace = fulltext.rfind(' ')
            if lastspace == -1:
                completions = [
                    record.title
                    for record in self.vault.records
                    if record.title.upper().startswith(text.upper())
                ]
            else:
                completions = [
                    record.title[lastspace + 1 :]
                    for record in self.vault.records
                    if record.title.upper().startswith(fulltext.upper())
                ]

        completions.sort(key=lambda e1: e1.title)
        return completions

    def find_titles(self, regexp):
        "Finds titles, username, group, or combination of all 3 matching a regular expression. (Case insensitive)"
        matches = []
        pat = re.compile(regexp, re.IGNORECASE)
        for record in self.vault.records:
            if pat.match(record.title) is not None:
                matches.append(record)
            elif pat.match(record.user) is not None:
                matches.append(record)
            elif pat.match(record.group) is not None:
                matches.append(record)
            elif (
                pat.match(record.group + "." + record.title + " [" + record.user + "]")
                is not None
            ):
                matches.append(record)

        if len(matches) == 0:
            return None
        return matches


def main():
    args = sys.argv[1:]
    interactiveConsole = InteractiveConsole()

    if len(args) < 1:
        if config.recentvaults:
            interactiveConsole.vault_file_name = config.recentvaults[0]
            print("No Vault specified, using " + interactiveConsole.vault_file_name)
        else:
            print("No Vault specified, and none found in config.")
            sys.exit(2)
    elif len(args) > 1:
        print("More than one Vault specified")
        sys.exit(2)
    else:
        interactiveConsole.vault_file_name = args[0]

    interactiveConsole.open_vault()
    interactiveConsole.cmdloop()
