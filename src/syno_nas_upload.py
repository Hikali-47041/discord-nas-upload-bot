import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from synology_api import filestation

def str2bool(value):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'true', and '1';
    False values are anything else.
    """
    return value.lower() in ("true", "1")

load_dotenv()
ip_addr = os.getenv('NAS_IP_ADDR')
port = os.getenv('NAS_IP_PORT')
username = os.getenv('NAS_USER_NAME')
password = os.getenv('NAS_USER_PASSWORD')
secure = bool(str2bool(os.getenv('SECURE', default="True")))
cert_verify = bool(str2bool(os.getenv('CERT_VERIFY', default="True")))
dsm_version = os.getenv('DSM_VERSION')
otp_code = os.getenv('OTP_CODE')

def nas_upload_main():
    """ nas upload main method """

    # parse command arguments
    parser = argparse.ArgumentParser(description='Synology nas file uploader')
    parser.add_argument('srcpath', help='upload source path', nargs="*")
    parser.add_argument('distpath', help='upload destination directory')
    parser.add_argument('-v', '--verbose', help='enable verbose', default=False, action='store_true')
    parser.add_argument('--overwrite', help='enable overwrite file if same name file exists', default=False, action='store_true')
    args = parser.parse_args()
    verbose_flag = args.verbose
    overwrite_flag = args.overwrite
    distpath = Path(args.distpath)
    dir_list = []
    srcpath_list = []
    for srcpath in args.srcpath:
        if Path(srcpath).is_file:
            srcpath_list += [(Path(srcpath), Path("."))]
            continue
        dir_list += [Path(file).relative_to(Path(srcpath).parent) for file in Path(srcpath).rglob("*") if Path.is_dir(file)]
        srcpath_list += [(Path(file), Path(file).relative_to(Path(srcpath).parent).parent) for file in Path(srcpath).rglob("*") if Path.is_file(file)]

    # connect
    if verbose_flag:
        print(f"Connecting to {ip_addr}:{port} as {username}")
    fl = filestation.FileStation(ip_addr, port, username, password, secure=secure, cert_verify=cert_verify, dsm_version=dsm_version, debug=verbose_flag, otp_code=otp_code)
    if verbose_flag:
        print(f"Connected to {ip_addr}:{port} \nServer Info: {fl.get_info()}")

    # warning if destination path is not in shared directories
    pubpath_list = [Path(directory["path"]) for directory in fl.get_list_share()["data"]["shares"]]
    if distpath.joinpath(distpath.root, distpath.parts[1]) not in pubpath_list:
        print(f"Warning: {distpath.joinpath(distpath.root, distpath.parts[1])} is not in share directories: {pubpath_list}")

    # mkdir
    for directory in dir_list:
        fl.create_folder(str(distpath), str(directory))
        if verbose_flag:
            print(f"created folder '{distpath.joinpath(directory)}'")

    # upload files
    for srcfile in srcpath_list:
        fl.upload_file(distpath.joinpath(srcfile[1]), srcfile[0], overwrite=overwrite_flag)
        if verbose_flag:
            print(f"uploaded '{srcfile[0]}' -> '{distpath.joinpath(srcfile[1])}'")

    # done
    print(f"uploaded files to {distpath}")
    fl.logout()


if __name__ == '__main__':
    nas_upload_main()
