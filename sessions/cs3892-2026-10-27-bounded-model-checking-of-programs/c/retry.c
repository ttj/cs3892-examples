/* A retry loop: try a flaky call until it succeeds, at most max_retries times.
 * max_retries is a configuration input between 0 and 5. The claim under test is
 * "the loop never makes more than 3 attempts" -- which is false when max_retries
 * is 4 or 5 and every attempt fails.
 *
 *   cbmc retry.c --unwind 3 --no-unwinding-assertions   SUCCESSFUL (and wrong)
 *   cbmc retry.c --unwind 3                             the unwinding assertion fails
 *   cbmc retry.c --unwind 6                             the real counterexample
 */
#include <assert.h>

int nondet_int(void);

int main(void) {
    int max_retries = nondet_int();
    __CPROVER_assume(0 <= max_retries && max_retries <= 5);
    int attempts = 0, ok = 0;
    while (!ok && attempts < max_retries) {
        attempts = attempts + 1;
        ok = nondet_int() > 0;               /* the call succeeds or fails */
    }
    assert(attempts <= 3);
    return 0;
}
