#include "TRTS_Engine.h"
#include <boost/program_options.hpp>

namespace po = boost::program_options;

// Helper to truncate massive output for console readability
std::string truncate(const std::string& s) {
    if (s.length() > 60) {
        return s.substr(0, 30) + "...(" + std::to_string(s.length() - 60) + " digits)..." + s.substr(s.length() - 30);
    }
    return s;
}

int main(int argc, char* argv[]) {
    // --- 1. DEFINE CLI OPTIONS ---
    std::string psi_str, koppa_str, engine_str;
    std::string u_seed_str, b_seed_str;
    int ticks;

    po::options_description desc("TRTS Shadow Core Analytics Engine (Hardcore Mode)");
    desc.add_options()
        ("help", "Produce help message")
        ("psi", po::value(&psi_str)->default_value("DUAL"), "Psi behavior (FORCED, RHO, DUAL)")
        ("koppa", po::value(&koppa_str)->default_value("FEED"), "Koppa mode (ACCUMULATE, DUMP, FEED)")
        ("engine", po::value(&engine_str)->default_value("QUIET"), "Engine type (ADDITIVE, QUIET, MULTI, ROTATIONAL)")
        ("u_seed", po::value(&u_seed_str)->required(), "REQUIRED: Upsilon seed numerator (High-Precision Integer)")
        ("b_seed", po::value(&b_seed_str)->required(), "REQUIRED: Beta seed numerator (High-Precision Integer)")
        ("ticks", po::value(&ticks)->default_value(5), "Number of macro-ticks (11 microticks each) to run");

    // --- 2. PARSE OPTIONS ---
    po::variables_map vm;
    try {
        po::store(po::parse_command_line(argc, argv, desc), vm);
        
        if (vm.count("help")) {
            std::cout << desc << "\n";
            return 1;
        }
        po::notify(vm);
    } catch (const po::error& e) {
        std::cerr << "ERROR: " << e.what() << "\n" << desc << "\n";
        return 1;
    }

    // --- 3. INITIALIZE AND RUN TRTS ENGINE ---
    try {
        TRTS_Engine engine(string_to_psi(psi_str), string_to_koppa(koppa_str), string_to_engine(engine_str));
        
        // Read massive numbers directly from the CLI strings
        HighPrecisionInt u_seed(u_seed_str);
        HighPrecisionInt b_seed(b_seed_str);

        engine.initialize_state(u_seed, b_seed);

        std::cout << "=== TRTS SHADOW CORE ANALYTICAL ===\n";
        std::cout << "Configuration: Psi=" << psi_str << ", Koppa=" << koppa_str << ", Engine=" << engine_str << "\n";
        std::cout << "Initial υ Seed: " << truncate(u_seed_str) << "/7\n";
        std::cout << "Propagating " << ticks << " macro-ticks (11 microticks/tick)...\n";
        
        // 4. RUN PROPAGATION
        for (int t = 1; t <= ticks; ++t) {
            engine.execute_step();
            std::cout << "\n--- TICK " << t << " COMPLETE ---\n";
            std::cout << "  Final υ: " << truncate(engine.get_upsilon_ratio()) << std::endl;
            std::cout << "  Final β: " << truncate(engine.get_beta_ratio()) << std::endl;
            std::cout << "  Koppa ϙ: " << truncate(engine.get_koppa_ratio()) << std::endl;
        }
        std::cout << "\n--- EXHAUSTIVE PROPAGATION END ---\n";

    } catch (const std::exception& e) {
        std::cerr << "FATAL RUNTIME ERROR: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
