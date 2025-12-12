// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
Ghidra did not zero-extend values loaded from the stack correctly.
This led functions using division such as the one below to be decompiled as:

    ulonglong div_by_1000(uint param_1)
    {
      undefined4 in_stack_00000000;
      return CONCAT44(in_stack_00000000,param_1) / 1000;
    }

This was fixed in Ghidra 11.4.1: https://github.com/NationalSecurityAgency/ghidra/pull/7979
("Fix eBPF zero-extend load instructions")
*/
unsigned int div_by_1000(unsigned int value) {
    return value / 1000;
}
