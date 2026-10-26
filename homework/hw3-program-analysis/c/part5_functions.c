/* HW3 Part 5: three small functions, to be given contracts.
 *
 * Put each contract in c/contracts.h as two macros per function, e.g.
 *     #define REQUIRES_SAT_ADD   (0 <= a && a <= limit)
 *     #define ENSURES_SAT_ADD    (__CPROVER_return_value <= limit)
 * __CPROVER_return_value is the function's result. python/hw3_part5_check.py checks each
 * contract against the function (goto-instrument --enforce-contract), against a mutant of it
 * (compile with -DMUTANT_SAT_ADD etc.), and checks that the precondition can be met at all.
 *
 * The placeholder contracts in contracts.h are "1": they hold for every function.
 */
#include "contracts.h"

/* a + b, but never more than limit (for non-negative inputs). */
int sat_add(int a, int b, int limit)
    __CPROVER_requires(REQUIRES_SAT_ADD)
    __CPROVER_ensures(ENSURES_SAT_ADD)
{
    int s = a + b;
#ifdef MUTANT_SAT_ADD
    if (s > limit) return limit - 1;
#else
    if (s > limit) return limit;
#endif
    return s;
}

/* |a - b| */
int abs_diff(int a, int b)
    __CPROVER_requires(REQUIRES_ABS_DIFF)
    __CPROVER_ensures(ENSURES_ABS_DIFF)
{
#ifdef MUTANT_ABS_DIFF
    return a - b;
#else
    return a > b ? a - b : b - a;
#endif
}

/* the middle value of three */
int median3(int a, int b, int c)
    __CPROVER_requires(REQUIRES_MEDIAN3)
    __CPROVER_ensures(ENSURES_MEDIAN3)
{
    if (a > b) { int t = a; a = b; b = t; }
    if (b > c) { int t = b; b = c; c = t; }
#ifdef MUTANT_MEDIAN3
    return b;
#else
    if (a > b) { int t = a; a = b; b = t; }
    return b;
#endif
}

int main(void) { return 0; }
