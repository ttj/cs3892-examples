/* Two variables that are always equal, chosen on one of two branches. The division
 * is safe on every run (x - y + 1 is always 1). An analysis that keeps each variable's
 * range separately cannot see that: after the join, x and y are both in [1, 2], so
 * x - y + 1 is in [0, 2], and 0 is a possible divisor.
 *
 *   goto-analyzer correlated.c --verify --intervals     UNKNOWN  (a false alarm)
 *   cbmc correlated.c                                   SUCCESS  (checks each path)
 */
#include <assert.h>

int nondet_int(void);

int main(void) {
    int x, y;
    if (nondet_int()) {
        x = 1;
        y = 1;
    } else {
        x = 2;
        y = 2;
    }
    assert(x - y + 1 != 0);        /* the divisor below */
    return 10 / (x - y + 1);
}
