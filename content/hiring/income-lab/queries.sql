-- Each named block is a standalone analytical question.
-- Grain: one federal unit per quarter. Income means are not additive.
-- query:coverage
SELECT quarter_code, COUNT(*) AS observations, COUNT(DISTINCT state_code) AS states
FROM income GROUP BY quarter_code ORDER BY quarter_code;
-- query:latest_ranking
SELECT quarter, state, region, income_real_brl,
       DENSE_RANK() OVER (ORDER BY income_real_brl DESC) AS income_rank
FROM income WHERE quarter_code=(SELECT MAX(quarter_code) FROM income)
ORDER BY income_real_brl DESC, state_code;
-- query:regional_means
SELECT quarter, region, COUNT(*) AS states,
       ROUND(AVG(income_real_brl), 2) AS unweighted_state_mean_brl
FROM income WHERE quarter_code=(SELECT MAX(quarter_code) FROM income)
GROUP BY quarter, region ORDER BY unweighted_state_mean_brl DESC;
-- query:exact_yoy
SELECT current.quarter, current.state, current.region,
       current.income_real_brl, prior.income_real_brl AS prior_year_income_brl,
       ROUND(100.0*(current.income_real_brl-prior.income_real_brl)
             /NULLIF(prior.income_real_brl,0),2) AS yoy_pct
FROM income AS current
LEFT JOIN income AS prior
  ON prior.state_code=current.state_code
 AND prior.year=current.year-1
 AND prior.quarter_number=current.quarter_number
WHERE current.quarter_code=(SELECT MAX(quarter_code) FROM income)
ORDER BY yoy_pct DESC, current.state_code;
