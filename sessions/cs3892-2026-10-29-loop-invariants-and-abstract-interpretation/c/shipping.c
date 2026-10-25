/* Shipping cost, in cents, for one order: a small function with three decisions.
 *
 *   cbmc shipping.c --function shipping --cover branch --show-test-suite
 *
 * CBMC turns "reach this branch" into a goal for the solver, one per branch, and
 * prints one set of inputs per goal it can reach: a test suite with full branch
 * coverage, generated rather than written.
 */
int shipping(int weight_g, int express) {
    if (weight_g <= 0)
        return -1;                 /* not a valid order */
    int cost = 500;
    if (weight_g > 2000)
        cost = cost + 300;         /* heavy parcel */
    if (express)
        cost = cost * 2;
    return cost;
}
