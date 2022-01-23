#!/usr/bin/env python
# This script should be run via sudo.


import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import hashlib
from optparse import OptionParser, BadOptionError

INSTALLER_LINUX_FILENAME_64 = "aws-replication-installer-64bit"
INSTALLER_LINUX_FILENAME_32 = "aws-replication-installer-32bit"
INSTALLER_BUCKET_MAP = """{"ap-south-1": ["aws-application-migration-service-ap-south-1", "aws-application-migration-service-hashes-ap-south-1", "latest"], "ap-northeast-2": ["aws-application-migration-service-ap-northeast-2", "aws-application-migration-service-hashes-ap-northeast-2", "latest"], "ap-east-1": ["aws-application-migration-service-ap-east-1", "aws-application-migration-service-hashes-ap-east-1", "latest"], "eu-west-2": ["aws-application-migration-service-eu-west-2", "aws-application-migration-service-hashes-eu-west-2", "latest"], "ap-northeast-3": ["aws-application-migration-service-ap-northeast-3", "aws-application-migration-service-hashes-ap-northeast-3", "latest"], "us-west-1": ["aws-application-migration-service-us-west-1", "aws-application-migration-service-hashes-us-west-1", "latest"], "ca-central-1": ["aws-application-migration-service-ca-central-1", "aws-application-migration-service-hashes-ca-central-1", "latest"], "sa-east-1": ["aws-application-migration-service-sa-east-1", "aws-application-migration-service-hashes-sa-east-1", "latest"], "eu-north-1": ["aws-application-migration-service-eu-north-1", "aws-application-migration-service-hashes-eu-north-1", "latest"], "ap-southeast-1": ["aws-application-migration-service-ap-southeast-1", "aws-application-migration-service-hashes-ap-southeast-1", "latest"], "us-east-2": ["aws-application-migration-service-us-east-2", "aws-application-migration-service-hashes-us-east-2", "latest"], "eu-west-1": ["aws-application-migration-service-eu-west-1", "aws-application-migration-service-hashes-eu-west-1", "latest"], "ap-southeast-2": ["aws-application-migration-service-ap-southeast-2", "aws-application-migration-service-hashes-ap-southeast-2", "latest"], "us-west-2": ["aws-application-migration-service-us-west-2", "aws-application-migration-service-hashes-us-west-2", "latest"], "eu-central-1": ["aws-application-migration-service-eu-central-1", "aws-application-migration-service-hashes-eu-central-1", "latest"], "ap-northeast-1": ["aws-application-migration-service-ap-northeast-1", "aws-application-migration-service-hashes-ap-northeast-1", "latest"], "us-east-1": ["aws-application-migration-service-us-east-1", "aws-application-migration-service-hashes-us-east-1", "latest"], "eu-west-3": ["aws-application-migration-service-eu-west-3", "aws-application-migration-service-hashes-eu-west-3", "latest"], "eu-south-1": ["aws-application-migration-service-eu-south-1", "aws-application-migration-service-hashes-eu-south-1", "latest"], "me-south-1": ["aws-application-migration-service-me-south-1", "aws-application-migration-service-hashes-me-south-1", "latest"], "af-south-1": ["aws-application-migration-service-af-south-1", "aws-application-migration-service-hashes-af-south-1", "latest"]}"""
DOCS_LINK = "https://docs.aws.amazon.com/mgn/latest/ug/Troubleshooting-Agent-Issues.html#Error-Installation-Failed"
INSTALLER_VERSION = "1.0.0"


