# Arrays revision rerun summary

This package reruns the main three-case pipeline and adds the reviewer-driven supplements:
- standard criterion comparisons (AIC/AICc/BIC/grouped CV/RIEC)
- lambda sensitivity for the drying case
- n_eff sensitivity across all three cases
- fold-wise group error tables and pairwise tests for drying

## Winner summary

- **optics**: AIC=cos_poly_deg2, AICc=cos_poly_deg2, BIC=cos_poly_deg2, grouped CV=cos_poly_deg2, RIEC=cos_poly_deg2
- **rtd**: AIC=gamma_2p, AICc=gamma_2p, BIC=gamma_2p, grouped CV=gamma_2p, RIEC=gamma_2p
- **drying**: AIC=two_term_3p, AICc=two_term_3p, BIC=weibull_2p, grouped CV=midilli_4p, RIEC=page_2p

## Main interpretation hook

- Optics and RTD are agreement regimes: all major criteria pick the same model.
- Drying is the disagreement regime: simpler information criteria, grouped CV, and RIEC do not all pick the same model, which is exactly the case where the paper needs a transparent compromise rule.
