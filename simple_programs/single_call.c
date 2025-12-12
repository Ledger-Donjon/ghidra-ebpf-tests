// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
Ghidra did not correctly decode CALL instructions to other functions.

This was fixed in Ghidra 11.4.1: https://github.com/NationalSecurityAgency/ghidra/pull/7929
("Fix eBPF CALL operand decoding")
*/
static int one(void) {
    return 1;
}

int call_one(void) {
    return one();
}
