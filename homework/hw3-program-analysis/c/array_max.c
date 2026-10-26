/* From github.com/ttj/fmaiv, day04/examples/array_max.c (the course's own short course), unchanged. */
/* Maximum of an array (implementation under verification).
 * Verified against the harness in array_max_check.c with CBMC:
 *     cbmc array_max.c array_max_check.c --unwind 6 --unwinding-assertions
 * (This file alone has no main(); the harness supplies inputs and the checks.)
 */
/* a = pointer to the first element; n = how many elements. `const` = array_max
 * promises not to modify the array. Returns the largest element. */
int array_max(const int *a, int n)
{
    int m = a[0];                       /* running maximum, seeded with the 1st element */
    for (int i = 1; i < n; ++i) {       /* scan the rest, elements 1..n-1 */
        if (a[i] > m) {                 /* found something bigger? */
            m = a[i];                   /* remember it as the new max */
        }
    }
    return m;                           /* m now holds the largest element seen */
}
