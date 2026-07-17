// SPDX-FileCopyrightText: 2026 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
Ghidra emulation was not saving registers correctly. This programs implements a
function (use_registers) which sets every register, call another function
(modify_all_registers) and computes a checksum of the register values. If the
registers were not restored correctly after the function returned, the checksum
would not be the expected one (0x987654321).

This is being fixed with:
https://github.com/NationalSecurityAgency/ghidra/pull/9381 ("Emulate function
frames in eBPF specifications")
*/

unsigned long __attribute__((noinline)) modify_all_registers(void) {
    register unsigned long r0 __asm__("r0");
    register unsigned long r1 __asm__("r1");
    register unsigned long r2 __asm__("r2");
    register unsigned long r3 __asm__("r3");
    register unsigned long r4 __asm__("r4");
    register unsigned long r5 __asm__("r5");
    register unsigned long r6 __asm__("r6");
    register unsigned long r7 __asm__("r7");
    register unsigned long r8 __asm__("r8");
    register unsigned long r9 __asm__("r9");

    __asm__ volatile (
        ""
        : "=r" (r0), "=r" (r1), "=r" (r2), "=r" (r3), "=r" (r4), "=r" (r5), "=r" (r6), "=r" (r7), "=r" (r8), "=r" (r9)
        : "0" (0x10), "1" (0x11), "2" (0x12), "3" (0x13), "4" (0x14), "5" (0x15), "6" (0x16), "7" (0x17), "8" (0x18)
    );
    return r0;
}

unsigned long use_registers(void) {
    register unsigned long r0 __asm__("r0");
    register unsigned long r1 __asm__("r1");
    register unsigned long r2 __asm__("r2");
    register unsigned long r3 __asm__("r3");
    register unsigned long r4 __asm__("r4");
    register unsigned long r5 __asm__("r5");
    register unsigned long r6 __asm__("r6");
    register unsigned long r7 __asm__("r7");
    register unsigned long r8 __asm__("r8");
    register unsigned long r9 __asm__("r9");

    __asm__ volatile (
        "call %[fct]"
        : "=r" (r0), "=r" (r1), "=r" (r2), "=r" (r3), "=r" (r4), "=r" (r5), "=r" (r6), "=r" (r7), "=r" (r8), "=r" (r9)
        : [fct] "i" (modify_all_registers), "1" (1), "2" (2), "3" (3), "4" (4), "5" (5), "6" (6), "7" (7), "8" (8), "9" (9)
        : "memory"
    );
    r0 = r0 ^ 0x10;
    r0 = (r0 << 4) + r9;
    r0 = (r0 << 4) + r8;
    r0 = (r0 << 4) + r7;
    r0 = (r0 << 4) + r6;
    r0 = (r0 << 4) + r5;
    r0 = (r0 << 4) + r4;
    r0 = (r0 << 4) + r3;
    r0 = (r0 << 4) + r2;
    r0 = (r0 << 4) + r1;
    return r0;
}