class CustomOptionParser(OptionParser):
    def _process_long_opt(self, rargs, values):
        try:
            OptionParser._process_long_opt(self, rargs, values)
        except BadOptionError:
            pass

    def _process_short_opts(self, rargs, values):
        try:
            OptionParser._process_short_opts(self, rargs, values)
        except BadOptionError:
            pass

    def print_help(self, file=None):
        script_name = os.path.basename(__file__)
        help_text = (
            """
usage: %s [-h] [--aws-access-key-id AWS_ACCESS_KEY_ID] [--aws-secret-access-key AWS_SECRET_ACCESS_KEY]
    [--region REGION] [--no-prompt] [--force-volumes] [--devices DEVICES] [--endpoint ENDPOINT]
    [--s3-endpoint S3_ENDPOINT] [--tags KEY=VALUE [KEY=VALUE ...]]

optional arguments:
  -h, --help            show this help message and exit
  --aws-access-key-id AWS_ACCESS_KEY_ID
                        The AWS Access Key ID you generated when creating an IAM User for installing the AWS
                        Replication Agent.
  --aws-secret-access-key AWS_SECRET_ACCESS_KEY
                        The AWS Secret Access Key you generated when creating an IAM User for installing the AWS
                        Replication Agent.
  --region REGION       Name of the AWS Region into which you want to migrate your source server in the standard
                        format (For example: us-east-1)
  --no-prompt           This parameter will run a non-interactive installation.
  --force-volumes       This parameter must be used with the --no-prompt parameter. This parameter will cancel the
                        automatic detection of physical disks to replicate. You will need to specify the exact
                        disks to replicate using the --devices parameter.
  --devices DEVICES
                        This parameter specifies which specific disks to replicate. This parameter does not
                        function when your Source servers are located in AWS. Devices are separated by commas. For
                        example: /dev/sda,/dev/sdb. It is required when --no-prompt and --force-volumes are
                        present.
  --endpoint ENDPOINT   Use this parameter to specify the Private Link endpoint you created for Application
                        Migration Service if you do not wish to open your firewall ports to access the default
                        Application Migration Service endpoint.
  --s3-endpoint S3_ENDPOINT
                        Use this parameter to specify a VPC endpoint you created for S3 if you do not wish to open
                        your firewall ports to access the default S3 endpoint. Used only during the installation
                        process.
  --tags KEY=VALUE [KEY=VALUE ...]
                        Use this parameter to add resource tags to the Source server. Use a space to separate each
                        tag (For example --tags tag1=val1 tag2=val2 tag3=val3)
""" % script_name
        )
        print(help_text)


# Though it would be cleaner to use namedtuple here, python 2.4 does not support it, so we use a class
class DF(object):  # pylint: disable=too-few-public-methods
    def __init__(self, filesystem, blocks, used, available, capacity, mounted_on):
        self.filesystem = filesystem
        self.blocks = blocks
        self.used = used
        self.available = available
        self.capacity = capacity
        self.mounted_on = mounted_on


IS_PYTHON2 = sys.version_info[0] == 2

if IS_PYTHON2:
    _input = raw_input
else:
    _input = input

REQUIRED_DISK_SPACE = 500 * 1024 * 1024


