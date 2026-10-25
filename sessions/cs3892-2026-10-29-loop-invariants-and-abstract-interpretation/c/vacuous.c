/* A harness whose assumption no input can meet. Every assertion after it "holds",
 * including assert(0): CBMC says VERIFICATION SUCCESSFUL about no runs at all.
 *
 *   cbmc vacuous.c                       SUCCESSFUL -- and meaningless
 *   cbmc vacuous.c --cover assume        shows that the code after the assume is unreachable
 */
#include <assert.h>

int nondet_int(void);

int main(void) {
    int n = nondet_int();
    __CPROVER_assume(n > 10 && n < 5);
    assert(0);
    return 0;
}
