#include "TRTS_Engine.h"
#include <cmath>

// --- ENUM Conversion Functions ---

PsiBehavior string_to_psi(const std::string& s) {
    if (s == "FORCED") return PSI_FORCED;
    if (s == "RHO") return PSI_RHO_TRIGGERED;
    if (s == "DUAL") return PSI_DUAL_RECIPROCAL;
    throw std::runtime_error("Invalid PsiBehavior: " + s);
}

KoppaMode string_to_koppa(const std::string& s) {
    if (s == "ACCUMULATE") return KOPPA_ACCUMULATE;
    if (s == "DUMP") return KOPPA_DUMP;
    if (s == "FEED") return KOPPA_RATIO_FEED;
    throw std::runtime_error("Invalid KoppaMode: " + s);
}

EngineType string_to_engine(const std::string& s) {
    if (s == "ADDITIVE") return ENGINE_ADDITIVE;
    if (s == "MULTI") return ENGINE_MULTIPLICATIVE;
    if (s == "ROTATIONAL") return ENGINE_ROTATIONAL;
    if (s == "QUIET") return ENGINE_QUIET_ADDITIVE;
    throw std::runtime_error("Invalid EngineType: " + s);
}

// --- TRTS_Engine Implementation ---

TRTS_Engine::TRTS_Engine(PsiBehavior psi, KoppaMode koppa, EngineType engine)
    : rho(0), microtick(0), step(0), psi_mode(psi), koppa_mode(koppa), engine_mode(engine) {
    // Default initial state (will be overwritten by initialize_state)
    upsilon = Rational(1, 1);
    beta = Rational(1, 1);
    koppa = Rational(0, 1);
}

/**
 * @brief HARDCORE Miller-Rabin Primality Test.
 */
bool TRTS_Engine::is_miller_rabin_prime(const HighPrecisionInt& n, int k) const {
    // ... (Implementation of Miller-Rabin as provided previously)
    HighPrecisionInt abs_n = abs(n);
    if (abs_n <= 1) return false;
    if (abs_n <= 3) return true;
    if (abs_n % 2 == 0) return false;
    
    // We assume the number is large enough to warrant this process
    HighPrecisionInt n_minus_1 = abs_n - 1;
    HighPrecisionInt d = n_minus_1;
    int s = 0;
    
    while (d % 2 == 0) { d /= 2; s++; }
    
    // Fixed test bases (k=10)
    const std::vector<int> test_bases = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29};
    
    for (int base_int : test_bases) {
        if (base_int >= abs_n) break;
        HighPrecisionInt a(base_int);
        
        HighPrecisionInt x = boost::multiprecision::powm(a, d, abs_n);

        if (x == 1 || x == n_minus_1) continue;

        bool is_composite = true;
        for (int r = 1; r < s; ++r) {
            x = boost::multiprecision::powm(x, 2, abs_n); 
            if (x == n_minus_1) {
                is_composite = false;
                break;
            }
        }
        if (is_composite) return false;
    }
    return true;
}

bool TRTS_Engine::is_prime_trigger() const {
    return is_miller_rabin_prime(upsilon.numerator()) || is_miller_rabin_prime(upsilon.denominator());
}

void TRTS_Engine::psi_transform() {
    if (psi_mode == PSI_DUAL_RECIPROCAL) {
        // New Dual Reciprocal Logic
        Rational u_inv = 1 / upsilon;
        Rational b_inv = 1 / beta;
        upsilon = Rational(u_inv.numerator(), b_inv.denominator());
        beta = Rational(b_inv.numerator(), u_inv.denominator());
        
        if (koppa_mode == KOPPA_RATIO_FEED && koppa != Rational(0)) {
            Rational feed_ratio = koppa / Rational(7);
            upsilon = upsilon + feed_ratio;
            beta = beta - feed_ratio;
        }
    } else {
        // Original C-style Ψ-transformation: (a/b, c/d) -> (d/a, b/c)
        Rational new_upsilon = Rational(beta.denominator(), upsilon.denominator());
        Rational new_beta = Rational(upsilon.numerator(), beta.denominator());
        upsilon = new_upsilon;
        beta = new_beta;
    }
}

void TRTS_Engine::apply_propagation_engine() {
    // Propagation Logic (R-Role: microticks 3, 6, 9)
    Rational diff = upsilon - beta;
    
    switch (engine_mode) {
        case ENGINE_QUIET_ADDITIVE: 
            // Weighted fractional addition (Quieter engine)
            upsilon = upsilon + (diff / Rational(11));
            beta = beta - (diff / Rational(11));
            break;
        case ENGINE_ADDITIVE:
        default:
            // Standard additive propagation
            upsilon = upsilon + diff;
            beta = beta - diff;
            break;
    }
}

void TRTS_Engine::update_koppa(int trigger) {
    // Koppa update logic (E-Role: microticks 1, 4, 7, 10)
    Rational differential = upsilon - beta;

    switch (koppa_mode) {
        case KOPPA_ACCUMULATE:
        case KOPPA_DUMP: // Dump action would happen at step boundary, accumulation here.
            koppa = koppa + differential;
            break;
        case KOPPA_RATIO_FEED:
            // Koppa acts as a multiplier/ratio holder
            if (koppa == Rational(0)) koppa = Rational(1, 1);
            koppa = koppa * (upsilon / beta);
            break;
    }
}

void TRTS_Engine::initialize_state(const HighPrecisionInt& u_num, const HighPrecisionInt& b_num) {
    // Standard TRTS Seed Rule (Denominators 7 and 11)
    upsilon = Rational(u_num, 7);
    beta = Rational(b_num, 11);
    koppa = Rational(1, 1); // Reset/initial Koppa
    step++;
    microtick = 0;
    rho = 0;
}

void TRTS_Engine::process_microtick() {
    microtick++;
    rho = 0; 

    bool is_emission = (microtick == 1 || microtick == 4 || microtick == 7 || microtick == 10);
    bool is_propagation = (microtick == 3 || microtick == 6 || microtick == 9); 
    bool is_transformation_point = (microtick == 2 || microtick == 5 || microtick == 8 || microtick == 11); 

    if (is_emission) {
        if (is_prime_trigger()) { rho = 1; } // CPU-KILLER: Prime check runs here
        if (rho > 0) { update_koppa(rho); }
    }

    if (is_propagation) { apply_propagation_engine(); }

    if (is_transformation_point) {
        bool should_transform = false;
        
        // M-Role transformation trigger logic
        if (psi_mode == PSI_FORCED && microtick == 11) should_transform = true;
        if (psi_mode == PSI_RHO_TRIGGERED && rho > 0) should_transform = true;
        if (psi_mode == PSI_DUAL_RECIPROCAL && (microtick == 11 || rho > 0)) should_transform = true;

        if (should_transform) { psi_transform(); }
    }
}

void TRTS_Engine::execute_step(int total_microticks) {
    for (int i = 0; i < total_microticks; ++i) {
        process_microtick();
    }
}

// --- Getters ---
std::string TRTS_Engine::get_upsilon_ratio() const { return upsilon.numerator().str() + "/" + upsilon.denominator().str(); }
std::string TRTS_Engine::get_beta_ratio() const { return beta.numerator().str() + "/" + beta.denominator().str(); }
std::string TRTS_Engine::get_koppa_ratio() const { return koppa.numerator().str() + "/" + koppa.denominator().str(); }
// (Other getters would follow)
