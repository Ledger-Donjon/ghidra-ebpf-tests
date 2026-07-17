#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyghidra>=3.0.0",
# ]
# ///

# SPDX-FileCopyrightText: 2026 LEDGER SAS
#
# SPDX-License-Identifier: MIT

"""Emulate call_saving_regs to ensure the registers get correctly saved

Usage:
- Define GHIDRA_INSTALL_DIR environment variable to the Ghidra location
- Install PyGhidra, for example by launching:

    "${GHIDRA_INSTALL_DIR}/support/pyghidraRun"

- Launch this script from the virtual environment, for example with:

    ~/.config/ghidra/ghidra_${GHIDRA_VERSION}/venv/bin/python3 ghidra_emulate_call_saving_regs.py

Example of broken output (Ghidra 12.1.2), where CALL does not modify the stack:

    Emulating compiled/call_saving_regs.deb13-clangO2-be.ebpf
    ram:00100050 (MOV R1,0x1              ) r0=0x0 r1=0x0 r2=0x0 r3=0x0 r4=0x0 r5=0x0 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100058 (MOV R8,0x8              ) r0=0x0 r1=0x1 r2=0x0 r3=0x0 r4=0x0 r5=0x0 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100060 (MOV R3,0x3              ) r0=0x0 r1=0x1 r2=0x0 r3=0x0 r4=0x0 r5=0x0 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100068 (MOV R5,0x5              ) r0=0x0 r1=0x1 r2=0x0 r3=0x3 r4=0x0 r5=0x0 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100070 (MOV R7,0x7              ) r0=0x0 r1=0x1 r2=0x0 r3=0x3 r4=0x0 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100078 (MOV R2,0x2              ) r0=0x0 r1=0x1 r2=0x0 r3=0x3 r4=0x0 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100080 (MOV R9,0x9              ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x0 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100088 (MOV R4,0x4              ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x0 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100090 (MOV R6,0x6              ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100098 (CALL 0x00100000         ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100000 (MOV R0,0x10             ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100008 (MOV R7,0x17             ) r0=0x10 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100010 (MOV R2,0x12             ) r0=0x10 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100018 (MOV R4,0x14             ) r0=0x10 r1=0x1 r2=0x12 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100020 (MOV R6,0x16             ) r0=0x10 r1=0x1 r2=0x12 r3=0x3 r4=0x14 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100028 (MOV R1,0x11             ) r0=0x10 r1=0x1 r2=0x12 r3=0x3 r4=0x14 r5=0x5 r6=0x16 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100030 (MOV R8,0x18             ) r0=0x10 r1=0x11 r2=0x12 r3=0x3 r4=0x14 r5=0x5 r6=0x16 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100038 (MOV R3,0x13             ) r0=0x10 r1=0x11 r2=0x12 r3=0x3 r4=0x14 r5=0x5 r6=0x16 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100040 (MOV R5,0x15             ) r0=0x10 r1=0x11 r2=0x12 r3=0x13 r4=0x14 r5=0x5 r6=0x16 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100048 (EXIT                    ) r0=0x10 r1=0x11 r2=0x12 r3=0x13 r4=0x14 r5=0x15 r6=0x16 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    Emulation complete, result is 0x10
    Test FAIL compiled/call_saving_regs.deb13-clangO2-be.ebpf: unexpected result 0x10

Example of successful output:

    Emulating compiled/call_saving_regs.deb13-clangO2-le.ebpf
    ram:00100050 (MOV R1,0x1              ) r0=0x0 r1=0x0 r2=0x0 r3=0x0 r4=0x0 r5=0x0 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100058 (MOV R8,0x8              ) r0=0x0 r1=0x1 r2=0x0 r3=0x0 r4=0x0 r5=0x0 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100060 (MOV R3,0x3              ) r0=0x0 r1=0x1 r2=0x0 r3=0x0 r4=0x0 r5=0x0 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100068 (MOV R5,0x5              ) r0=0x0 r1=0x1 r2=0x0 r3=0x3 r4=0x0 r5=0x0 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100070 (MOV R7,0x7              ) r0=0x0 r1=0x1 r2=0x0 r3=0x3 r4=0x0 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100078 (MOV R2,0x2              ) r0=0x0 r1=0x1 r2=0x0 r3=0x3 r4=0x0 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100080 (MOV R9,0x9              ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x0 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100088 (MOV R4,0x4              ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x0 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100090 (MOV R6,0x6              ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x0 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100098 (CALL 0x00100000         ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x0 StkTop-8280=0x0
    ram:00100000 (MOV R0,0x10             ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100008 (MOV R7,0x17             ) r0=0x10 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100010 (MOV R2,0x12             ) r0=0x10 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100018 (MOV R4,0x14             ) r0=0x10 r1=0x1 r2=0x12 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100020 (MOV R6,0x16             ) r0=0x10 r1=0x1 r2=0x12 r3=0x3 r4=0x14 r5=0x5 r6=0x6 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100028 (MOV R1,0x11             ) r0=0x10 r1=0x1 r2=0x12 r3=0x3 r4=0x14 r5=0x5 r6=0x16 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100030 (MOV R8,0x18             ) r0=0x10 r1=0x11 r2=0x12 r3=0x3 r4=0x14 r5=0x5 r6=0x16 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100038 (MOV R3,0x13             ) r0=0x10 r1=0x11 r2=0x12 r3=0x3 r4=0x14 r5=0x5 r6=0x16 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100040 (MOV R5,0x15             ) r0=0x10 r1=0x11 r2=0x12 r3=0x13 r4=0x14 r5=0x5 r6=0x16 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100048 (EXIT                    ) r0=0x10 r1=0x11 r2=0x12 r3=0x13 r4=0x14 r5=0x15 r6=0x16 r10=0xffa8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000a0 (LSH R7,0x8              ) r0=0x10 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000a8 (LSH R8,0xc              ) r0=0x10 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000b0 (ADD R8,R7               ) r0=0x10 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000b8 (LSH R0,0x4              ) r0=0x10 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000c0 (XOR R0,0x100            ) r0=0x100 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000c8 (ADD R0,R9               ) r0=0x0 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000d0 (LSH R0,0x10             ) r0=0x9 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000d8 (ADD R0,R8               ) r0=0x90000 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000e0 (LSH R6,0x4              ) r0=0x98700 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x6 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000e8 (ADD R6,R5               ) r0=0x98700 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x60 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000f0 (ADD R6,R0               ) r0=0x98700 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x65 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:001000f8 (LSH R3,0x8              ) r0=0x98700 r1=0x1 r2=0x2 r3=0x3 r4=0x4 r5=0x5 r6=0x98765 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100100 (LSH R4,0xc              ) r0=0x98700 r1=0x1 r2=0x2 r3=0x300 r4=0x4 r5=0x5 r6=0x98765 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100108 (ADD R4,R3               ) r0=0x98700 r1=0x1 r2=0x2 r3=0x300 r4=0x4000 r5=0x5 r6=0x98765 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100110 (LSH R6,0x10             ) r0=0x98700 r1=0x1 r2=0x2 r3=0x300 r4=0x4300 r5=0x5 r6=0x98765 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100118 (ADD R6,R4               ) r0=0x98700 r1=0x1 r2=0x2 r3=0x300 r4=0x4300 r5=0x5 r6=0x987650000 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100120 (LSH R2,0x4              ) r0=0x98700 r1=0x1 r2=0x2 r3=0x300 r4=0x4300 r5=0x5 r6=0x987654300 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100128 (ADD R2,R1               ) r0=0x98700 r1=0x1 r2=0x20 r3=0x300 r4=0x4300 r5=0x5 r6=0x987654300 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100130 (ADD R2,R6               ) r0=0x98700 r1=0x1 r2=0x21 r3=0x300 r4=0x4300 r5=0x5 r6=0x987654300 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100138 (MOV R0,R2               ) r0=0x98700 r1=0x1 r2=0x987654321 r3=0x300 r4=0x4300 r5=0x5 r6=0x987654300 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    ram:00100140 (EXIT                    ) r0=0x987654321 r1=0x1 r2=0x987654321 r3=0x300 r4=0x4300 r5=0x5 r6=0x987654300 r10=0x10ff8 StkTop-4176=0x1000a0 StkTop-8280=0x1
    Emulation complete, result is 0x987654321
    Test OK compiled/call_saving_regs.deb13-clangO2-le.ebpf

This is being fixed with:
https://github.com/NationalSecurityAgency/ghidra/pull/9381 ("Emulate function
frames in eBPF specifications")
"""
from __future__ import annotations

