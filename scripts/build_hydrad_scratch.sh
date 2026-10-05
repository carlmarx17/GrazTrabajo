#!/usr/bin/env bash
# Copy vendor/HYDRAD to a scratch directory and build Initial_Conditions.exe and HYDRAD.exe
# with beam heating.  The run scripts modify the copy (configuration files, Results_*),
# never vendor/HYDRAD itself.  The source lists are read from the upstream .bat scripts.
#
#   scripts/build_hydrad_scratch.sh /path/to/scratch/HYDRAD
#
# Flags: BEAM_HEATING is not defined in the shipped config.h; gamma.cpp needs <cstdlib> and
# <cstring> with clang (docs/01_hydrad_code.md).  Radiation physics stays as shipped
# (power-law losses, no optically thick chromosphere).
set -euo pipefail
dest=${1:?usage: build_hydrad_scratch.sh <destination directory>}
repo=$(cd "$(dirname "$0")/.." && pwd)
CXX=${CXX:-c++}
FLAGS=(-O3 -std=gnu++14 -DBEAM_HEATING -include cstdlib -include cstring -w)

mkdir -p "$dest"
rsync -a --exclude 'Results*' --exclude '*.exe' "$repo/vendor/HYDRAD/" "$dest/"

build() {  # <component dir> <.bat file>: compile from build_scripts/, as the .bat does
    local dir="$dest/$1"
    local sources out
    sources=$(grep -o '\.\./[^ ]*\.cpp' "$dir/build_scripts/$2" | tr '\n' ' ')
    out=$(grep -o '\-o [^ ]*\.exe' "$dir/build_scripts/$2" | awk '{print $2}')
    (cd "$dir/build_scripts" && $CXX "${FLAGS[@]}" $sources -o "$out")
    echo "built $(cd "$dir/build_scripts" && cd "$(dirname "$out")" && pwd)/$(basename "$out")"
}

build Initial_Conditions build_initial_conditions.bat
build HYDRAD build_HYDRAD.bat