def main(region, s3_endpoint):

    print("The installation of the AWS Replication Agent has started.")  # pylint: disable=superfluous-parens

    if IS_PYTHON2:
        from urllib2 import urlopen  # pylint: disable=no-name-in-module,import-error

        if sys.maxint > (2 ** 31):  # pylint: disable=no-member
            arch = 64
        else:
            arch = 32
    else:
        import struct
        from urllib.request import urlopen  # pylint: disable=no-name-in-module,import-error

        if struct.calcsize("P") * 8 == 64:
            arch = 64
        else:
            arch = 32

    if arch == 32:
        filename = INSTALLER_LINUX_FILENAME_32
    else:
        filename = INSTALLER_LINUX_FILENAME_64

    try:
        handle_noexec_tmp()
    except Exception:  # pylint: disable=broad-except
        pass

    doing = ""
    reading_url = ""

    try:

        while not region:
            region = _input("AWS Region Name: ").strip()

        bucket_map = json.loads(INSTALLER_BUCKET_MAP)

        doing = "checking disk free space"
        if not check_free_space(REQUIRED_DISK_SPACE):
            print(
                """Installation failed. 
The source server does not have enough free disk space to install the AWS Replication Agent.
Free up the required space and re-start theinstallation."""
            )

            return -1
        doing = "preparing installer download url"

        if region not in bucket_map:
            print("Region " + region + " is not supported by this version of the AWS Replication Agent installer")
            return -1

        bucket_name, hash_bucket_name, bucket_path = bucket_map[region]

        netloc = bucket_name + ".s3." + region + ".amazonaws.com"
        url = "https://" + netloc + "/" + bucket_path + "/linux/" + filename
        hash_netloc = hash_bucket_name + ".s3." + region + ".amazonaws.com"
        hash_url = "https://" + hash_netloc + "/" + bucket_path + "/linux/" + filename + ".sha512"

        doing = "downloading installer"

        if s3_endpoint:
            original_getaddrinfo = socket.getaddrinfo

            def getaddrinfo(hostname, *args):
                return original_getaddrinfo(s3_endpoint if hostname in [netloc, hash_netloc] else hostname, *args)

            socket.getaddrinfo = getaddrinfo

        reading_url = url
        content = urlopen(url).read()
        reading_url = hash_url
        content_hash = urlopen(hash_url).read().strip()

        if hashlib.sha512(content).hexdigest().encode() != content_hash:
            print(
                """Installation failed
Failed verifying the AWS Replication Agent file contents
Learn more about connectivity issues in our documentation at """
                + DOCS_LINK
            )

            return -1

        open(filename, "wb").write(content)

        doing = "preparing installer to run"
        currentStat = os.stat(filename).st_mode
        os.chmod(filename, currentStat | stat.S_IEXEC)

        doing = "running installer"
        s3_endpoint_part = ["--s3-endpoint", s3_endpoint] if s3_endpoint else []
        return subprocess.call(["./" + filename] + sys.argv[1:] + ["--region", region] + s3_endpoint_part)

    except:
        # We have to retrieve exception info this way due to the need to remain
        # compatible with both Python 2.4 and Python 3.6
        etype, e, _ = sys.exc_info()
        if etype is KeyboardInterrupt:
            return -1
        elif doing == "downloading installer":
            failed_message = "Downloading of '{}'{}".format(
                reading_url,
                " from S3 Endpoint {}".format(s3_endpoint) if s3_endpoint else ""
            ) if reading_url else "Connection attempt to " + region + "on port 443"
            # pylint: disable=line-too-long, superfluous-parens
            print(
                failed_message
                + """ failed.
This is usually caused by lack of routing to AWS, firewall configuration that block the connection (local or in a firewall appliance) or an incorrect web proxy configuration on this server.
Resolve the connectivity issue and run the installer again.
Learn more about connectivity issues in our documentation at """
                + DOCS_LINK
            )
        else:
            print("Error " + doing + "! Please contact AWS Support at https://console.aws.amazon.com/support")  # pylint: disable=superfluous-parens

        print("Error details: " + str(e))  # pylint: disable=superfluous-parens
        return -1
    finally:
        try:
            os.remove(filename)
        except:
            pass


def check_free_space(required):
    fs = get_fs(".")
    return required <= int(fs.available) * 1024  # the fields are in 1024-blocks


def handle_noexec_tmp():
    # get tempdir
    tmpdir = tempfile.gettempdir()

    # get mountpoint of tempdir
    tmpfs = get_fs(tmpdir)
    if not tmpfs:
        return
    mountpoint = tmpfs.mounted_on

    # check fs flags for 'noexec'
    flags = ""
    f = open("/etc/mtab")
    try:
        lines = [l.split() for l in f.readlines()]
        for line in lines:
            if line[1] == mountpoint:
                flags = line[3]
                break
    finally:
        f.close()

    if "noexec" not in flags:
        return

    # tmpdir is no noexec fs, use alternate tmp dir
    alternate_tmpdir = "/var/lib/aws-replication-agent/.tmp_install"
    if os.path.isdir(alternate_tmpdir):
        shutil.rmtree(alternate_tmpdir)

    os.makedirs(alternate_tmpdir)

    for var in ["TEMP", "TMP", "TMPDIR"]:
        os.environ[var] = alternate_tmpdir


def get_fs(directory):
    """
    get filesystem data for a directory as in 'df -P' command and parse the result
    :type directory: str
    :rtype DF # namedtuple('DF', 'filesystem blocks used available capacity mounted_on')
    """
    p = subprocess.Popen(["df", "-P", directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = p.communicate()
    if p.returncode != 0:
        return None

    res = out.splitlines()[-1]  # take the last line
    return DF(*res.split())


if __name__ == "__main__":

    parser = CustomOptionParser()
    parser.add_option("--region")
    parser.add_option("--s3-endpoint")
    parser.add_option("--version", default=False, action="store_true")
    opts, _ = parser.parse_args()

    if opts.version:
        print("AWS Replication Agent Installer version " + INSTALLER_VERSION)
        sys.exit(0)

    region = opts.region.strip() if opts.region else None
    s3_endpoint = opts.s3_endpoint.strip() if opts.s3_endpoint else None
    sys.exit(main(region, s3_endpoint))