import tempfile

from pathlib import Path
from typing import Final, TYPE_CHECKING

import pyghidra

pyghidra.start()

from java.math import BigInteger
from jpype import JLong
from ghidra.pcode.emu import PcodeEmulator, EmulatorUtilities
from ghidra.program.model.lang import RegisterValue
from ghidra.program.model.symbol import SymbolUtilities

if TYPE_CHECKING:
    from ghidra.program.model.listing import Program
    from ghidra.util.task import TaskMonitor


ROOT_DIR: Final[Path] = Path(__file__).parent


def emulate_function(program: Program, fct_name: str, monitor: TaskMonitor) -> int | None:
    ram = program.getAddressFactory().getDefaultAddressSpace()
    listing = program.getListing()
    fct_sym = SymbolUtilities.getLabelOrFunctionSymbol(program, fct_name, None)
    if fct_sym is None:
        print(f"Error: function {fct_name!r} not found")
        return None
    # Create an emulator
    lang = program.getLanguage()
    emu = PcodeEmulator(lang)
    EmulatorUtilities.loadProgram(emu, program)
    thread = emu.newThread()
    EmulatorUtilities.initializeForFunction(thread, fct_sym.getObject(), 0x10000)
    tstate = thread.getState()
    def set_reg(name: str, value: int | JLong) -> None:
        # Convert large unsigned values using string parsing
        value_bi = BigInteger(str(value)) if value >= (1 << 63) else BigInteger.valueOf(value)
        reg = lang.getRegister(name)
        tstate.setRegisterValue(RegisterValue(reg, value_bi))
    def get_reg(name: str) -> JLong:
        reg = lang.getRegister(name)
        return tstate.inspectRegisterValue(reg).getSignedValue().longValue()
    thread.setCounter(fct_sym.getAddress())
    controlledReturnAddr = ram.getAddress(0x0badc0de)
    # Push the return address on the stack
    stack_top = ram.getAddress(get_reg("r10")).subtract(8)
    set_reg("r10", stack_top.getOffset())
    tstate.setLong(stack_top, controlledReturnAddr.getOffset())
    result = None
    # Run the emulation
    while not monitor.isCancelled():
        executionAddress = thread.getCounter()
        if executionAddress == controlledReturnAddr:
            result = get_reg("r0")
            print(f"Emulation complete, result is {result:#x}")
            break
        # Print current instruction and the registers we care about
        desc = f"{executionAddress} ({str(listing.getInstructionAt(executionAddress)):24s})"
        for reg in ("r0", "r1", "r2", "r3", "r4", "r5", "r6", "r10"):
            desc += f" {reg}={get_reg(reg):#x}"
        desc += f" StkTop-4176={tstate.inspectLong(stack_top.subtract(4176)):#x}"
        desc += f" StkTop-8280={tstate.inspectLong(stack_top.subtract(8280)):#x}"  # saved R1 at 4176+4104
        print(desc)
        # Single-step emulation
        try:
            thread.stepInstruction()
        except Exception as e:
            print(f"Emulation Error: {e}")
            break
    return result


def emulate_all_call_saving_regs() -> None:
    """Analyze all compiled versions of call_saving_regs.c"""
    with tempfile.TemporaryDirectory(prefix="ghidra-prj-") as proj_dir:
        with pyghidra.open_project(proj_dir, "call_saving_regs_emulation", create=True) as project:
            for compiled_path in sorted((ROOT_DIR / "compiled").glob("call_saving_regs.*.ebpf")):
                compiled_relpath = compiled_path.relative_to(ROOT_DIR)
                print(f"Emulating {compiled_relpath}")
                loader = pyghidra.program_loader().project(project).source(str(compiled_path))
                with loader.load() as loaded_program:
                    program = loaded_program.getPrimaryDomainObject()
                    # Analyze the program
                    pyghidra.analyze(program)
                    result = emulate_function(program, "use_registers", pyghidra.task_monitor())
                    if result is None:
                        print(f"Test FAIL {compiled_relpath}: incomplete emulation")
                        return
                    elif result != 0x987654321:
                        print(f"Test FAIL {compiled_relpath}: unexpected result {result:#x}")
                        return
                    print(f"Test OK {compiled_relpath}")


if __name__ == "__main__":
    emulate_all_call_saving_regs()
