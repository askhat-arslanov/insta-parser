import os
import shutil

from .constants import ARCHIVES_DIR


def prepare_archive(account_name):
    """ Packs media files to zip archive and
    after that deletes them with directory.
    Returns name of prepared archive.
    """
    current_dir = os.path.join(ARCHIVES_DIR, account_name)
    shutil.make_archive(current_dir, 'zip', current_dir)
    shutil.rmtree(current_dir)
    return account_name + '.zip'
