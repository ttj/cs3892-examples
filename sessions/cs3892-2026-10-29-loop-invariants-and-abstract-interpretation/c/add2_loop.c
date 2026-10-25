/* Session 9's add-2 counter as a loop, with x != 5 checked after it -- for every
 * number of iterations, not just up to a bound. A loop contract states the invariant;
 * goto-instrument --apply-loop-contracts replaces the loop by three checks:
 * the invariant holds on entry, one iteration preserves it, and it gives the assertion.
 *
 *   goto-cc add2_loop.c -o add2.gb -DINV="x != 5"
 *   goto-instrument --apply-loop-contracts add2.gb add2_c.gb && cbmc add2_c.gb --trace
 *
 * "x != 5" is not preserved (from 3, one step gives 5). The strengthened invariant
 * 0 <= x <= 1000 and x even is, and then the assertion is proved with no bound at all.
 * (The cap at 1000 keeps x + 2 from overflowing.)
 */
#include <assert.h>

int nondet_int(void);

#ifndef INV
#define INV (0 <= x && x <= 1000 && x % 2 == 0)
#endif

int main(void) {
    int x = 0;
    while (nondet_int())
        __CPROVER_loop_invariant(INV)
    {
        x = x + 2;
        if (x > 1000)
            x = 0;
    }
    assert(x != 5);
    return 0;
}
