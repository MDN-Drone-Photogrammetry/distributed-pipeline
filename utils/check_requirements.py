import os
from pathlib import Path
import shutil
import subprocess

from utils.text_utils import emojis
from utils.colorstr import colorstr

def check_requirements(requirements='requirements.txt', exclude=()):
    # Check installed dependencies meet requirements (pass *.txt file or list of packages)
    import pkg_resources as pkg
    prefix = colorstr('red', 'bold', 'requirements:')
    if isinstance(requirements, (str, Path)):  # requirements.txt file
        file = Path(requirements)
        if not file.exists():
            print(f"{prefix} {file.resolve()} not found, check failed.")
            return
        requirements = [f'{x.name}{x.specifier}' for x in pkg.parse_requirements(
            file.open()) if x.name not in exclude]
    else:  # list or tuple of packages
        requirements = [x for x in requirements if x not in exclude]

    n = 0  # number of packages updates
    for r in requirements:
        try:
            pkg.require(r)
        except Exception as e:  # DistributionNotFound or VersionConflict if requirements not met
            n += 1
            print(
                f"{prefix} {e.req} not found and is required by distributed-pipeline, attempting auto-update...")
            print(subprocess.check_output(
                f"pip install '{e.req}'", shell=True).decode())

    if n:  # if packages updated
        source = file.resolve() if 'file' in locals() else requirements
        s = f"{prefix} {n} package{'s' * (n > 1)} updated per {source}\n" \
            f"{prefix} ⚠️ {colorstr('bold', 'Restart runtime or rerun command for updates to take effect')}\n"
        print(emojis(s))  # emoji-safe

def install_lastools(force=False):
    import wget
    import zipfile
    LASTOOLS = 'LAStools_210330'

    if not os.path.isdir('./LAStools') or force:
        if force:
            shutil.rmtree('./LAStools')
            print('Reinstalling lastools...')    
        else:
            print('Lastools not found installing...')

        if not os.path.isfile(f'{LASTOOLS}.zip'):
            filename = wget.download(f'https://lastools.github.io/download/{LASTOOLS}.zip')
        else:
            filename = f'{LASTOOLS}.zip'

        with zipfile.ZipFile(filename,"r") as zip_ref:
            zip_ref.extractall("./")

        shutil.rmtree(filename)

        output = subprocess.Popen("make", cwd="./LAStools", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        output.wait()
        try:
            print(output.returncode)
        except:
            print(f'Error installing lastools, {output.stderr}')