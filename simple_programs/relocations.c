// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
Emit several kinds of ELF relocations.

The relocations can be listed with:

    clang -O0 -target bpf -c relocations.c -o relocations.ebpf
    llvm-objdump --reloc relocations.ebpf

Ghidra 12.0's implementation of ELF relocations is very limited and buggy:
https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.0_build/Ghidra/Processors/eBPF/src/main/java/ghidra/app/util/bin/format/elf/relocation/eBPF_ElfRelocationHandler.java#L42

- Relocations R_BPF_64_64 are considered as if they always target an eBPF map
- Processing eBPF map relocations R_BPF_64_64 assumes the program is in Little Endian
- Relocations R_BPF_64_32 (for function calls) assumes it targets a local function or a section,
  and does not consider external functions
- Relocations R_BPF_64_ABS64 are not handled

This is being fixed with:
https://github.com/NationalSecurityAgency/ghidra/pull/8860 ("Process more ELF
relocation kinds for eBPF programs")
*/
static int some_int = 42;

// Create a relocation of kind R_BPF_64_ABS64 in section .data
static int *int_pointer = &some_int;


// Create a relocation R_BPF_64_64 to section .data
int get_some_int(void) {
    return *int_pointer;
}

// Create a relocation R_BPF_64_64 to a symbol
extern int some_extern_int;
int get_some_extern_int(void) {
    return some_extern_int;
}

static int get_some_int_static(void) {
    return 1234;
}

// Macro from https://github.com/libbpf/libbpf/blob/v1.6.2/src/bpf_helpers.h#L41
#define SEC(name) __attribute__((section(name), used))

// Create a relocation R_BPF_64_32 to a symbol
int SEC("prog") get_some_int_from_section(void) {
    return get_some_int();
}

// Create a relocation R_BPF_64_32 to section .text
int SEC("prog") get_some_int_static_from_section(void) {
    return get_some_int_static();
}

// Create a relocation R_BPF_64_32 to an external function
void some_external_function(void);
void call_some_external_function(void) {
    some_external_function();
}

// Create a relocation R_BPF_64_64 to an external pointer
extern void (*ptr_to_some_function)(void);
void call_ptr_to_some_function(void) {
    ptr_to_some_function();
}
