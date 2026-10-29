/* Session 18 -- one specification, checked by CBMC (python/09_property_based_testing.py).

   bad_sort is selection sort with one bug: it COPIES the minimum into place instead of
   swapping it, so the output is sorted but can lose and duplicate elements.
   The specification has two parts, the same two the Hypothesis test checks:
     sorted:      a[0] <= a[1] <= ... <= a[N-1]
     permutation: every value occurs as often in the output as in the input.
   The harness checks both for EVERY array of N ints (nondet), not a sample.
   Run: cbmc bad_sort.c --unwind 4 */
#define N 3

int nondet_int(void);

void bad_sort(int *a, int n) {
  for (int i = 0; i < n; i++) {
    int m = i;
    for (int j = i + 1; j < n; j++)
      if (a[j] < a[m]) m = j;
    a[i] = a[m];               /* BUG: should swap a[i] and a[m] */
  }
}

int count(const int *a, int n, int v) {
  int c = 0;
  for (int k = 0; k < n; k++)
    if (a[k] == v) c++;
  return c;
}

int main(void) {
  int in[N], a[N];
  for (int i = 0; i < N; i++) { in[i] = nondet_int(); a[i] = in[i]; }
  bad_sort(a, N);
  for (int i = 0; i + 1 < N; i++)
    __CPROVER_assert(a[i] <= a[i + 1], "sorted");
  for (int i = 0; i < N; i++)
    __CPROVER_assert(count(a, N, in[i]) == count(in, N, in[i]), "permutation");
  return 0;
}
