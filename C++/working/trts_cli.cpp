#include "TRTS_Engine.h"
#include <boost/program_options.hpp>
#include <iostream>
#include <sstream>

namespace po = boost::program_options;

std::string truncate(const std::string& s) {
    if (s.length() > 60)
        return s.substr(0, 30) + "...(" + std::to_string(s.length() - 60) + " digits)..." + s.substr(s.length() - 30);
    return s;
}

// Parse rational input like "22/7" or "137"
Rational parse_rational(const std::string& s) {
    size_t slash = s.find('/');
    if (slash == std::string::npos)
        return Rational(HighPrecisionInt(s), 1);
    else {
        std::string num = s.substr(0, slash);
        std::string den = s.substr(slash + 1);
        return Rational(HighPrecisionInt(num), HighPrecisionInt(den));
    }
}

// Helper to parse numeric or text modes
PsiBehavior parse_psi(const std::string& s) {
    if (s == "0" || s == "FORCED" || s == "forced") return PSI_FORCED;
    if (s == "1" || s == "RHO" || s == "rho") return PSI_RHO_TRIGGERED;
    if (s == "2" || s == "DUAL" || s == "dual") return PSI_DUAL_RECIPROCAL;
    if (s == "3" || s == "CRIT" || s == "crit") return PSI_CRITICAL_IMBALANCE;
    throw std::runtime_error("Invalid PsiBehavior: " + s);
}

KoppaMode parse_koppa(const std::string& s) {
    if (s == "0" || s == "ACCUMULATE" || s == "accumulate") return KOPPA_ACCUMULATE;
    if (s == "1" || s == "DUMP" || s == "dump") return KOPPA_DUMP;
    if (s == "2" || s == "FEED" || s == "feed") return KOPPA_RATIO_FEED;
    throw std::runtime_error("Invalid KoppaMode: " + s);
}

EngineType parse_engine(const std::string& s) {
    if (s == "0" || s == "ADDITIVE" || s == "additive") return ENGINE_ADDITIVE;
    if (s == "1" || s == "MULTI" || s == "multi") return ENGINE_MULTIPLICATIVE;
    if (s == "2" || s == "ROT" || s == "rot" || s == "rotational") return ENGINE_ROTATIONAL;
    if (s == "3" || s == "QUIET" || s == "quiet") return ENGINE_QUIET_ADDITIVE;
    throw std::runtime_error("Invalid EngineType: " + s);
}

int main(int argc, char* argv[]) {
    std::string psi_str, koppa_str, engine_str;
    std::string u_seed_str, b_seed_str;
    int ticks = 5;

    po::options_description desc("TRTS Shadow Core (compact CLI)");
    desc.add_options()
        ("help,h", "Show this help message")
        ("psi,i", po::value(&psi_str)->default_value("2"), "Psi behavior: [0=FORCED,1=RHO,2=DUAL]")
        ("koppa,k", po::value(&koppa_str)->default_value("2"), "Koppa mode: [0=ACCUM,1=DUMP,2=FEED]")
        ("engine,e", po::value(&engine_str)->default_value("3"), "Engine: [0=ADD,1=MULTI,2=ROT,3=QUIET]")
        ("u,u_seed", po::value(&u_seed_str)->required(), "Upsilon seed (e.g. 22/7)")
        ("b,b_seed", po::value(&b_seed_str)->required(), "Beta seed (e.g. 19/11)")
        ("ticks,t", po::value(&ticks)->default_value(5), "Number of macro-ticks");

    po::variables_map vm;
    try {
        po::store(po::parse_command_line(argc, argv, desc), vm);

        if (vm.count("help")) {
            std::cout << desc << "\n";
            return 0;
        }

        po::notify(vm);
    } catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << "\n\n" << desc << "\n";
        return 1;
    }

    try {
        // Parse modes
        PsiBehavior psi_mode = parse_psi(psi_str);
        KoppaMode koppa_mode = parse_koppa(koppa_str);
        EngineType engine_mode = parse_engine(engine_str);

        // Parse rational seeds
        Rational upsilon_seed = parse_rational(u_seed_str);
        Rational beta_seed = parse_rational(b_seed_str);

        // Initialize engine
        TRTS_Engine engine(psi_mode, koppa_mode, engine_mode);
        engine.initialize_state(upsilon_seed.numerator(), beta_seed.numerator());  // numerators still drive state

        std::cout << "\n=== TRTS SHADOW CORE ===\n";
        std::cout << "Ψ=" << psi_str << "  κ=" << koppa_str << "  Engine=" << engine_str << "\n";
        std::cout << "υ₀=" << truncate(u_seed_str) << ", β₀=" << truncate(b_seed_str)
                  << " | ticks=" << ticks << "\n";

        for (int t = 1; t <= ticks; ++t) {
            engine.execute_step();
            std::cout << "\n[TICK " << t << "] υ=" << truncate(engine.get_upsilon_ratio())
                      << "  β=" << truncate(engine.get_beta_ratio())
                      << "  κ=" << truncate(engine.get_koppa_ratio()) << std::endl;
        }

        std::cout << "\n--- PROPAGATION COMPLETE ---\n";

    } catch (const std::exception& e) {
        std::cerr << "FATAL RUNTIME ERROR: " << e.what() << "\n";
        return 1;
    }

    return 0;
}

