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

import os
from io import BytesIO
from importlib.resources import open_binary
import wx


def get_image(fname):
    with open_binary('loxodo.resources', fname) as fp:
        return wx.Image(fp)


def get_bitmap(fname):
    return wx.Bitmap(get_image(fname))


def get_icon(fname, width, height):
    icon = wx.Icon()
    icon.CopyFromBitmap(get_bitmap(fname))
    icon.SetWidth(width)
    icon.SetHeight(height)
    return icon
