// PURE TRTS CLI ENGINE - NO HARCODING, FULL USER CONTROL
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>

// PURE RATIONAL TYPE - NO NORMALIZATION
typedef struct {
    int64_t num;
    int64_t den;
} Rational;

// TRTS CONFIGURATION - ALL USER CONTROLLED
typedef struct {
    Rational seed_u;
    Rational seed_b;
    Rational seed_k;
    int psi_behavior;    // 0: forced, 1: rho, 2: mu, 3: rho_mstep
    int koppa_mode;      // 0: dump, 1: accumulate, 2: pop  
    int engine_type;     // 0: additive, 1: multiplicative, 2: rotational
    int total_ticks;
    int verbose;
    int symbolic_output;
} TRTS_Config;

// PURE RATIONAL ARITHMETIC - NO GCD
static Rational r_add(Rational a, Rational b) {
    return (Rational){a.num * b.den + b.num * a.den, a.den * b.den};
}

static Rational r_mul(Rational a, Rational b) {
    return (Rational){a.num * b.num, a.den * b.den};
}

static Rational r_div(Rational a, Rational b) {
    return (Rational){a.num * b.den, a.den * b.num};
}

// PURE PRIME CHECK - PRESERVES SIGN
static bool is_prime_preserve_sign(int64_t n) {
    if (n < 0) n = -n;
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    for (int64_t i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return false;
    }
    return true;
}

// SYMBOLIC MATH OUTPUT
void print_symbolic_step(TRTS_Config config, int tick, int microtick, 
                        Rational u, Rational b, Rational k, int rho) {
    if (!config.symbolic_output) return;
    
    printf("\n--- SYMBOLIC STEP %d.%d ---\n", tick, microtick);
    printf("υ=%ld/%ld, β=%ld/%ld, ϙ=%ld/%ld, ρ=%d\n", 
           u.num, u.den, b.num, b.den, k.num, k.den, rho);
    
    switch (microtick) {
        case 1: case 4: case 7: case 10:
            printf("ε: prime_check(|υ.num|=%ld) || prime_check(|υ.den|=%ld) || mt==10\n",
                   u.num, u.den);
            if (is_prime_preserve_sign(u.num) || is_prime_preserve_sign(u.den) || microtick == 10) {
                printf("ρ = (%d mod 4) + 1 = %d\n", rho, (rho % 4) + 1);
            }
            break;
        case 2: case 5: case 8: case 11:
            printf("μ: ");
            if (rho > 0) {
                switch (config.engine_type) {
                    case 0: printf("υ = υ + ϙ = %ld/%ld + %ld/%ld\n", u.num, u.den, k.num, k.den); break;
                    case 1: printf("υ = υ × ϙ = %ld/%ld × %ld/%ld\n", u.num, u.den, k.num, k.den); break;
                    case 2: printf("υ = (υ + ϙ) / 2\n"); break;
                }
            }
            break;
        case 3: case 6: case 9:
            printf("φ: β = ");
            switch (config.engine_type) {
                case 0: printf("υ + β = %ld/%ld + %ld/%ld\n", u.num, u.den, b.num, b.den); break;
                case 1: printf("υ × β = %ld/%ld × %ld/%ld\n", u.num, u.den, b.num, b.den); break;
                case 2: printf("(υ + β) / 2\n"); break;
            }
            break;
    }
}

// PURE TRTS PROPAGATION
void run_trts(TRTS_Config config) {
    Rational u = config.seed_u;
    Rational b = config.seed_b; 
    Rational k = config.seed_k;
    int rho = 0;
    
    printf("=== PURE TRTS PROPAGATION ===\n");
    printf("SEEDS: υ=%ld/%ld, β=%ld/%ld, ϙ=%ld/%ld\n", 
           u.num, u.den, b.num, b.den, k.num, k.den);
    printf("CONFIG: psi=%d, koppa=%d, engine=%d, ticks=%d\n\n",
           config.psi_behavior, config.koppa_mode, config.engine_type, config.total_ticks);
    
    for (int tick = 0; tick < config.total_ticks; tick++) {
        for (int mt = 1; mt <= 11; mt++) {
            if (config.verbose >= 2) {
                print_symbolic_step(config, tick, mt, u, b, k, rho);
            }
            
            switch (mt) {
                case 1: case 4: case 7: case 10: // EPSILON
                    if ((config.psi_behavior == 0) || // forced
                        (config.psi_behavior == 1 && is_prime_preserve_sign(u.num)) || // rho only
                        (config.psi_behavior == 2 && (mt == 2 || mt == 5 || mt == 8 || mt == 11)) || // all mu
                        (config.psi_behavior == 3 && (is_prime_preserve_sign(u.num) || mt == 10))) { // rho+mstep
                        rho = (rho % 4) + 1;
                    }
                    break;
                    
                case 2: case 5: case 8: case 11: // MU  
                    if (rho > 0) {
                        switch (config.engine_type) {
                            case 0: u = r_add(u, k); break; // additive
                            case 1: u = r_mul(u, k); break; // multiplicative  
                            case 2: u = r_div(r_add(u, k), (Rational){2,1}); break; // rotational
                        }
                    }
                    break;
                    
                case 3: case 6: case 9: // PHI
                    switch (config.engine_type) {
                        case 0: b = r_add(u, b); break;
                        case 1: b = r_mul(u, b); break;
                        case 2: b = r_div(r_add(u, b), (Rational){2,1}); break;
                    }
                    break;
            }
            
            // KOPPA MODE HANDLING
            switch (config.koppa_mode) {
                case 0: // dump - reset periodically
                    if (mt == 11) k = config.seed_k;
                    break;
                case 1: // accumulate - no change
                    break;
                case 2: // pop - modify based on state
                    if (mt == 11 && rho > 0) {
                        k = r_add(k, (Rational){rho, 1});
                    }
                    break;
            }
        }
        
        if (config.verbose >= 1 && (tick % 100 == 0 || tick < 10)) {
            printf("Tick %4d: υ=%ld/%ld, β=%ld/%ld, ϙ=%ld/%ld, ρ=%d\n", 
                   tick, u.num, u.den, b.num, b.den, k.num, k.den, rho);
        }
    }
    
    printf("\n=== FINAL STATE ===\n");
    printf("υ = %ld/%ld ≈ %.6f\n", u.num, u.den, (double)u.num/u.den);
    printf("β = %ld/%ld ≈ %.6f\n", b.num, b.den, (double)b.num/b.den); 
    printf("ϙ = %ld/%ld ≈ %.6f\n", k.num, k.den, (double)k.num/k.den);
    printf("ρ = %d\n", rho);
}

