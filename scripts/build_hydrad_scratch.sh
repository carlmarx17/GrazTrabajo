#!/usr/bin/env bash
# Copy vendor/HYDRAD to a scratch directory and build Initial_Conditions.exe and HYDRAD.exe
# with beam heating.  The run scripts modify the copy (configuration files, Results_*),
# never vendor/HYDRAD itself.  The source lists are read from the upstream .bat scripts.
#
#   scripts/build_hydrad_scratch.sh /path/to/scratch/HYDRAD [--set NAME=VALUE ...] \
#       [--linear-restriction] [--no-conservation]
#
# --set changes an existing #define of HYDRAD/source/config.h.  The core pilot uses
# --set SAFETY_CONDUCTION=0.2: with the shipped 1.0 the explicit conduction step goes
# unstable when the second pulse heats the dense, evaporated corona (grid-scale
# oscillations of T_e, runaway refinement, NaN); 0.2 keeps conservation and stays smooth,
# while 0.5 is only marginal (docs/07_core_pilot_hydrad.md, Section 2.2).
#
# Options (numerical, see the HYDRAD user guide, Section 7.3): --linear-restriction interpolates
# newly refined cells linearly instead of with cubic polynomials; --no-conservation drops the
# correction that forces refined cells to sum to the parent's conserved quantities.  Together
# they suppress grid-scale oscillations that otherwise make dense two-pulse runs intractable
# (docs/00, Section 4); both act like a small numerical diffusion.
#
# Flags: BEAM_HEATING is not defined in the shipped config.h; gamma.cpp needs <cstdlib> and
# <cstring> with clang (docs/01_hydrad_code.md).  Radiation physics stays as shipped
# (power-law losses, no optically thick chromosphere).
set -euo pipefail
dest=${1:?usage: build_hydrad_scratch.sh <destination directory> [--set NAME=VALUE ...] [--linear-restriction] [--no-conservation]}
shift
linear=0; nocons=0; sets=()
while [ $# -gt 0 ]; do
    case $1 in
        --set) sets+=("${2:?--set needs NAME=VALUE}"); shift ;;
        --linear-restriction) linear=1 ;;
        --no-conservation) nocons=1 ;;
        *) echo "unknown option $1" >&2; exit 2 ;;
    esac
    shift
done
repo=$(cd "$(dirname "$0")/.." && pwd)
CXX=${CXX:-c++}
FLAGS=(-O3 -std=gnu++14 -DBEAM_HEATING -include cstdlib -include cstring -w)

mkdir -p "$dest"
rsync -a --exclude 'Results*' --exclude '*.exe' "$repo/vendor/HYDRAD/" "$dest/"
cfg="$dest/HYDRAD/source/config.h"
if [ $linear = 1 ]; then
    sed -i.bak 's|^// \*\*\*\* End of Grid \*\*\*\*|#define LINEAR_RESTRICTION\n&|' "$cfg"
fi
if [ $nocons = 1 ]; then
    sed -i.bak '/^#define ENFORCE_CONSERVATION/d' "$cfg"
fi
for kv in ${sets[@]+"${sets[@]}"}; do
    name=${kv%%=*}; value=${kv#*=}
    grep -q "^#define $name " "$cfg" || { echo "no #define $name in config.h" >&2; exit 2; }
    sed -i.bak "s|^#define $name .*|#define $name $value|" "$cfg"
done
rm -f "$cfg.bak"

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
