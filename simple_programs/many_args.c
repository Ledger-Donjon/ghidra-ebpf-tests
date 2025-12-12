// SPDX-FileCopyrightText: 2025 LEDGER SAS
//
// SPDX-License-Identifier: MIT

/*
Define functions with many arguments

eBPF function ABI only supports 5 arguments.

Using 6 argument, clang complains:

    many_args.c:25:14: error: defined with too many args
    unsigned int fct_6args(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5, unsigned int a6) {
                 ^

and gcc complains as well:

    many_args.c: In function ‘fct_6args’:
    many_args.c:25:14: error: too many function arguments for eBPF
       25 | unsigned int fct_6args(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5, unsigned int a6) {
          |              ^~~~~~~~~
*/

unsigned int fct_5args(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5) {
    return (a1 + a2 - a3) * a4 + a5;
}

/*
unsigned int fct_6args(unsigned int a1, unsigned int a2, unsigned int a3, unsigned int a4, unsigned int a5, unsigned int a6) {
    return (a1 + a2 - a3) * a4 + a5 - a6;
}
*/
