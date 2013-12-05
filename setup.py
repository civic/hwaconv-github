# -*- coding: utf-8 -*-

from distutils.core import setup
from glob import glob
import os
import py2exe
import shutil

candidates = glob(r"C:\Windows\winsxs\Manifests\x86_microsoft.vc90.crt_*_9.0.21022.8_*.manifest")
if not candidates:
    raise Exception("Coud not find VC9 runtime ( 9.0.21022.8 ) from 'C:\Windows\winsxs'.")

dirname = os.path.splitext(os.path.basename(candidates[0]))[0]
data_files = [("Microsoft.VC90.CRT", [candidates[0]] + glob(os.path.join(r"C:\Windows\winsxs", dirname, "*.*")))]

build_dir = "dist"

option = {
    "compressed"    :    1    ,
    "optimize"      :    2    ,
    "bundle_files"  :    1
}

setup(
    options = {
        "py2exe"    :    option
    },

    console = [
        {"script"   :    "hwaconv.py"}
    ],

    data_files=data_files,
    zipfile = None
)

manifests = glob(os.path.join(build_dir, r"Microsoft.VC90.CRT", "*.manifest"))
shutil.move(manifests[0], os.path.join(build_dir, "Microsoft.VC90.CRT", "Microsoft.VC90.CRT.manifest"))
