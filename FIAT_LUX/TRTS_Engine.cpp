// --- TRTS_Engine Implementation (Synthesis) ---

// **CRITICAL DYNAMIC AXIOM 1: UNREDUCED PRIME CHECK (No-GCD)**
bool TRTS_Engine::is_prime_trigger() const {
    // We check the UNREDUCED NUMERATOR (Historical State)
    HighPrecisionInt num = upsilon_numerator_unreduced; 
    if (num < 0) num = -num;
    // Assume is_miller_rabin_prime is implemented for HighPrecisionInt
    return is_miller_rabin_prime(num); 
}

// **CRITICAL DYNAMIC AXIOM 2: CONTEXT-DEPENDENT KOPPA UPDATE**
void TRTS_Engine::update_koppa() {
    // This function must now be called with the context-dependent mode.
    // For the dynamic engine, we assume the calling code (CLI) or a pre-check
    // has set the correct koppa_mode based on the microtick position (Mt 7 vs Mt 10).
    
    if (koppa_mode == KOPPA_RATIO_FEED) {
        if (koppa == 0) koppa = Rational(1, 1);
        koppa = koppa * (upsilon / beta);
    } else if (koppa_mode == KOPPA_ACCUMULATE) {
        // Linear history (for low-energy flux)
        koppa = koppa + (upsilon - beta);
    } else if (koppa_mode == KOPPA_DUMP) {
        // Unstable/Massive force carriers: DUMP/NEUTRALIZE
        koppa = Rational(1, 1); // Or KOPPA = (upsilon/beta) to neutralize history
    }
}

// **PROPAGATION ENGINE (Includes UNREDUCED HISTORY UPDATE)**
void TRTS_Engine::apply_propagation_engine() {
    // ENGINE_QUIET_ADDITIVE: (Canonical)
    Rational diff = upsilon - beta;
    upsilon = upsilon + (diff / 11);
    beta = beta - (diff / 11);

    // CRITICAL: Propagate the UNREDUCED state (Conceptual/Placeholder)
    // This is the hardest part of the Python -> C++ port. In a true Unreduced
    // C++ system, you must implement Rational arithmetic without GCD.
    // The placeholder below shows the required conceptual update:
    upsilon_numerator_unreduced = (upsilon_numerator_unreduced * 11 + (diff.numerator() * 11 / diff.denominator())) / 11;
}

// **MICRO-TICK PROCESS (Includes IMMEDIATE PSI)**
void TRTS_Engine::process_microtick() {
    microtick++;
    rho = 0; 
    
    bool is_emission = (microtick == 1 || microtick == 4 || microtick == 7 || microtick == 10);
    bool is_propagation = (microtick == 3 || microtick == 6 || microtick == 9); 
    bool is_transformation_point = (microtick == 2 || microtick == 5 || microtick == 8 || microtick == 11); 

    if (is_emission) {
        if (is_prime_trigger()) { rho = 1; }
        if (rho > 0) { update_koppa(); } // Uses context-dependent koppa_mode
    }

    if (is_propagation) { apply_propagation_engine(); }

    if (is_transformation_point) {
        // **IMMEDIATE PSI (P1) LOGIC**
        if (rho > 0) { 
            psi_transform(); // Transforms at the very next M-Role
        } else if (microtick == 11) {
            psi_transform(); // Transforms at the end of step (canonical)
        }
    }
    
    if (microtick == 11) { microtick = 0; step++; }
}
