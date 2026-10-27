/* Session 11's agent, as a C program: it may delete files only after a human said yes.
 *
 * Each step, the language model picks an action, and CBMC treats that choice as an
 * input it may set to anything: 0 = plan, 1 = ask the human, 2 = delete. When it
 * asks, the human's answer is a second input. Nothing stops the model from taking
 * the shortcut and deleting without asking.
 *
 *   cbmc agent.c --unwind 4 --trace            the property fails; read the trace
 *   cbmc agent.c --unwind 4 -DGATEWAY          a gateway refuses the shortcut: it holds
 */
#include <assert.h>

int nondet_int(void);   /* no body: CBMC lets it return any int */

int main(void) {
    int approved = 0;
    for (int step = 0; step < 3; step++) {
        int action = nondet_int();
        __CPROVER_assume(0 <= action && action <= 2);
        if (action == 1) {
            approved = nondet_int() > 0;      /* the human answers yes or no */
        } else if (action == 2) {
#ifdef GATEWAY
            if (!approved)
                continue;                     /* the gateway refuses the call */
#endif
            assert(approved);                 /* never delete without approval */
            approved = 0;                     /* one approval, one delete */
        }
    }
    return 0;
}
