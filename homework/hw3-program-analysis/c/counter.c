/* From github.com/ttj/fmaiv, day04/examples/counter.c (the course's own short course), unchanged. */
/* Day 4 — the counter from Days 1 / 2 / 3, now in C.
 *
 * Same transition system, third encoding. The CBMC harness in
 * counter_check.c calls counter_step in a bounded loop and asserts the
 * same invariant x <= count_max that nuXmv verified on Day 2 and Lean
 * proved by induction on Day 3.
 *
 * Build with any C99 compiler; verify with cbmc (see counter_check.c).
 */

#include <stdbool.h>         /* gives the `bool` type and true/false */

#define COUNT_MAX 10         /* the count is never allowed to exceed this */

enum mode { MODE_OFF = 0, MODE_ON = 1 };   /* the two modes, as named integer constants */

struct state {               /* the whole counter state bundled together */
    enum mode mode;          /*   on/off mode */
    int x;                   /*   current count */
};

/* One step of the counter under input `press`. Matches the SMV
 * `next(...)` clauses exactly. */
/* `struct state *s` is a POINTER to the state: the function updates it in place
 * (writes through `s->...`). `press` is the button input for this step. */
void counter_step(struct state *s, bool press)
{
    enum mode prev_mode = s->mode;      /* snapshot the OLD mode before we overwrite */
    int prev_x = s->x;                  /* snapshot the OLD count */

    /* An if/else-if chain choosing the next state. Exactly one branch runs.
     * `==` compares, `!press` is "not pressed", `&&`/`||` are AND/OR. */
    if (prev_mode == MODE_OFF && !press) {        /* OFF, no press */
        s->mode = MODE_OFF;                       /*   -> stay OFF */
        s->x = prev_x;                            /*      count unchanged */
    } else if (prev_mode == MODE_OFF && press) {  /* OFF, pressed */
        s->mode = MODE_ON;                        /*   -> turn ON */
        s->x = prev_x;                            /*      count unchanged */
    } else if (prev_mode == MODE_ON && !press && prev_x < COUNT_MAX) {  /* ON, no press, room left */
        s->mode = MODE_ON;                        /*   -> stay ON */
        s->x = prev_x + 1;                        /*      and increment */
    } else if (prev_mode == MODE_ON && (press || prev_x >= COUNT_MAX)) {  /* ON and (pressed OR maxed) */
        s->mode = MODE_OFF;                       /*   -> turn OFF */
        s->x = 0;                                 /*      and reset count */
    }
    /* else: no clause matched; leave s unchanged (mirrors SMV `TRUE : ...`). */
}
