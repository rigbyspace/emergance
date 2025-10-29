#pragma once
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/rational.hpp>
#include <iostream>

// --- Core Definitions ---
// Note: boost::rational auto-reduces (GCD), which we now know is a design flaw.
// The Logic below compensates by checking the UNREDUCED NUMERATOR (N_unreduced).
using HighPrecisionInt = boost::multiprecision::cpp_int;
using Rational = boost::rational<HighPrecisionInt>;

// --- ENUMS for CLI Control (From your files) ---
enum PsiBehavior { PSI_FORCED, PSI_RHO_TRIGGERED, PSI_DUAL_RECIPROCAL, PSI_CRITICAL_IMBALANCE };
enum KoppaMode { KOPPA_ACCUMULATE, KOPPA_DUMP, KOPPA_RATIO_FEED };
enum EngineType { ENGINE_ADDITIVE, ENGINE_MULTIPLICATIVE, ENGINE_ROTATIONAL, ENGINE_QUIET_ADDITIVE };

// --- TRTS Engine Class ---
class TRTS_Engine {
private:
    Rational upsilon, beta, koppa; 
    HighPrecisionInt upsilon_numerator_unreduced; // NEW: Stores history
    HighPrecisionInt beta_numerator_unreduced;    // NEW: Stores history
    int rho, microtick, step;         
    PsiBehavior psi_mode;
    KoppaMode koppa_mode;
    EngineType engine_mode;
    
    // Core Functions (Derived Logic)
    bool is_prime_trigger() const; // Uses upsilon_numerator_unreduced
    void psi_transform();
    void apply_propagation_engine();
    void update_koppa();

public:
    TRTS_Engine(PsiBehavior psi, KoppaMode koppa, EngineType engine);
    // Initialization now requires the raw numerators
    void initialize_state(const HighPrecisionInt& u_num, const HighPrecisionInt& b_num);
    void process_microtick(); // The 11-tick cycle logic
};