// PARSE RATIONAL FROM STRING "a/b"
Rational parse_rational(const char* str) {
    int64_t num, den;
    if (sscanf(str, "%ld/%ld", &num, &den) == 2 && den != 0) {
        return (Rational){num, den};
    }
    fprintf(stderr, "ERROR: Invalid rational format: %s (use a/b)\n", str);
    exit(1);
}

// PRINT HELP
void print_help() {
    printf("PURE TRTS ENGINE - ZERO HARCODING\n");
    printf("==================================\n\n");
    printf("USAGE: trts [OPTIONS]\n\n");
    printf("OPTIONS:\n");
    printf("  -u, --upsilon RATIO    Upsilon seed (default: 2/7)\n");
    printf("  -b, --beta RATIO       Beta seed (default: 3/11)\n"); 
    printf("  -k, --koppa RATIO      Koppa seed (default: 1/1)\n");
    printf("  -t, --ticks N          Number of ticks (default: 100)\n");
    printf("  -p, --psi MODE         Psi behavior: 0=forced, 1=rho, 2=mu, 3=rho_mstep (default: 0)\n");
    printf("  -o, --koppa MODE       Koppa mode: 0=dump, 1=accumulate, 2=pop (default: 1)\n");
    printf("  -e, --engine MODE      Engine type: 0=additive, 1=multiplicative, 2=rotational (default: 0)\n");
    printf("  -v, --verbose LEVEL    Verbosity: 0=quiet, 1=progress, 2=symbolic (default: 1)\n");
    printf("  -h, --help             Show this help\n\n");
    printf("EXAMPLES:\n");
    printf("  trts -u 5/7 -b 13/11 -t 1000 -p 1 -o 2 -e 0 -v 2\n");
    printf("  trts --upsilon 89/7 --beta 233/11 --ticks 5000 --psi 3\n");
}

int main(int argc, char *argv[]) {
    TRTS_Config config = {
        .seed_u = {2, 7},
        .seed_b = {3, 11},
        .seed_k = {1, 1},
        .psi_behavior = 0,
        .koppa_mode = 1,
        .engine_type = 0, 
        .total_ticks = 100,
        .verbose = 1,
        .symbolic_output = 0
    };
    
    // PARSE COMMAND LINE
    static struct option long_options[] = {
        {"upsilon", required_argument, 0, 'u'},
        {"beta", required_argument, 0, 'b'},
        {"koppa", required_argument, 0, 'k'},
        {"ticks", required_argument, 0, 't'},
        {"psi", required_argument, 0, 'p'},
        {"koppa-mode", required_argument, 0, 'o'},
        {"engine", required_argument, 0, 'e'},
        {"verbose", required_argument, 0, 'v'},
        {"help", no_argument, 0, 'h'},
        {0, 0, 0, 0}
    };
    
    int c;
    while ((c = getopt_long(argc, argv, "u:b:k:t:p:o:e:v:h", long_options, NULL)) != -1) {
        switch (c) {
            case 'u': config.seed_u = parse_rational(optarg); break;
            case 'b': config.seed_b = parse_rational(optarg); break;
            case 'k': config.seed_k = parse_rational(optarg); break;
            case 't': config.total_ticks = atoi(optarg); break;
            case 'p': config.psi_behavior = atoi(optarg); break;
            case 'o': config.koppa_mode = atoi(optarg); break;
            case 'e': config.engine_type = atoi(optarg); break;
            case 'v': config.verbose = atoi(optarg); break;
            case 'h': print_help(); return 0;
            default: fprintf(stderr, "Use -h for help\n"); return 1;
        }
    }
    
    config.symbolic_output = (config.verbose >= 2);
    
    // RUN TRTS WITH USER CONFIG
    run_trts(config);
    
    return 0;
}
