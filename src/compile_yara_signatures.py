#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess
from tempfile import NamedTemporaryFile
from common_helper_files import get_files_in_dir, get_dirs_in_dir

from helperFunctions.fileSystem import get_src_dir

SIGNATURE_DIR = os.path.join(get_src_dir(), 'analysis/signatures')


def _create_joint_signature_file(directory, tmp_file):
    all_signatures = list()
    for signature_file in sorted(get_files_in_dir(directory)):
        with open(signature_file, 'rb') as fd:
            all_signatures.append(fd.read())

    with open(tmp_file.name, 'wb') as fd:
        fd.write(b'\x0a'.join(all_signatures))


def _get_plugin_name(plugin_path):
    return plugin_path.split('/')[-2]


def _create_compiled_signature_file(directory, tmp_file):
    target_path = os.path.join(SIGNATURE_DIR, '{}.yc'.format(_get_plugin_name(directory)))
    try:
        subprocess.run('yarac -d test_flag=false {} {}'.format(tmp_file.name, target_path), shell=True, check=True)
    except subprocess.CalledProcessError:
        print('[ERRROR] Creation of {} failed !!'.format(os.path.split(target_path)[0]))


def _create_signature_dir():
    print('Create signature directory {}'.format(SIGNATURE_DIR))
    os.makedirs(SIGNATURE_DIR, exist_ok=True)


def main():
    _create_signature_dir()
    for plugin_dir in get_dirs_in_dir(os.path.join(get_src_dir(), 'plugins/analysis')):
        signature_dir = os.path.join(plugin_dir, 'signatures')
        if os.path.isdir(signature_dir):
            print('Compile signatures in {}'.format(signature_dir))
            with NamedTemporaryFile(mode='w') as tmp_file:
                _create_joint_signature_file(signature_dir, tmp_file)
                _create_compiled_signature_file(signature_dir, tmp_file)

    return 0


if __name__ == '__main__':
    exit(main())
