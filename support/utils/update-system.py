#! /usr/bin/env nix-shell
#! nix-shell -i python -p python rustUnstable.cargo git
#! nix-shell -I nixpkgs=https://github.com/NixOS/nixpkgs/archive/125ffff089b6bd360c82cf986d8cc9b17fc2e8ac.tar.gz

import os
import subprocess
import shlex
import sys
import re
import time
import getopt
from itertools import chain

repo = " -I nixpkgs=https://github.com/NixOS/nixpkgs/archive/125ffff089b6bd360c82cf986d8cc9b17fc2e8ac.tar.gz"

def query_yes_no(question, default="no"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

result = query_yes_no(
"This script will update the dependencies of all your components and the rust registry.\n\
Proceed?")

if result == False:
  exit()

def generate_component_name( path ):
  name_list = path[17:].split("/")
  return '_'.join(map(str, name_list))

# update all the components via cargo
print "\n[*] Updating every Cargo.toml via cargo"
paths = ('../../components', '../../support')
for root, dirs, files in chain.from_iterable(os.walk(path) for path in paths):
  cmd = "cargo generate-lockfile --manifest-path " + root + "/Cargo.toml"
  args = shlex.split(cmd)
  if "Cargo.toml" in files:
    print "[ ] - " + root+"/Cargo.toml"
    output, error = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()

# get crates.io head rev
print "[*] Obtaining new crates.io HEAD revision"
cmd = "git ls-remote git://github.com/rust-lang/crates.io-index.git refs/heads/master"
args = shlex.split(cmd)
head_blob, error = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
head_rev = head_blob.split('\t')[0]

# update rust-packages
print "[*] Inserting new crates.io HEAD revision into rustRegistry"
rustRegistry = "../rust-packages.nix"
find = r"^.*rev = .*$";
replace = "rev = \"%s\";" % head_rev
subprocess.call(["sed","-i","s/"+find+"/"+replace+"/g",rustRegistry])
find = r"^.*version = .*$";
replace = "version = \"%s\";" % time.strftime('%Y-%m-%d')
subprocess.call(["sed","-i","s/"+find+"/"+replace+"/g",rustRegistry])

# build rustRegistry to get the sha256, then build it again...
print "[*] Checking for new rustRegistry sha256"
cmd =  "nix-build --argstr debug true -A support.rustRegistry" + repo
args = shlex.split(cmd)
output, error = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE, cwd = "../../").communicate()
if error:
  if re.search('.*has wrong length for hash type.*', error):
    print error
    exit()
  if re.search('.*invalid base-32 hash.*', error):
    print error
    exit()
  m = re.search('.*hash.*(\w{52}).*when.*', error)
  if m:
    found = m.group(1)
    print "[*] Inserting latest sha256 into rustRegistry"
    find = r"^.*sha256 = .*$";
    replace = "  sha256 = \"%s\";" % found
    subprocess.call(["sed","-i","s/"+find+"/"+replace+"/g",rustRegistry])
    print "[*] Building rustRegistry with latest sha256"
    cmd =  "nix-build --argstr debug true -A support.rustRegistry" + repo
    args = shlex.split(cmd)
    output, error = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE, cwd = "../../").communicate()


print "[*] Checking Rust components for new depsSha256"
for root, dirs, files in os.walk("../../components"):
  if "Cargo.toml" in files:
    name = generate_component_name(root)
    cmd =  "nix-build --argstr debug true -A components." + name  + repo
    print "[ ] - " + name + " path: " + root
    args = shlex.split(cmd)
    output, error = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE, cwd = "../../").communicate()
    if error:
      if re.search('.*not found', error):
        print error + "\nerror: folder hierarchy != attribute name in components/default.nix. Please fix it, commit it, then run again."
        exit()
      if re.search('.*has wrong length for hash type.*', error):
        print error
        exit()
      if re.search('.*invalid base-32 hash.*', error):
        print error
        exit()
      m = re.search('.*hash.*(\w{52}).*when.*', error)
      if m:
        found = m.group(1)
        print "[!] -- " + name + " has a new depsSha256"
        find = r"^.*depsSha256 = .*$";
        replace = "  depsSha256 = \"%s\";" % found
        subprocess.call(["sed","-i","s/"+find+"/"+replace+"/g",root+"/default.nix"])
        #output, error = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE, cwd = "../../").communicate()

# for root, dirs, files in os.walk("../vm"):
#     if "Cargo.toml" in files:
#       name = os.path.basename(root)
#       cmd = "nix-build --argstr debug true -A vm" + repo
#       print "[ ] - " + name
#       print cmd
#       args = shlex.split(cmd)
#       output, error = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE, cwd = "../vm").communicate()
#       if error:
#         print error
#         if re.search('.*has wrong length for hash type.*', error):
#           print error
#           exit()
#         if re.search('.*invalid base-32 hash.*', error):
#           exit()
#         m = re.search('.*hash.*(\w{52}).*when.*', error)
#         if m:
#           print "[!] -- found new depsSha256... building "
#           found = m.group(1)
#           find = r"^.*depsSha256 = .*$";
#           if name == "vm":
#             space = "    "
#           else:
#             space = "  "
#           replace = space + "depsSha256 = \"%s\";" % found
#           subprocess.call(["sed","-i","s/"+find+"/"+replace+"/g",root+"/default.nix"])
#           output, error = subprocess.Popen(args, stdout = subprocess.PIPE, stderr= subprocess.PIPE, cwd = "../../").communicate()

print "[*] Done"
