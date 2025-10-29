"""
TRTS (Triadic Rational Time-Step) Framework with CLI
Pure Rational Propagation Engine with CSV Output
"""

import sympy as sp
import csv
import math
import argparse
from fractions import Fraction
from typing import List, Dict, Tuple

class TRTSEngine:
    """Pure Rational TRTS Propagation Engine."""
    
    def __init__(self, u_seed: int = 13, b_seed: int = 3, 
                 psi_mode: str = "RHO", koppa_mode: str = "ACCUMULATE", 
                 engine_type: str = "ADDITIVE"):
        self.step_count = 0
        self.microtick = 0
        self.rho_triggered = False
        self.rho_prime = None
        
        # Initialize state - PURE RATIONALS ONLY
        self.upsilon = sp.Rational(u_seed, 7)
        self.beta = sp.Rational(b_seed, 11)
        self.koppa = sp.Rational(1, 1)
        self.imbalance_active = True
        
        self.psi_mode = psi_mode.upper()
        self.koppa_mode = koppa_mode.upper()
        self.engine_type = engine_type.upper()
        
        self.state_history = []
        self.emission_history = []
        self.csv_data = []
        
        self.fib_primes = [2, 3, 5, 13, 89, 233, 1597, 28657, 514229]
        self._initialize_csv_headers()
    
    def _initialize_csv_headers(self):
        headers = [
            'step', 'microtick', 'upsilon_num', 'upsilon_den', 'beta_num', 'beta_den',
            'koppa_num', 'koppa_den', 'rho_triggered', 'rho_prime', 
            'ratio_decimal', 'convergence_error'
        ]
        self.csv_data.append(headers)
    
    def is_prime_trigger(self, n: int) -> bool:
        abs_val = abs(n)
        if abs_val <= 1:
            return False
        return abs_val in self.fib_primes
    
    def psi_transform(self, a: sp.Rational, b: sp.Rational) -> Tuple[sp.Rational, sp.Rational]:
        num_a, den_a = a.as_numer_denom()
        num_b, den_b = b.as_numer_denom()
        
        if self.psi_mode == "DUAL":
            # Dual reciprocal: invert both, swap denominators
            new_upsilon = sp.Rational(den_a, den_b)
            new_beta = sp.Rational(den_b, den_a)
        else:
            # Original: (a/b, c/d) → (d/a, b/c)
            new_upsilon = sp.Rational(den_b, num_a)
            new_beta = sp.Rational(num_a, den_b)
        
        return new_upsilon, new_beta
    
    def advance_microtick(self):
        self.microtick += 1
        if self.microtick > 11:
            self.microtick = 1
            self.step_count += 1
        
        # Emission check at mt 1,4,7,10
        if self.microtick in [1, 4, 7, 10]:
            current_val = self.upsilon if self.microtick in [1, 7] else self.beta
            
            num_prime = self.is_prime_trigger(current_val.numerator)
            den_prime = self.is_prime_trigger(current_val.denominator)
            
            if num_prime or den_prime:
                self.rho_triggered = True
                self.rho_prime = current_val.numerator if num_prime else current_val.denominator
                
                # Apply Ψ-transformation based on mode
                if self.psi_mode in ["RHO", "DUAL"]:
                    self.upsilon, self.beta = self.psi_transform(self.upsilon, self.beta)
        
        self._handle_koppa_imbalance()
        
        if self.microtick == 11 and self.rho_triggered:
            self._eject_null_tick()
    
    def _handle_koppa_imbalance(self):
        if self.koppa_mode == "ACCUMULATE":
            self.koppa += (self.upsilon + self.beta) / 2
        elif self.koppa_mode == "FEED":
            if self.koppa == 0:
                self.koppa = sp.Rational(1, 1)
            self.koppa *= (self.upsilon / self.beta)
        elif self.koppa_mode == "DUMP":
            self.koppa = self.upsilon / self.beta
    
    def _eject_null_tick(self):
        self.rho_triggered = False
        self.rho_prime = None
        self.imbalance_active = not self.imbalance_active
    
    def execute_step(self, steps: int = 1, verbose: bool = False):
        for s in range(steps):
            for mt in range(11):
                self.advance_microtick()
                self._record_state()
            
            if verbose and (s == 0 or (s + 1) % 10 == 0 or s == steps - 1):
                ratio = float(self.upsilon / self.beta)
                print(f"Step {s+1:4d}: υ/β = {ratio:.10f}")
    
    def _record_state(self):
        ratio_float = float(self.upsilon / self.beta)
        sqrt2 = math.sqrt(2)
        convergence_error = abs(ratio_float - sqrt2)
        
        record = [
            self.step_count, self.microtick,
            int(self.upsilon.numerator), int(self.upsilon.denominator),
            int(self.beta.numerator), int(self.beta.denominator),
            int(self.koppa.numerator), int(self.koppa.denominator),
            self.rho_triggered, self.rho_prime if self.rho_prime else 0,
            ratio_float, convergence_error
        ]
        
        self.csv_data.append(record)
        self.state_history.append({
            'step': self.step_count,
            'ratio': ratio_float,
            'error': convergence_error
        })
    
    def export_csv(self, filename: str = "trts_output.csv"):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.csv_data)
        print(f"✓ Data exported to {filename}")
    
    def get_final_ratio(self) -> float:
        return float(self.upsilon / self.beta)
    
    def print_summary(self):
        if not self.state_history:
            print("No propagation data available")
            return
        
        final_ratio = self.state_history[-1]['ratio']
        final_error = self.state_history[-1]['error']
        
        print(f"\n{'='*60}")
        print(f"TRTS PROPAGATION SUMMARY")
        print(f"{'='*60}")
        print(f"Seeds: υ={self.upsilon.numerator}/{self.upsilon.denominator}, "
              f"β={self.beta.numerator}/{self.beta.denominator}")
        print(f"Mode: Ψ={self.psi_mode}, κ={self.koppa_mode}, Engine={self.engine_type}")
        print(f"Steps: {self.step_count}")
        print(f"\nFinal υ/β ratio: {final_ratio:.10f}")
        print(f"Target √2:       {math.sqrt(2):.10f}")
        print(f"Convergence error: {final_error:.8e}")
        print(f"Error %: {(final_error/math.sqrt(2))*100:.4f}%")
        
        # Check against SM targets
        targets = {
            'α⁻¹': 137.035999084,
            'p/e': 1836.15267343,
            'sin²θw': 0.23121
        }
        
        print(f"\nSM Target Analysis:")
        for name, target in targets.items():
            error_pct = abs(final_ratio - target) / target * 100
            if error_pct < 1.0:
                print(f"  {name}: {target:.6f} - Match! (error: {error_pct:.4f}%)")
            elif error_pct < 10.0:
                print(f"  {name}: {target:.6f} - Close (error: {error_pct:.2f}%)")


