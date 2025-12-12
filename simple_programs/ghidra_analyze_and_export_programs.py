#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyghidra>=2.1.0",
# ]
# ///

# SPDX-FileCopyrightText: 2025 LEDGER SAS
#
# SPDX-License-Identifier: MIT

"""Analyze compiled eBPF programs with Ghidra and export the result

Usage:
- Define GHIDRA_INSTALL_DIR environment variable to the Ghidra location
- Install PyGhidra, for example by launching:

    "${GHIDRA_INSTALL_DIR}/support/pyghidraRun"

- Launch this script from the virtual environment, for example with:

    ~/.config/ghidra/ghidra_${GHIDRA_VERSION}/venv/bin/python3 ghidra_analyze_and_export_programs.py
"""
from __future__ import annotations

import tempfile

from pathlib import Path
from typing import Final, TYPE_CHECKING

import pyghidra

pyghidra.start()

from ghidra.app.decompiler import DecompInterface
from ghidra.framework import Application
from ghidra.program.model.address import AddressSet

if TYPE_CHECKING:
    from ghidra.program.database import ProgramDB
    from ghidra.program.flatapi import FlatProgramAPI


ROOT_DIR: Final[Path] = Path(__file__).parent

GHIDRA_VERSION: Final[str] = f"{Application.getApplicationVersion()} {Application.getApplicationReleaseName()}"


def export_program(compiled_path: Path, flat_api: FlatProgramAPI, program: ProgramDB) -> None:
    listing = program.getListing()
    decomp = DecompInterface()
    decomp.openProgram(program)

    assert compiled_path.parent.name == "compiled"
    export_dir = compiled_path.parent.parent / "ghidra_export"
    export_dir.mkdir(exist_ok=True)
    with (export_dir / f"{compiled_path.name}.txt").open('w') as fout:
        print(f"Export of {compiled_path.relative_to(ROOT_DIR)} by Ghidra {GHIDRA_VERSION}", file=fout)
        print("", file=fout)
        print("Symbols:", file=fout)
        for symbol in program.getSymbolTable().getSymbolIterator():
            if symbol.getAddress().getAddressSpace().getName() in {
                ".comment",
                ".debug_frame",
                "syscall",
            }:
                # Skip the special address spaces
                continue
            print(f"  {symbol.getAddress()} {symbol.getName()}", file=fout)
        print("", file=fout)
        print("Listing:", file=fout)
        for mem_blk in program.getMemory().getBlocks():
            if mem_blk.getStart().getAddressSpace().getName() in {
                ".BTF",
                ".BTF.ext",
                ".comment",
                ".debug_abbrev",
                ".debug_addr",
                ".debug_aranges",
                ".debug_frame",
                ".debug_info",
                ".debug_line",
                ".debug_line_str",
                ".debug_loclists",
                ".debug_rnglists",
                ".debug_str",
                ".debug_str_offsets",
                ".llvm_addrsig",
                ".rel.BTF.ext",
                ".rel.debug_addr",
                ".rel.debug_aranges",
                ".rel.debug_frame",
                ".rel.debug_info",
                ".rel.debug_line",
                ".rel.debug_loclists",
                ".rel.debug_rnglists",
                ".rel.debug_str_offsets",
                ".rel.text",
                ".shstrtab",
                ".strtab",
                ".symtab",
                "_elfHeader",
                "_elfSectionHeaders",
                "syscall",
            }:
                # Skip the special address spaces
                continue
            print(f"  Memory Block {mem_blk.getName()} @{mem_blk.getStart()}..{mem_blk.getEnd()}", file=fout)
            for cu in listing.getCodeUnits(AddressSet(mem_blk.getAddressRange()), True):
                symbols_at_addr = program.getSymbolTable().getSymbols(cu.getAddress())
                for symbol in symbols_at_addr:
                    print(f"    {symbol.getName()}:", file=fout)
                if program.getMemory().isExternalBlockAddress(cu.getAddress()):
                    if symbols_at_addr:
                        # Only show EXTERNAL address when a symbol is defined
                        print(f"      {cu.getAddress()} (external) {cu.toString()}", file=fout)
                else:
                    print(f"      {cu.getAddress()} {bytes(cu.getBytes()).hex()} {cu.toString()}", file=fout)
            print("", file=fout)

        print("Decompiled functions:", file=fout)
        for fct in listing.getFunctions(True):
            print("", file=fout)
            print(f"/* Function {fct.getName()} at {fct.getEntryPoint()} */", file=fout)
            decomp_result = decomp.decompileFunction(fct, 10000, None)
            print(decomp_result.getDecompiledFunction().getC().strip("\n"), file=fout)



def analyze_and_export_all_programs() -> None:
    """Analyze all eBPF programs and export them"""
    with tempfile.TemporaryDirectory(prefix="ghidra-prj-") as proj_dir:
        if hasattr(pyghidra, "open_project"):
            # Ghidra 12.0 new API
            project = pyghidra.open_project(proj_dir, "my_project", create=True)

        for compiled_path in sorted((ROOT_DIR / "compiled").glob("*.ebpf")):
            print(f"Analyzing {compiled_path.relative_to(ROOT_DIR)}")
            if hasattr(pyghidra, "open_project"):
                loaded_program = pyghidra.program_loader().project(project).source(str(compiled_path)).load()
                program = loaded_program.getPrimaryDomainObject()
                from ghidra.program.flatapi import FlatProgramAPI
                flat_api = FlatProgramAPI(program)

                # Analyze the program
                pyghidra.analyze(program)
                export_program(compiled_path, flat_api, program)
            else:
                # Old API before Ghidra 12.0
                with pyghidra.open_program(compiled_path, project_location=proj_dir) as flat_api:
                    program = flat_api.getCurrentProgram()
                    export_program(compiled_path, flat_api, program)


if __name__ == "__main__":
    analyze_and_export_all_programs()
