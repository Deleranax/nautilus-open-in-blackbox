#!/usr/bin/python3
import shlex
import shutil
import subprocess
import urllib.parse

from gi import require_version

require_version("Nautilus", "4.0")
require_version("Gtk", "4.0")

TERMINAL_NAME = "com.raggesilver.BlackBox"

import logging
import os
from gettext import gettext

from gi.repository import GObject, Nautilus

if os.environ.get("NAUTILUS_BLACKBOX_DEBUG", "False") == "True":
    logging.basicConfig(level=logging.DEBUG)

REMOTE_URI_SCHEME = ["ftp", "sftp"]

class BlackBoxNautilus(GObject.GObject, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()
        self.is_select = False
        pass

    def get_file_items(self, files: list[Nautilus.FileInfo]):
        """Return to menu when click on any file/folder"""
        if not self.only_one_file_info(files):
            return []

        menu = []
        fileInfo = files[0]
        self.is_select = False

        if fileInfo.is_directory():
            self.is_select = True
            dir_path = self.get_abs_path(fileInfo)
            
            if fileInfo.get_uri_scheme() in REMOTE_URI_SCHEME:
                menu_item = self._create_remote_nautilus_item(dir_path)
                menu.append(menu_item)
            else:
                menu_item = self._create_nautilus_item(dir_path)
                menu.append(menu_item)

        return menu

    def get_background_items(self, directory):
        """Returns the menu items to display when no file/folder is selected
        (i.e. when right-clicking the background)."""
        # Some concurrency problem fix.
        # when you select a directory, and right mouse, nautilus will call this
        # once the moments you focus the menu. This code to ignore that time.
        if self.is_select:
            self.is_select = False
            return []
            
        menu = []
        
        if directory.is_directory():
            dir_path = self.get_abs_path(directory)
            
            if directory.get_uri_scheme() in REMOTE_URI_SCHEME:
                menu_item = self._create_remote_nautilus_item(dir_path)
                menu.append(menu_item)
            else:
                menu_item = self._create_nautilus_item(dir_path)
                menu.append(menu_item)

        return menu

    def _create_nautilus_item(self, dir_path: str) -> Nautilus.MenuItem:
        """Creates the 'Open In Black Box' menu item."""

        item = Nautilus.MenuItem(
            name="BlackBoxNautilus::open_in_blackbox",
            label=gettext("Ouvrir dans Boîte Noire"),
            tip=gettext("Ouvrir le fichier/dossier dans Boîte Noire"),
        )

        item.connect("activate", self._nautilus_run, dir_path)

        return item
        
    def _create_remote_nautilus_item(self, dir_path: str) -> Nautilus.MenuItem:
        """Creates the 'Open Remote In Black Box' menu item."""

        item = Nautilus.MenuItem(
            name="BlackBoxNautilus::open_remote_in_blackbox",
            label=gettext("Ouvrir à distance dans Boîte Noire"),
            tip=gettext("Ouvrir à distance le fichier/dossier dans Boîte Noire"),
        )

        item.connect("activate", self._nautilus_run, dir_path)

        return item

    def is_native(self):
        if shutil.which("blackbox-terminal") == "/usr/bin/blackbox-terminal":
            return "blackbox-terminal"
        if shutil.which("blackbox") == "/usr/bin/blackbox":
            return "blackbox"

    def _nautilus_run(self, menu, path):
        """'Open with Black Box 's menu item callback."""
        args = None
            
        if self.is_native()=="blackbox-terminal":
            args = ["blackbox-terminal"]
        elif self.is_native()=="blackbox":
            args = ["blackbox"]
        else:
            args = ["/usr/bin/flatpak", "run", TERMINAL_NAME]
            
        result = urllib.parse.urlparse(path)
        if result.scheme in REMOTE_URI_SCHEME:
            cmd = ["ssh", "-t"]
            if result.username:
                cmd.append(f"{result.username}@{result.hostname}")
            else:
                cmd.append(result.hostname)

            if result.port:
                cmd.append("-p")
                cmd.append(str(result.port))

            cmd.append(shlex.quote("cd " + shlex.quote(urllib.parse.unquote(result.path)) + " ; $SHELL"))
            
            args.extend(["-c", " ".join(cmd)])
            subprocess.Popen(args)
        else:
            args.extend(["-w", path])
            subprocess.Popen(args, cwd=path)

    def get_abs_path(self, fileInfo: Nautilus.FileInfo):
        uri = fileInfo.get_uri()
        path = uri.replace("file://", "")

        return urllib.parse.unquote(path)

    def only_one_file_info(self, files: list[Nautilus.FileInfo]):
        return len(files) == 1
