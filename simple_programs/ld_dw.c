// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
Debug decoding instruction LDDW, known as IMM, DW, LD (with immediate 64-bit value)

This was useful when support for Big Endian eBPF programs was added to Ghidra 11.4.1:
https://github.com/NationalSecurityAgency/ghidra/pull/7985#issuecomment-2858704968
*/

unsigned long get_1(void) {
    return 1;
}

long get_min1(void) {
    return -1;
}

/* Test that the low 32-bit part does not get sign-extended */
long get_min1_32bit(void) {
    return 0xffffffffUL;
}

long get_min_min1_32bit(void) {
    return -0xffffffffUL;
}

long get_value(void) {
    return 0x123456789abcdef0UL;
}
