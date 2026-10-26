/* From github.com/ttj/fmaiv, day04/examples/counter_check.c (the course's own short course), unchanged. */
/* CBMC harness for the counter from counter.c.
 *
 * We unwind the step function up to N times. At each step we let CBMC
 * choose a nondeterministic press input (this is what `nondet_bool()`
 * does — CBMC treats it as a fresh, unconstrained boolean). After every
 * step we assert the invariant that nuXmv and Lean confirmed:
 *      x <= COUNT_MAX
 *
 * Build and verify:
 *
 *      cbmc counter.c counter_check.c --unwind 26 --unwinding-assertions
 *
 * Expected verdict:  VERIFICATION SUCCESSFUL
 *
 * Try also:
 *      cbmc counter.c counter_check.c --unwind 6     (still ok; covers a shorter
 *                                                     trace -- BOUND-1 iterations)
 *      cbmc counter.c counter_check.c --trace        (shows a successful path)
 *
 * Note: --unwind needs BOUND+1, not BOUND. CBMC unwinds the body BOUND
 * times and then adds one more check confirming the loop has terminated.
 * The "+1" is for that termination check.
 *
 * To see a failed verification, change `<= COUNT_MAX` to `< COUNT_MAX`
 * below and re-run. CBMC will print a counterexample path that pushes
 * x to exactly COUNT_MAX.
 */

#include <stdbool.h>         /* bool, true/false */
#include <assert.h>          /* assert(): each becomes a CBMC proof goal */

#define BOUND 25             /* how many steps (button presses) to check */

enum mode { MODE_OFF = 0, MODE_ON = 1 };   /* must match counter.c */

struct state {               /* must match counter.c */
    enum mode mode;
    int x;
};

extern void counter_step(struct state *s, bool press);   /* the function under test, defined in counter.c */

/* CBMC nondeterminism: returns an unconstrained boolean each call. */
/* No body on purpose -- CBMC treats nondet_* as a FREE input it may pick any way. */
bool nondet_bool(void);

int main(void)
{
    struct state s = { .mode = MODE_OFF, .x = 0 };   /* start in the initial state: OFF, count 0 */

    for (int i = 0; i < BOUND; ++i) {
        bool press = nondet_bool();   /* arbitrary press/no-press each step: CBMC explores ALL sequences */
        counter_step(&s, press);      /* advance the state by one step (updates s in place) */

        /* The invariant we want CBMC to discharge over every
         * reachable state up to BOUND steps. */
        assert(s.x <= 10);            /* PROPERTY: the count never exceeds COUNT_MAX (= 10) */
    }

    return 0;
}
