#pragma once
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/rational.hpp>
#include <iostream>

// --- Core Definitions ---
// FIX: Corrected 'multiplexing' to 'multiprecision'
using HighPrecisionInt = boost::multiprecision::cpp_int;
using Rational = boost::rational<HighPrecisionInt>;

// --- ENUMS for CLI Control ---
enum PsiMode { PSI_F, PSI_R, PSI_D, PSI_C };       // Forced, Rho, Dual, Critical
enum KappaMode { KAPPA_A, KAPPA_D, KAPPA_F };     // Accumulate, Dump, Ratio_Feed
enum EngineType { ENG_A, ENG_M, ENG_R, ENG_Q };    // Additive, Multi, Rotational, Quiet

// --- TRTS Engine Class ---
class TRTS_Engine {
private:
    // **CRITICAL STATE VARIABLES**
    Rational upsilon, beta, koppa; 
    // Tracks the unreduced numerators for the RHO (prime) check.
    HighPrecisionInt upsilon_num_unreduced; 
    HighPrecisionInt beta_num_unreduced;
    
    int rho, microtick, step;
    PsiMode psi_mode;
    KappaMode kappa_mode_default;
    EngineType engine_mode;

    // --- Dynamic Axiom Functions ---
    bool is_prime_trigger() const;
    void psi_transform();
    void apply_propagation_engine();
    void update_koppa(int trigger);

public:
    TRTS_Engine(PsiMode psi, KappaMode kappa, EngineType engine);
    // Initializes state with FULL rational values
    void initialize_state(const Rational& u_seed, const Rational& b_seed);
    void process_microtick(); 
    void execute_tick(int total_microticks = 11);
    
    // Getters for Logging (needed for CSV output)
    std::string get_upsilon_str() const;
    std::string get_beta_str() const;
    std::string get_koppa_str() const;
    std::string get_psi_precursor_str() const;
    int get_step() const { return step; }
    int get_microtick() const { return microtick; }
    int get_rho() const { return rho; }
    const Rational& get_upsilon() const { return upsilon; }
    const Rational& get_beta() const { return beta; }
    const Rational& get_koppa() const { return koppa; }
};
