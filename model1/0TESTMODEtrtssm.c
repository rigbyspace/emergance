// COMPREHENSIVE TEST SUITE FOR TRTS FRAMEWORK
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>

// [Previous type definitions and functions remain the same...]

// Enhanced testing with multiple configurations
typedef struct {
    PsiBehavior psi_behavior;
    KoppaMode koppa_mode;
    EngineType engine_type;
    int ticks;
    char* config_name;
} TestConfig;

void run_comprehensive_test_suite() {
    printf("=== TRTS FRAMEWORK COMPREHENSIVE VALIDATION ===\n\n");
    
    TestConfig configs[] = {
        {PSI_FORCED, KOPPA_ACCUMULATE, ENGINE_ADDITIVE, 100, "Baseline Additive"},
        {PSI_FORCED, KOPPA_ACCUMULATE, ENGINE_MULTIPLICATIVE, 100, "Multiplicative"},
        {PSI_FORCED, KOPPA_ACCUMULATE, ENGINE_ROTATIONAL, 100, "Rotational"},
        {PSI_RHO, KOPPA_DUMP, ENGINE_ADDITIVE, 100, "Rho-Triggered Dump"},
        {PSI_MU, KOPPA_ACCUMULATE, ENGINE_ADDITIVE, 100, "Mu-Step Accumulate"},
        {PSI_RHO_MSTEP, KOPPA_POP, ENGINE_ADDITIVE, 100, "Rho+MStep Pop"}
    };
    
    int num_configs = sizeof(configs) / sizeof(configs[0]);
    
    for (int cfg = 0; cfg < num_configs; cfg++) {
        printf("\n🧪 CONFIGURATION: %s\n", configs[cfg].config_name);
        printf("Psi: %d, Koppa: %d, Engine: %d, Ticks: %d\n", 
               configs[cfg].psi_behavior, configs[cfg].koppa_mode, 
               configs[cfg].engine_type, configs[cfg].ticks);
        
        TRTS_State state = {0};
        state.psi_behavior = configs[cfg].psi_behavior;
        state.koppa_mode = configs[cfg].koppa_mode;
        state.engine_type = configs[cfg].engine_type;
        
        // Track convergence metrics
        double convergence_data[100] = {0};
        int prime_emissions = 0;
        int forced_emissions = 0;
        
        for (int tick = 0; tick < configs[cfg].ticks; tick++) {
            initialize_state(&state, tick);
            
            for (state.microtick = 1; state.microtick <= 11; state.microtick++) {
                process_microtick_complete(&state);
            }
            
            // Store convergence data
            convergence_data[tick] = (double)state.upsilon.num / state.upsilon.den;
            
            // Track emission types
            if (state.rho > 0 && state.rho < 4) prime_emissions++;
            if (state.rho == 4) forced_emissions++;
            
            // Display key checkpoints
            if (tick == 0 || tick == 24 || tick == 49 || tick == 74 || tick == 99) {
                double beta_val = (double)state.beta.num / state.beta.den;
                printf("  Tick %3d: υ=%.6f, β=%.6f, ϙ=%ld/%ld\n", 
                       tick, convergence_data[tick], beta_val, 
                       state.koppa.num, state.koppa.den);
            }
        }
        
        // Calculate convergence to fundamental constants
        double final_upsilon = convergence_data[configs[cfg].ticks - 1];
        double sqrt2 = sqrt(2.0);
        double phi = (1.0 + sqrt(5.0)) / 2.0;
        double inv_sqrt2 = 1.0 / sqrt2;
        
        double error_sqrt2 = fabs(final_upsilon - sqrt2) / sqrt2 * 100.0;
        double error_phi = fabs(final_upsilon - phi) / phi * 100.0;
        double error_inv_sqrt2 = fabs(final_upsilon - inv_sqrt2) / inv_sqrt2 * 100.0;
        
        // Role distribution analysis
        float distribution[3];
        calculate_role_distribution(&state, distribution);
        
        printf("  RESULTS:\n");
        printf("  Final υ: %.6f (Error: √2=%.1f%%, φ=%.1f%%, 1/√2=%.1f%%)\n",
               final_upsilon, error_sqrt2, error_phi, error_inv_sqrt2);
        printf("  Emissions: Prime=%d, Forced=%d, Total=%d\n", 
               prime_emissions, forced_emissions, prime_emissions + forced_emissions);
        printf("  Role Dist: E=%.1f%%, M=%.1f%%, R=%.1f%%\n",
               distribution[0], distribution[1], distribution[2]);
        printf("  Koppa Final: %ld/%ld ≈ %.3f\n", 
               state.koppa.num, state.koppa.den, 
               (double)state.koppa.num / state.koppa.den);
        
        // Check for tick 137 resonance if applicable
        if (configs[cfg].ticks >= 137) {
            double resonance_val = convergence_data[136];
            printf("  Tick 137 Resonance: υ=%.6f\n", resonance_val);
        }
    }
}

// Specialized test for accuracy gap analysis
void accuracy_gap_analysis() {
    printf("\n=== ACCURACY GAP ANALYSIS (15-20%% Deviation) ===\n");
    
    TRTS_State state = {0};
    state.psi_behavior = PSI_FORCED;
    state.koppa_mode = KOPPA_ACCUMULATE;
    state.engine_type = ENGINE_ADDITIVE;
    
    double sqrt2 = sqrt(2.0);
    double errors[200];
    int within_20pct = 0;
    int within_15pct = 0;
    
    for (int tick = 0; tick < 200; tick++) {
        initialize_state(&state, tick);
        
        for (state.microtick = 1; state.microtick <= 11; state.microtick++) {
            process_microtick_complete(&state);
        }
        
        double current_val = (double)state.upsilon.num / state.upsilon.den;
        double error = fabs(current_val - sqrt2) / sqrt2 * 100.0;
        errors[tick] = error;
        
        if (error <= 20.0) within_20pct++;
        if (error <= 15.0) within_15pct++;
        
        if (tick < 10 || tick % 50 == 49) {
            printf("  Tick %3d: Error = %.1f%%\n", tick, error);
        }
    }
    
    printf("  Accuracy Summary (200 ticks):\n");
    printf("  Within 20%% error: %d/200 (%d%%)\n", within_20pct, (within_20pct * 100) / 200);
    printf("  Within 15%% error: %d/200 (%d%%)\n", within_15pct, (within_15pct * 100) / 200);
    printf("  Final error: %.1f%%\n", errors[199]);
}

int main() {
    printf("TRTS FRAMEWORK - COMPREHENSIVE TESTING\n");
    printf("Validating against SM Model Predictions\n\n");
    
    run_comprehensive_test_suite();
    accuracy_gap_analysis();
    
    return 0;
}
