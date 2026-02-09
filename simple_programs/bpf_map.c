// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
eBPF programs can use "maps" to store data between each execution.
The content of some maps is available from userspace, which enable getting
access to some statistics such as counters.

In practise, when an eBPF program using maps is loaded by libbpf, relocations
targeting a map are replaced with a special instruction: LDDW with src=1.
(The usual 64-bit load instruction uses src=0.)

More precisely, libbpf:

- identifies a section named ".maps",
  https://github.com/libbpf/libbpf/blob/v1.6.2/src/libbpf.c#L3909
- collects all ELF relocations targeting this section, in function bpf_object__collect_map_relos
  https://github.com/libbpf/libbpf/blob/v1.6.2/src/libbpf.c#L7193
- associates file descriptor (map_fd) with each map
- rewrites LDDW instructions (64-bit load immediate) with src=BPF_PSEUDO_MAP_FD=1 and imm=map_fd
  https://github.com/libbpf/libbpf/blob/v1.6.2/src/libbpf.c#L6121

When Ghidra parses ELF relocations, it always rewrites LDDW instructions:
https://github.com/NationalSecurityAgency/ghidra/blob/Ghidra_12.0_build/Ghidra/Processors/eBPF/src/main/java/ghidra/app/util/bin/format/elf/relocation/eBPF_ElfRelocationHandler.java#L66-L73

This is buggy, as this would also treat usual symbol relocations as if they were eBPF maps.

As documented on https://docs.ebpf.io/linux/concepts/maps/ ,
legacy eBPF programs used section "maps" instead of ".maps".

This is being fixed with:
https://github.com/NationalSecurityAgency/ghidra/pull/8860 ("Process more ELF
relocation kinds for eBPF programs")
*/
typedef unsigned int u32;
typedef unsigned long u64;

// These definitions are based on Linux:include/uapi/linux/bpf.h
// Copyright (c) 2011-2014 PLUMgrid, http://plumgrid.com
// SPDX-License-Identifier: GPL-2.0-only WITH Linux-syscall-note

// Constant from https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/bpf.h?h=v6.18#n980
// and https://github.com/libbpf/libbpf/blob/v1.6.2/include/uapi/linux/bpf.h#L979
enum bpf_map_type {
    BPF_MAP_TYPE_PERCPU_ARRAY = 6,
};

// The following lines are derived from libbpf (v1.6.2)
// SPDX-License-Identifier: LGPL-2.1-only OR BSD-2-Clause

// Macro from https://github.com/libbpf/libbpf/blob/v1.6.2/src/bpf_helpers.h#L41
#define SEC(name) __attribute__((section(name), used))

// Structure from https://github.com/libbpf/libbpf/blob/v1.6.2/src/libbpf.c#L537
struct bpf_map_def {
	unsigned int type;
	unsigned int key_size;
	unsigned int value_size;
	unsigned int max_entries;
	unsigned int map_flags;
};

// Function from https://github.com/libbpf/libbpf/blob/v1.6.2/src/bpf_helper_defs.h#L64
static void *(* const bpf_map_lookup_elem)(void *map, const void *key) = (void *) 1;

// Legacy way to declare a map
struct bpf_map_def SEC("maps") my_counter_legacy = {
    .type = BPF_MAP_TYPE_PERCPU_ARRAY,
    .key_size = sizeof(u32),
    .value_size = sizeof(u64),
    .max_entries = 1,
};

// Macros from https://github.com/libbpf/libbpf/blob/v1.6.2/src/bpf_helpers.h#L13
#define __uint(name, val) int (*name)[val]
#define __type(name, val) typeof(val) *name

// New way to declare a map
struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __type(key, u32);
    __type(value, u64);
    __uint(max_entries, 1);
} my_counter SEC(".maps");

SEC("tp_btf/sys_enter")
int sys_enter_count(void *ctx __attribute__((unused))) {
    u32 key = 0;
    u64 *counter;

    counter = bpf_map_lookup_elem(&my_counter_legacy, &key);
    if (counter) {
        (*counter)++;
    }

    counter = bpf_map_lookup_elem(&my_counter, &key);
    if (counter) {
        (*counter)++;
    }
    return 0;
}
