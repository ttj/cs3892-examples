/* HW3 Part 2b: two indices that walk towards each other.
 *
 * The claim is i == j after the loop. The loop contract's invariant is the macro INV,
 * set on the command line:
 *
 *   goto-cc converge.c -o c.gb -DINV="your invariant"
 *   goto-instrument --apply-loop-contracts c.gb c2.gb
 *   cbmc c2.gb --trace
 *
 * python/hw3_part2_converge.py runs those three commands for you.
 */
#include <assert.h>

#ifndef INV
#define INV 1
#endif

int main(void) {
    int i = 0, j = 10;
    while (i < j)
        __CPROVER_loop_invariant(INV)
    {
        i = i + 1;
        j = j - 1;
    }
    assert(i == j);
    return 0;
}
