// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
eBPF historically does not support indirect calls (calling a function by its
address), as verifying such a call is quite difficult. While there were some
works related to adding indirect call support in the Linux kernel, this was
never finished and the standardized eBPF ISA does not define how the related
instruction "CALL register" is encoded:
https://www.rfc-editor.org/rfc/rfc9669.html

Some eBPG compilers nonetheless implemented this instruction.

LLVM (and clang) uses opcode {CALL, X, JMP} (also known as "CALLX") and
was encoding the register in the immediate field:

    8d 00 00 00 01 00 00 00  callx r1

This was implemented in
https://github.com/llvm/llvm-project/blob/7fa104ed20a576a792162e8ac677c1543032d8f1/llvm/lib/Target/BPF/BPFInstrInfo.td#L744-L754

gcc has been using a different encoding, where the register is encoded in the
destination register field:

    8d 01 00 00 00 00 00 00  callx r1

LLVM changed in 2024 to use gcc's encoding with commit
https://github.com/llvm/llvm-project/commit/c43ad6c0fddac0bbed5e881801dd2bc2f9eeba2d
(Pull Request https://github.com/llvm/llvm-project/pull/81546). This was part
of LLVM release 19.1.

Solana was using LLVM's old encoding and changed in 2024 to use a third
encoding in their fork of eBPF ISA called SBPF, where the source register field
is used:
https://github.com/solana-foundation/solana-improvement-documents/pull/173
In 2025, some discussions started questioning this change, to make Solana use
eBPF ISA again:
https://github.com/solana-foundation/solana-improvement-documents/pull/377

Ghidra was not supporting any encoding.
This was fixed in Ghidra 12.0: https://github.com/NationalSecurityAgency/ghidra/pull/7972
("Add eBPF instruction CALLX for indirect calls")
*/
extern void (*ptr_to_some_function)(void);

void call_ptr_to_some_function(void) {
    ptr_to_some_function();
}

unsigned int call_first_arg(unsigned int callback(unsigned int), unsigned int value) {
    return callback(value);
}

unsigned int call_last_arg(unsigned int value, unsigned int callback(unsigned int)) {
    return callback(value);
}
