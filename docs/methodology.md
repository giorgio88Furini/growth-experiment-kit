# Methodology and interpretation

Growth Experiment Kit implements deliberately small-scope methods for two independent binomial arms. It reports estimates under assumptions; it does not establish that an intervention caused an outcome. A valid causal interpretation depends on study design and execution, including appropriate random assignment, exposure integrity, outcome measurement, and absence of material interference or bias.

## Planning: equal allocation

Inputs are a control conversion probability \(p_1\), a positive **absolute** minimum detectable effect \(\Delta\), type-I error rate \(\alpha\), and target power \(1-\beta\). The assumed alternative is \(p_2=p_1+\Delta\), which must be below one. For a two-sided test, define \(\bar p=(p_1+p_2)/2\), and let \(z_q\) be the standard-normal quantile at probability \(q\). The estimated sample size per arm is

\[
n = \left\lceil
\frac{\left[z_{1-\alpha/2}\sqrt{2\bar p(1-\bar p)} + z_{1-\beta}\sqrt{p_1(1-p_1)+p_2(1-p_2)}\right]^2}{(p_2-p_1)^2}
\right\rceil.
\]

The total is \(2n\). This common normal-approximation formula assumes independent observations and equal allocation. It is an estimate, not an exact power guarantee, and does not include expected attrition or design effects. Users needing a decrease as the alternative, a non-inferiority design, or unequal allocation should use a method designed for that question.

The MDE is given as a probability difference: `0.02` means two percentage points. The relative change corresponding to the planning rates is \(\Delta/p_1\); it is not interchangeable with the absolute MDE.

## Analysis: independent binomial arms

For control counts \((x_c,n_c)\) and treatment counts \((x_t,n_t)\), observed rates are \(\hat p_c=x_c/n_c\) and \(\hat p_t=x_t/n_t\). The signed absolute uplift is

\[
\hat d=\hat p_t-\hat p_c.
\]

Positive values favor the treatment on conversion rate. The relative uplift is \(\hat d/\hat p_c\), when \(\hat p_c>0\); otherwise it is undefined. A 10% to 12% change is +2 percentage points absolute and +20% relative.

The reported two-sided p-value uses the pooled score z-test under the equal-rate null. Let \(\hat p=(x_c+x_t)/(n_c+n_t)\). Its statistic is

\[
z=\frac{\hat p_t-\hat p_c}{\sqrt{\hat p(1-\hat p)(1/n_c+1/n_t)}}
\]

and the two-sided normal-tail probability is \(2\Phi(-|z|)\). If the pooled variance is zero (all observations are failures or all are successes), the observed rates are identical; the implementation returns \(z=0\), \(p=1\).

The reported two-sided 95% **unpooled Wald** confidence interval is

\[
\hat d \;\pm\; z_{0.975}
\sqrt{\frac{\hat p_c(1-\hat p_c)}{n_c}+
      \frac{\hat p_t(1-\hat p_t)}{n_t}}.
\]

This interval is not clipped to the feasible difference range \([-1,1]\). Like the test, it is an asymptotic approximation and can behave poorly with small counts or rates near zero or one. The implementation warns if any expected pooled success or failure count for an arm is below five; this is a practical signal, not a universal validity threshold.

## Design caveats

Interpret all outputs in light of the following limitations:

- Independent observations are assumed; users must account for repeated measures, household/site clustering, or other dependence separately.
- Planning assumes equal allocation. Analysis accepts different arm sizes but does not design for them.
- A fixed-horizon design is assumed. Repeated peeking or outcome-driven stopping can inflate false-positive rates; no sequential correction is applied.
- No multiple-testing correction is applied across metrics, variants, segments, or experiments.
- Normal approximations underlie planning, the pooled z-test, and the Wald interval; they may be unreliable for sparse data or boundary rates.
- No adjustment is made for attrition, noncompliance, covariates, delayed outcomes, missingness, or exposure imbalance.
- A small p-value is not the probability that the null is true, the probability the result replicates, or evidence of practical importance. A confidence interval is model-based and does not account for design defects.

Use a prespecified analysis plan and an appropriate method for the actual design. Consider exact or score-based intervals, simulation-based power, or specialist review when the approximation is questionable.
