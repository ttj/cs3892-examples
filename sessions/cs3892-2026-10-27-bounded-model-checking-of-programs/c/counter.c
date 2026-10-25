/* The running counter, as a C program.
 *
 *   x := 0;   x < 10 / x := x + 1;   x >= 10 / x := 0
 *
 * A state of this program is (the line it is at, the value of x): the same
 * transition system as the SMV model, with a program counter added. The loop runs
 * the counter for 30 steps and checks x <= 10 after every one.
 *
 *   cbmc counter.c --unwind 31
 *
 * Since CBMC 6, unwinding assertions are on by default: CBMC also proves that 31
 * unwindings are enough, i.e. that no run of the loop is longer than the bound.
 */
#include <assert.h>

int main(void) {
    int x = 0;
    for (int step = 0; step < 30; step++) {
        if (x < 10)
            x = x + 1;
        else
            x = 0;
        assert(x <= 10);
    }
    return 0;
}
