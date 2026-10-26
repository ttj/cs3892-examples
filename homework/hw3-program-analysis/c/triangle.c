/* HW3 Part 4: classify a triangle by its side lengths.
 *
 *   0 = not a triangle (a side is not positive, or one side is too long)
 *   1 = equilateral    2 = isosceles    3 = scalene
 *
 * Compile with -DMUTANT to get a version with one deliberate bug in it.
 *
 *   cbmc triangle.c --function triangle --cover branch --show-test-suite
 */
int triangle(int a, int b, int c) {
    if (a <= 0 || b <= 0 || c <= 0)
        return 0;
    if ((long long)a + b <= c || (long long)a + c <= b || (long long)b + c <= a)
        return 0;                  /* the sums are done in 64 bits, so they cannot overflow */
    if (a == b && b == c)
        return 1;
#ifdef MUTANT
    if (a == b || b == c)
#else
    if (a == b || b == c || a == c)
#endif
        return 2;
    return 3;
}
