#!/usr/bin/env sh

# SPDX-FileCopyrightText: 2025 LEDGER SAS
#
# SPDX-License-Identifier: MIT

# Build some eBPF programs using old compilers from Alpine Linux 3.10
#
# clang<19.1 used a different encoding for instruction CALLX (indirect call).
# Use a Alpine 3.10 to compile programs with an old version of clang.
#
# To use with a container:
#   podman run --rm -v "$(pwd):/work" -w /work docker.io/library/alpine:3.10 ./build_alpine_3_10.sh

set -eu

# Check the distribution
if ! grep -qe '^PRETTY_NAME="Alpine Linux v3\.10"$' /etc/os-release ; then
    echo >&2 "Not running Alpine Linux 3.10"
    exit 1
fi

# Install the compilers if needed
if ! command -v clang > /dev/null 2>&1 || ! command -v llvm-objdump > /dev/null 2>&1 ; then
    export DEBIAN_FRONTEND=noninteractive
    echo "Installing compilers..."
    apk --no-cache --update add clang llvm
fi



# Check the versions of the compilers
if ! (clang --version | grep -qe '^Alpine clang version 8\.0\.0 ') ; then
    echo >&2 "Unexpected clang version:"
    clang --version >&2
    exit 1
fi

mkdir -p compiled objdump

# From now on, display the executed commands
set -x

# Compile some programs, with warnings and debug information
compile_clang() {
    # Compile with clang
    clang -target bpf \
        -Werror -Wall -Wextra \
        "$@"
}

compile_clang -O2 -mlittle-endian -c indirect_call.c -o compiled/indirect_call.alp310-clangO2-le.ebpf
compile_clang -O2 -mbig-endian -c indirect_call.c -o compiled/indirect_call.alp310-clangO2-be.ebpf

# Disassemble the programs
for PROG in compiled/*.alp310-clang*.ebpf ; do
    llvm-objdump -r -d "$PROG" > "objdump/${PROG#compiled/}.txt"
done
