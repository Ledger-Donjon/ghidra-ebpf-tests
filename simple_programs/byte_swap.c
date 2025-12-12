// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
eBPF contains legacy byteswap instructions which depend on the endianness of the host.
eBPF ISA v4 introduced instruction BSWAP, which always swaps bytes.

Ghidra was not considering the endianness of the host in legacy instructions and did not know the
new instruction.

This was fixed in Ghidra 11.4.1 with:
- https://github.com/NationalSecurityAgency/ghidra/pull/7982 ("Add eBPF ISA v4 instructions")
- https://github.com/NationalSecurityAgency/ghidra/pull/7985 ("Fix the semantics of eBPF byte swap instructions")
*/
unsigned short do_be16(unsigned short x) {
#ifdef __clang__
    __asm__("%0 = be16 %0" : "=r" (x) : "0" (x));
#else
    // bpf-gcc's dialect "normal", used before gcc 14.1:
    // https://github.com/gcc-mirror/gcc/commit/77d0f9ec3809b4d2e32c36069b6b9239d301c030
    // (Later versions require compiling with -masm=normal)
    __asm__("endbe %0,16" : "=r" (x) : "0" (x));
#endif
    return x;
}

unsigned int do_be32(unsigned int x) {
#ifdef __clang__
    __asm__("%0 = be32 %0" : "=r" (x) : "0" (x));
#else
    __asm__("endbe %0,32" : "=r" (x) : "0" (x));
#endif
    return x;
}

unsigned long do_be64(unsigned long x) {
#ifdef __clang__
    __asm__("%0 = be64 %0" : "=r" (x) : "0" (x));
#else
    __asm__("endbe %0,64" : "=r" (x) : "0" (x));
#endif
    return x;
}

unsigned short do_le16(unsigned short x) {
#ifdef __clang__
    __asm__("%0 = le16 %0" : "=r" (x) : "0" (x));
#else
    __asm__("endle %0,16" : "=r" (x) : "0" (x));
#endif
    return x;
}

unsigned int do_le32(unsigned int x) {
#ifdef __clang__
    __asm__("%0 = le32 %0" : "=r" (x) : "0" (x));
#else
    __asm__("endle %0,32" : "=r" (x) : "0" (x));
#endif
    return x;
}

unsigned long do_le64(unsigned long x) {
#ifdef __clang__
    __asm__("%0 = le64 %0" : "=r" (x) : "0" (x));
#else
    __asm__("endle %0,64" : "=r" (x) : "0" (x));
#endif
    return x;
}

#if __BPF_CPU_VERSION__ == 4
unsigned short do_bswap16(unsigned short x) {
    return __builtin_bswap16(x);
}
unsigned int do_bswap32(unsigned int x) {
    return __builtin_bswap32(x);
}
unsigned long do_bswap64(unsigned long x) {
    return __builtin_bswap64(x);
}
#endif