def main():
    parser = argparse.ArgumentParser(
        description='TRTS Pure Rational Propagation Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default seeds (13/7, 3/11) for 100 steps
  python trts.py
  
  # Run with canonical seeds (22/7, 19/11) for 4 steps
  python trts.py -u 22 -b 19 -t 4 -v
  
  # Run with DUAL/FEED/QUIET modes
  python trts.py -u 22 -b 19 -p DUAL -k FEED -e QUIET -t 10 -v
  
  # Export to custom CSV file
  python trts.py -u 22 -b 19 -t 100 -o sm_test.csv
        """
    )
    
    parser.add_argument('-u', '--upsilon', type=int, default=13,
                       help='Upsilon seed numerator (denominator=7)')
    parser.add_argument('-b', '--beta', type=int, default=3,
                       help='Beta seed numerator (denominator=11)')
    parser.add_argument('-p', '--psi', type=str, default='RHO',
                       choices=['RHO', 'DUAL', 'FORCED'],
                       help='Psi transformation mode')
    parser.add_argument('-k', '--koppa', type=str, default='ACCUMULATE',
                       choices=['ACCUMULATE', 'FEED', 'DUMP'],
                       help='Koppa imbalance mode')
    parser.add_argument('-e', '--engine', type=str, default='ADDITIVE',
                       choices=['ADDITIVE', 'QUIET', 'PURE'],
                       help='Propagation engine type')
    parser.add_argument('-t', '--ticks', type=int, default=100,
                       help='Number of steps to propagate')
    parser.add_argument('-o', '--output', type=str, default='trts_output.csv',
                       help='Output CSV filename')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Print progress during propagation')
    parser.add_argument('--no-csv', action='store_true',
                       help='Skip CSV export')
    
    args = parser.parse_args()
    
    print(f"{'='*60}")
    print(f"TRTS PURE RATIONAL PROPAGATION ENGINE")
    print(f"{'='*60}")
    print(f"Configuration:")
    print(f"  Seeds: υ={args.upsilon}/7, β={args.beta}/11")
    print(f"  Modes: Ψ={args.psi}, κ={args.koppa}, Engine={args.engine}")
    print(f"  Steps: {args.ticks}")
    print(f"{'='*60}\n")
    
    # Initialize engine
    engine = TRTSEngine(
        u_seed=args.upsilon,
        b_seed=args.beta,
        psi_mode=args.psi,
        koppa_mode=args.koppa,
        engine_type=args.engine
    )
    
    # Execute propagation
    try:
        engine.execute_step(steps=args.ticks, verbose=args.verbose)
    except KeyboardInterrupt:
        print("\n\n⚠ Propagation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during propagation: {e}")
        return 1
    
    # Print summary
    engine.print_summary()
    
    # Export CSV
    if not args.no_csv:
        engine.export_csv(args.output)
    
    return 0


if __name__ == "__main__":
    exit(main())
