#pragma once
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/rational.hpp>
#include <iostream>

// --- Core Definitions ---
using HighPrecisionInt = boost::multiprecision::cpp_int;
using Rational = boost::rational<HighPrecisionInt>;

// --- ENUMS for CLI Control ---
enum PsiBehavior { PSI_FORCED, PSI_RHO_TRIGGERED, PSI_DUAL_RECIPROCAL };
enum KoppaMode { KOPPA_ACCUMULATE, KOPPA_DUMP, KOPPA_RATIO_FEED };
enum EngineType { ENGINE_ADDITIVE, ENGINE_MULTIPLICATIVE, ENGINE_ROTATIONAL, ENGINE_QUIET_ADDITIVE };

// --- ENUM Conversion Function DECLARATIONS ---
PsiBehavior string_to_psi(const std::string& s);
KoppaMode string_to_koppa(const std::string& s);
EngineType string_to_engine(const std::string& s);

// --- TRTS Engine Class ---
class TRTS_Engine {
private:
    Rational upsilon, beta, koppa; 
    int rho, microtick, step;         
    PsiBehavior psi_mode;
    KoppaMode koppa_mode;
    EngineType engine_mode;
    
    bool is_miller_rabin_prime(const HighPrecisionInt& n, int k = 10) const;
    bool is_prime_trigger() const;
    void psi_transform();
    void apply_propagation_engine();
    void update_koppa(int trigger);

public:
    // Constructor
    TRTS_Engine(PsiBehavior psi, KoppaMode koppa, EngineType engine);

    // Initialization and Execution
    void initialize_state(const HighPrecisionInt& u_num, const HighPrecisionInt& b_num);
    void process_microtick();
    void execute_step(int total_microticks = 11);

    // Getters
    std::string get_upsilon_ratio() const;
    std::string get_beta_ratio() const;
    std::string get_koppa_ratio() const;
};

