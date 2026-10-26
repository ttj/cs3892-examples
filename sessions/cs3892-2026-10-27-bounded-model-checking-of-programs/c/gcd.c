/* Euclid's algorithm by subtraction: while a != b, take the smaller from the larger.
 * The inputs are any a0, b0 from 1 to 20. Two claims about the result g:
 *
 *   divides both    a0 % g == 0 and b0 % g == 0
 *   the greatest    no d with g < d <= 20 divides both
 *
 *   cbmc gcd.c --unwind 20                  both claims: SUCCESSFUL
 *   cbmc gcd.c --unwind 20 -DBROKEN         gcd returns 1: "divides both" still SUCCESS,
 *                                           "the greatest" FAILS (e.g. a0 = b0 = 2)
 *   cbmc gcd.c --unwind 20 -DBROKEN -DWEAK  with only "divides both": SUCCESSFUL, and wrong
 *
 *   cbmc gcd.c --unwind 19                  the unwinding assertion fails: a0 = 20, b0 = 1
 *
 * 20 because the longest run, a0 = 20 and b0 = 1, goes round the loop 19 times (and the check
 * loop at the end at most 19); CBMC needs one unwinding more than the longest run.
 */
#include <assert.h>

unsigned nondet_uint(void);

unsigned gcd(unsigned a, unsigned b) {
    while (a != b) {
        if (a > b) a = a - b;
        else       b = b - a;
    }
#ifdef BROKEN
    return 1;                                /* 1 divides everything */
#else
    return a;
#endif
}

int main(void) {
    unsigned a0 = nondet_uint(), b0 = nondet_uint();
    __CPROVER_assume(1 <= a0 && a0 <= 20 && 1 <= b0 && b0 <= 20);
    unsigned g = gcd(a0, b0);
    assert(a0 % g == 0 && b0 % g == 0);                 /* divides both */
#ifndef WEAK
    for (unsigned d = g + 1; d <= 20; d++)              /* the greatest */
        assert(!(a0 % d == 0 && b0 % d == 0));
#endif
    return 0;
}
