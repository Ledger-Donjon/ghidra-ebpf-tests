// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
Perform some signing operations, to use Sign-Extension Load Operations

The eBPF ISA RFC defined Sign-Extension Load Operations:
https://www.rfc-editor.org/rfc/rfc9669.html#name-sign-extension-load-operati

    {MEMSX, <size>, LDX} means: dst = *(signed size *) (src + offset)

These instructions were added to Linux 6.6:
https://github.com/torvalds/linux/commit/1f9a1ea821ff25353a0e80d971e7958cd55b47a3

A blog article detailed the versions of the instruction set architecture:
https://pchaigno.github.io/bpf/2021/10/20/ebpf-instruction-sets.html

    The first two extensions of the base instruction set, v2 and v3, add support for new jump instructions. The fourth extension adds a whole set of new instructions, for the most part related to signed operations.

Ghidra was not supporting the instructions.
This was fixed in Ghidra 11.4.1: https://github.com/NationalSecurityAgency/ghidra/pull/7982
("Add eBPF ISA v4 instructions")
*/
signed long sext_8bit(signed char x) {
    return (long)x;
}
signed long sext_16bit(signed short x) {
    return (long)x;
}
signed long sext_32bit(signed int x) {
    return x;
}

#if __BPF_CPU_VERSION__ == 4
/* Test instructions added in eBPF v4 extensions (compiler option -cpu=v4) */
signed long signed_div64(signed long x) {
    return x / 1000;
}
unsigned long unsigned_div64(unsigned long x) {
    return x / 1000;
}
signed int signed_div32(signed int x) {
    return x / 1000;
}
unsigned int unsigned_div32(unsigned int x) {
    return x / 1000;
}
signed long signed_mod64(signed long x) {
    return x % 1000;
}
unsigned long unsigned_mod64(unsigned long x) {
    return x % 1000;
}
signed int signed_mod32(signed int x) {
    return x % 1000;
}
unsigned int unsigned_mod32(unsigned int x) {
    return x % 1000;
}

/* Signed mov */
signed long signed_mov_s8s64(unsigned char x) {
    return (signed long)(signed char)x;
}
signed long signed_mov_s16s64(unsigned short x) {
    return (signed long)(signed short)x;
}
signed long signed_mov_s32s64(unsigned int x) {
    return (signed long)(signed int)x;
}
signed int signed_mov_s8s32(unsigned char x) {
    return (signed int)(signed char)x;
}
signed int signed_mov_s16s32(unsigned short x) {
    return (signed int)(signed short)x;
}
#endif /* __BPF_CPU_VERSION__ == 4 */
