#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2025 LEDGER SAS
#
# SPDX-License-Identifier: MIT

# Build some eBPF programs using compilers from Debian 13
#
# Use Debian stable to build the programs. This file is expected to be updated
# for every new Debian stable release, to keep using recent-ish compilers.
#
# To use with a container:
#   podman run --rm -v "$(pwd):/work" -w /work docker.io/library/debian:13-slim ./build_debian_13.sh

set -eu

# Check the distribution
if ! grep -qe '^PRETTY_NAME="Debian GNU/Linux 13 (trixie)"$' /etc/os-release ; then
    echo >&2 "Not running Debian 13"
    exit 1
fi

# Install the compilers if needed
if ! command -v clang > /dev/null 2>&1 || ! command -v bpf-gcc > /dev/null || ! command -v llvm-objdump > /dev/null 2>&1 ; then
    export DEBIAN_FRONTEND=noninteractive
    echo "Installing compilers..."
    apt-get -q update
    apt-get -y install clang gcc-bpf llvm
fi

# Check the versions of the compilers
if ! (clang --version | grep -qe '^Debian clang version 19\.1\.7 ') ; then
    echo >&2 "Unexpected clang version:"
    clang --version >&2
    exit 1
fi
if ! (bpf-gcc --version | grep -qe '^bpf-gcc (14\.2\.0-') ; then
    echo >&2 "Unexpected bpf-gcc version:"
    bpf-gcc --version >&2
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
compile_gcc() {
    # Compile with gcc
    bpf-gcc \
        -Werror -Wall -Wextra \
        "$@"
}

compile_clang -O2 -mcpu=v1 -c atomic.c -o compiled/atomic.deb13-clangO2-v1.ebpf
compile_clang -O2 -mcpu=v4 -c atomic.c -o compiled/atomic.deb13-clangO2-v4.ebpf
compile_gcc -O2 -mcpu=v1 -c atomic.c -o compiled/atomic.deb13-gccO2-v1.ebpf
compile_gcc -O2 -mcpu=v4 -c atomic.c -o compiled/atomic.deb13-gccO2-v4.ebpf

compile_clang -O2 -c bpf_map.c -o compiled/bpf_map.deb13-clangO2.ebpf
compile_gcc -O2 -c bpf_map.c -o compiled/bpf_map.deb13-gccO2.ebpf

compile_clang -O2 -mcpu=v4 -mlittle-endian -c byte_swap.c -o compiled/byte_swap.deb13-clangO2-le.ebpf
compile_clang -O2 -mcpu=v4 -mbig-endian -c byte_swap.c -o compiled/byte_swap.deb13-clangO2-be.ebpf
compile_gcc -O2 -mcpu=v4 -masm=normal -mlittle-endian -c byte_swap.c -o compiled/byte_swap.deb13-gccO2-le.ebpf
compile_gcc -O2 -mcpu=v4 -masm=normal -mbig-endian -c byte_swap.c -o compiled/byte_swap.deb13-gccO2-be.ebpf

compile_clang -O0 -mlittle-endian -c call_saving_regs.c -o compiled/call_saving_regs.deb13-clangO0-le.ebpf
compile_clang -O2 -mlittle-endian -c call_saving_regs.c -o compiled/call_saving_regs.deb13-clangO2-le.ebpf
compile_clang -O0 -mbig-endian -c call_saving_regs.c -o compiled/call_saving_regs.deb13-clangO0-be.ebpf
compile_clang -O2 -mbig-endian -c call_saving_regs.c -o compiled/call_saving_regs.deb13-clangO2-be.ebpf
compile_gcc -O0 -mlittle-endian -c call_saving_regs.c -o compiled/call_saving_regs.deb13-gccO0-le.ebpf
compile_gcc -O2 -mlittle-endian -c call_saving_regs.c -o compiled/call_saving_regs.deb13-gccO2-le.ebpf
compile_gcc -O0 -mbig-endian -c call_saving_regs.c -o compiled/call_saving_regs.deb13-gccO0-be.ebpf
compile_gcc -O2 -mbig-endian -c call_saving_regs.c -o compiled/call_saving_regs.deb13-gccO2-be.ebpf

compile_clang -O0 -c division.c -o compiled/division.deb13-clangO0.ebpf
compile_gcc -O0 -c division.c -o compiled/division.deb13-gccO0.ebpf

compile_clang -O2 -mlittle-endian -c indirect_call.c -o compiled/indirect_call.deb13-clangO2-le.ebpf
compile_clang -O2 -mbig-endian -c indirect_call.c -o compiled/indirect_call.deb13-clangO2-be.ebpf
compile_gcc -O2 -mlittle-endian -masm=normal -mxbpf -c indirect_call.c -o compiled/indirect_call.deb13-gccO2-le.ebpf
compile_gcc -O2 -mbig-endian -masm=normal -mxbpf -c indirect_call.c -o compiled/indirect_call.deb13-gccO2-be.ebpf

compile_clang -O2 -mlittle-endian -c ld_dw.c -o compiled/ld_dw.deb13-clangO2-le.ebpf
compile_clang -O2 -mbig-endian -c ld_dw.c -o compiled/ld_dw.deb13-clangO2-be.ebpf
compile_gcc -O2 -mlittle-endian -masm=normal -mxbpf -c ld_dw.c -o compiled/ld_dw.deb13-gccO2-le.ebpf
compile_gcc -O2 -mbig-endian -masm=normal -mxbpf -c ld_dw.c -o compiled/ld_dw.deb13-gccO2-be.ebpf

compile_clang -O2 -c many_args.c -o compiled/many_args.deb13-clangO2.ebpf
compile_gcc -O2 -c many_args.c -o compiled/many_args.deb13-gccO2.ebpf

compile_clang -O0 -mlittle-endian -c relocations.c -o compiled/relocations.deb13-clangO0-le.ebpf
compile_clang -O0 -mbig-endian  -c relocations.c -o compiled/relocations.deb13-clangO0-be.ebpf
compile_gcc -O0 -mlittle-endian -masm=normal -mxbpf -c relocations.c -o compiled/relocations.deb13-gccO0-le.ebpf
compile_gcc -O0 -mbig-endian  -masm=normal -mxbpf -c relocations.c -o compiled/relocations.deb13-gccO0-be.ebpf

compile_clang -O2 -mcpu=v1 -c signed_op.c -o compiled/signed_op.deb13-clangO2-v1.ebpf
compile_clang -O2 -mcpu=v4 -c signed_op.c -o compiled/signed_op.deb13-clangO2-v4.ebpf
compile_gcc -O2 -mcpu=v1 -c signed_op.c -o compiled/signed_op.deb13-gccO2-v1.ebpf
compile_gcc -O2 -mcpu=v4 -c signed_op.c -o compiled/signed_op.deb13-gccO2-v4.ebpf

compile_clang -O0 -c single_call.c -o compiled/single_call.deb13-clangO0.ebpf
compile_gcc -O0 -c single_call.c -o compiled/single_call.deb13-gccO0.ebpf

# Disassemble the programs
for PROG in compiled/*.deb13-clang*.ebpf ; do
    llvm-objdump -rd "$PROG" > "objdump/${PROG#compiled/}.txt"
done
for PROG in compiled/*.deb13-gcc*.ebpf ; do
    bpf-objdump -rd "$PROG" > "objdump/${PROG#compiled/}.txt"
done
