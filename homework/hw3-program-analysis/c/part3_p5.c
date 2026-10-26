/* HW3 Part 3.3 -- your program P5, in C, for goto-analyzer and CBMC.
 *
 * Write a program on which the interval domain raises a FALSE alarm because of a join,
 * with the claim as an assert. Then compare:
 *
 *   goto-analyzer part3_p5.c --verify --intervals      (expect UNKNOWN: the false alarm)
 *   cbmc part3_p5.c                                    (expect SUCCESS: it checks each path)
 *
 * This placeholder is not such a program: replace it.
 */
#include <assert.h>

int nondet_int(void);

int main(void) {
    int x = nondet_int() ? 1 : 2;
    assert(x != 0);
    return 0;
}
