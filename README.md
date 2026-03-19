<!--
SPDX-FileCopyrightText: 2025 LEDGER SAS

SPDX-License-Identifier: MIT
-->

# Ghidra eBPF tests

This repository aims at testing the [eBPF](https://ebpf.io/) support in [Ghidra](https://github.com/NationalSecurityAgency/ghidra)

## What is eBPF?

As the [official documentation](https://ebpf.io/what-is-ebpf/) states: eBPF is a revolutionary technology with origins in the Linux kernel that can run sandboxed programs in a privileged context such as the operating system kernel.

In short, programs written in C or Rust are compiled into a specific bytecode (called *eBPF bytecode*) that can be executed in a secure way, thanks to strong restrictions around what programs can do.

eBPF was first introduced in the Linux kernel to filter network packets and monitor the performance.
Later, the [uBPF project](https://github.com/iovisor/ubpf) provided an implementation able to run eBPF programs in userspace.
This project was used by Microsoft to provide [eBPF for Windows](https://github.com/microsoft/ebpf-for-windows), an eBPF implementation that runs on top of Windows.
This project was rewritten in Rust in a project named [RBPF](https://github.com/qmonnet/rbpf).
RBPF was later [forked](https://github.com/solana-labs/rbpf) and used by [Solana](https://solana.com/) to implement smart contract (called Solana Programs).
Solana then changed the bytecode so much it was renamed SBF (Solana Bytecode Format) and the virtual machine running it [sBPF](https://github.com/anza-xyz/sbpf).
In October 2025, this project began migrating back to eBPF (cf. [SIMD-0377](https://github.com/solana-foundation/solana-improvement-documents/pull/377)).

Many projects are using eBPF programs in one way or another.
There are some lists on the Internet ([here](https://ebpf.io/applications/), [here](https://github.com/mikeroyal/eBPF-Guide/blob/abc9295bdd2497947a38a888ccccb2008f03a382/README.md#ebpf-tools--libraries), etc.).
Some datasets of compiled eBPF program exist on the Internet, such as <https://github.com/vbpf/ebpf-samples>.

The bytecode format got standardised as IETF [RFC 9669: BPF Instruction Set Architecture (ISA)](https://www.rfc-editor.org/rfc/rfc9669.html) in 2024.
Before this standardisation process, there were 4 versions, described for example in [a blog post detailing eBPF Instruction Set Extensions](https://pchaigno.github.io/bpf/2021/10/20/ebpf-instruction-sets.html).
The RFC standardised version 4.

The first compilers supported eBPF target were in [clang/LLVM 3.7](https://releases.llvm.org/3.7.0/docs/ReleaseNotes.html) in 2015 and [gcc 10.1.0](https://gcc.gnu.org/gcc-10/) in 2020 ([documentation](https://gcc.gnu.org/onlinedocs/gcc/eBPF-Options.html), [wiki](https://gcc.gnu.org/wiki/BPFBackEnd)).
<!--
LLVM commit: https://github.com/llvm/llvm-project/commit/e4c8c807bb609daa9be3fb9977703355b119fe8c reviewed in https://reviews.llvm.org/D6494
gcc commit: https://github.com/gcc-mirror/gcc/commit/91dfef9610b8844c62dc7186a9aea9a6aca9805c
-->

Programs are compiled to [ELF files](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format) with specific relocations documented in [Linux kernel's documentation](https://docs.kernel.org/bpf/llvm_reloc.html).
When these programs are loaded into Linux kernel, they are first decoded by a userspace library called `libbpf`, located in [kernel's directory `tools/lib/bpf/`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/lib/bpf) and on [GitHub `libbpf/libbpf`](https://github.com/libbpf/libbpf).
This library uses [syscall `bpf`](https://man7.org/linux/man-pages/man2/bpf.2.html) to transmit the BPF code to the kernel.
At this point, several kernel components get involved:

- The eBPF Verifier in [`kernel/bpf/verifier.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/kernel/bpf/verifier.c), which ensures loaded programs will not break some security properties.
- The eBPF Interpreter, mainly implemented in [`kernel/bpf/core.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/kernel/bpf/core.c).
- Just-In-Time (JIT) compilers for some processor architectures ([`arch/x86/net/bpf_jit_comp.c` for x86](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/arch/x86/net/bpf_jit_comp.c), [`arch/arm64/net/bpf_jit_comp.c` for ARM64](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/arch/arm64/net/bpf_jit_comp.c)).

Project [uBPF](https://github.com/iovisor/ubpf) uses a different kind of verification mechanism: instead of trying to determine every possible runtime behaviour of a program before running it, it mainly validates instructions are correctly encoded (cf. [function `validate`](https://github.com/iovisor/ubpf/blob/8c0dc65ddb7dd2eff53aed958b1a2f9424855cdb/vm/ubpf_vm.c#L1434)) and checks access at runtime (cf. [this comment around macro `BOUNDS_CHECK_LOAD`](https://github.com/iovisor/ubpf/blob/8c0dc65ddb7dd2eff53aed958b1a2f9424855cdb/vm/ubpf_vm.c#L923-L927)).

Some projects do not rely on `libbpf` to load eBPF programs.
For example [Rust project Aya](https://github.com/aya-rs/aya) directly interacts with syscall `bpf`.

## What is Ghidra?

[Ghidra](https://github.com/NationalSecurityAgency/ghidra) is a powerful free and open source reverse engineering tool able to decompile many processor instruction set architectures (ARM, PowerPC, x86...).
It provides an interactive graphical user interface as well as a headless analyzer (able to execute "Ghidra scripts") to automate some analyses.

In 2025, [Ghidra 11.3](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_11.3_build/Ghidra/Configurations/Public_Release/src/global/docs/WhatsNew.md#pyghidra) integrated PyGhidra to extent to capabilities of the headless mode, enabling to drive Ghidra from a Python script.

In 2019, someone published a Ghidra extension adding support for eBPF architecture to Ghidra: <https://github.com/Nalen98/eBPF-for-Ghidra>.
In 2022 this support was submitted upstream (in [Pull Request #4378](https://github.com/NationalSecurityAgency/ghidra/pull/4378)) and integrated to [Ghidra 10.3](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_10.3_build) in 2023.

## What is this project about?

While analyzing some eBPF programs, I encountered several bugs in the Ghidra support: wrong semantics of some instructions, wrong decoding of `CALL`, missing instructions, unsupported relocations, etc.
To better diagnose these issues and ensure the fixes did not introduce regressions, I built a set of small eBPF programs.

This project contains these programs and some scripts helping analysing them. For each program:

- a source code (in C) is provided ;
- several compiled programs are provided (as some compilers changed the way some instructions were encoded) ;
- a textual export from Ghidra analysis, for each compiled program.

This textual export is designed to be readable and understandable by humans while being automatically generated by Ghidra.
Its content depends on the version of Ghidra being used (as some bugs were fixed) and using a textual line-based format makes studying evolutions easier.

## Installing an eBPF compiler

On Debian-based Linux distributions, eBPF support is available in packages [`clang`](https://packages.debian.org/sid/clang) and [`gcc-bpf`](https://packages.debian.org/sid/gcc-bpf).

They enable compiling C programs with:

```sh
clang -O2 -target bpf -mcpu=v4 -c my_prog.c -o my_prog.ebpf
```

or:

```sh
bpf-gcc -O2 -mcpu=v4 -c my_prog.c -o my_prog.ebpf
```

## Using PyGhidra

eBPF programs can be loaded by Ghidra.
The way the eBPF support was integrated make this intuitive: eBPF programs can be loaded like any other programs.

Since Ghidra 11.3, a Python library named pyghidra has been provided to help performing automated actions in headless mode (without any graphical user interface).
Some documentation were written:

- [PyGhidra feature README file](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_11.3.1_build/Ghidra/Features/PyGhidra/README.md)
- [PyGhidra py README file](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.0_build/Ghidra/Features/PyGhidra/src/main/py/README.md)
- [Getting Started instructions, PyGhidra Mode](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.0_build/GhidraDocs/GettingStarted.md#pyghidra-mode)
- [Example of PyGhidra-specific functionality (`PyGhidraBasics.py`)](https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.0_build/Ghidra/Features/PyGhidra/ghidra_scripts/PyGhidraBasics.py)

PyGhidra is available as a [Python package published on PyPI](https://pypi.org/project/pyghidra/).
This means it can be installed with:

```sh
pip install pyghidra
```

This nonetheless requires a working Ghidra installation, referenced with environment variable `GHIDRA_INSTALL_DIR`.

To install PyGhidra in a Debian 13 container, the following commands can be used:

```sh
# Install dependencies
sudo apt-get update
sudo apt-get install openjdk-25-jdk-headless python3 python3-pip python3-venv unzip wget

# Download Ghidra from https://github.com/NationalSecurityAgency/ghidra/releases
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.0_build/ghidra_12.0_PUBLIC_20251205.zip
SHA256=af43e8cfb2fa4490cf6020c3a2bde25c159d83f45236a0542688a024e8fc1941
echo "${SHA256}  ghidra_12.0_PUBLIC_20251205.zip" | sha256sum --check
unzip ghidra_12.0_PUBLIC_20251205.zip

# Install PyGhidra from the downloaded release
echo y | ./ghidra_12.0_PUBLIC/support/pyghidraRun

# Export to a variable Ghidra's location
export GHIDRA_INSTALL_DIR="$(pwd)/ghidra_12.0_PUBLIC"
```

This installed PyGhidra in a Python virtual environment located in `~/.config/ghidra/ghidra_12.0_PUBLIC/venv`.
It can be used to launch an interactive Python:

```sh
~/.config/ghidra/ghidra_12.0_PUBLIC/venv/bin/python3
```

From there, analyzing an eBPF program can be done with few lines of code:

```python
from pathlib import Path

import pyghidra

pyghidra.start()

GHIDRA_PRJ_PATH = Path("/tmp/ghidra-test-prj")
GHIDRA_PRJ_PATH.mkdir(exist_ok=True)

project = pyghidra.open_project(str(GHIDRA_PRJ_PATH), "test-project", create=True)
loaded_program = pyghidra.program_loader().project(project).source("my_program.ebpf").load()
program = loaded_program.getPrimaryDomainObject()
from ghidra.program.flatapi import FlatProgramAPI
flat_api = FlatProgramAPI(program)

# Analyze the program
pyghidra.analyze(program)

# List all available symbols
print(list(program.getSymbolTable().getSymbolIterator()))

# Disassemble a function, showing its code units (assembly statements)
listing = program.getListing()
fct = listing.getFunctionAt(program.getSymbolTable().getGlobalSymbols("some_function")[0].getAddress())
for cu in listing.getCodeUnits(fct.getBody(), True):
    print(f"{cu.getAddress()} {bytes(cu.getBytes()).hex()} {cu.toString()}")

# Decompile a function, printing pseudo-code
import ghidra.app.decompiler.DecompInterface
decomp = ghidra.app.decompiler.DecompInterface()
decomp.openProgram(program)
decomp_result = decomp.decompileFunction(fct, 10000, None)
print(decomp_result.getDecompiledFunction().getC())
```

This repository includes a Python script which automates analyzing some eBPF programs and saving the disassembler and decompiler outputs: [`simple_programs/ghidra_analyze_and_export_programs.py`](./simple_programs/ghidra_analyze_and_export_programs.py).

This script is compatible with [uv](https://docs.astral.sh/uv/), meaning it can be launch with:

```sh
export GHIDRA_INSTALL_DIR=/path/to/ghidra_12.0_PUBLIC
uv run simple_programs/ghidra_analyze_and_export_programs.py
```

## Merged Pull Requests

Here are some Pull Requests I did to Ghidra:

Merged in [Ghidra 11.4.1](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_11.4.1_build) (2025-07-31):

- [#7929: Fix eBPF CALL operand decoding](https://github.com/NationalSecurityAgency/ghidra/pull/7929)
- [#7979: Fix eBPF zero-extend load instructions](https://github.com/NationalSecurityAgency/ghidra/pull/7979)
- [#7982: Add eBPF v4 signed extension](https://github.com/NationalSecurityAgency/ghidra/pull/7982) 
- [#7985: Fix the semantics of eBPF byte swap instructions](https://github.com/NationalSecurityAgency/ghidra/pull/7985)

Merged in [Ghidra 12.0](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.0_build) (2025-08-12):

- [#7972: Add eBPF instruction CALLX for indirect calls](https://github.com/NationalSecurityAgency/ghidra/pull/7972)

Not merged yet:

- [#8721: Fix disassembly of eBPF atomic instructions and semantics of compare-and-exchange](https://github.com/NationalSecurityAgency/ghidra/pull/8721)
- [#8860: Process more ELF relocation kinds for eBPF programs](https://github.com/NationalSecurityAgency/ghidra/pull/8860)

## License

This project is primarily licensed under the **MIT License**. This applies to the core source code and all documentation.

### Third-Party Components & Licenses

To ensure compatibility and respect for upstream work, some components are included or used under different permissive licenses:

* **`bpf_maps.c`**: Licensed under **MIT License**, **GPL-2.0-only WITH Linux-syscall-note License** and **LGPL-2.1-only OR BSD-2-Clause License**.
* **`ghidra_analyze_and_export_programs.py`**: This component relies on [PyGhidra](https://pypi.org/project/pyghidra/), which is licensed under the **Apache-2.0 License** (consistent with the Ghidra project).

### Compliance

* Full license texts are available in the [LICENSES/](./LICENSES) directory.
* In accordance with best practices, individual files contain **SPDX-License-Identifier** headers to clarify their specific licensing terms.
