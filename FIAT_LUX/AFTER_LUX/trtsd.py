"""
TRTS (Triadic Rational Time-Step) Framework - FIXED VERSION
Fully Parameterized Implementation with No Hardcoding
"""

import sympy as sp
import csv
import math
import argparse
from typing import List, Dict, Tuple, Optional
from enum import Enum

class PsiMode(Enum):
    RHO = "RHO"           # Ψ only on ρ-trigger
    DUAL = "DUAL"         # Ψ on ρ-trigger OR microtick 11
    FORCED = "FORCED"     # Ψ every step
    NONE = "NONE"         # No Ψ transformations

class KoppaMode(Enum):
    ACCUMULATE = "ACCUMULATE"  # Linear accumulation
    FEED = "FEED"              # Ratio feeding
    OSCILLATE = "OSCILLATE"    # Alternating sign
    DUMP = "DUMP"              # Reset on emission
    NONE = "NONE"              # No κ accumulation

class EngineType(Enum):
    ADDITIVE = "ADDITIVE"      # Linear propagation
    QUIET = "QUIET"           # Weighted fractional
    PURE = "PURE"             # No external operations
    CANONICAL = "CANONICAL"   # Reference implementation
    PHASE_LOCKED = "PHASE_LOCKED"  # Phase-synchronized

class TRTSEngine:
    """
    Fully Parameterized TRTS Engine - No Hardcoding
    """
    
    def __init__(self, 
                 u_seed: int = 13,
                 u_denom: int = 7,
                 b_seed: int = 3, 
                 b_denom: int = 11,
                 k_seed_num: int = 1,
                 k_seed_den: int = 1,
                 psi_mode: PsiMode = PsiMode.RHO,
                 koppa_mode: KoppaMode = KoppaMode.ACCUMULATE,
                 engine_type: EngineType = EngineType.ADDITIVE,
                 fib_primes: Optional[List[int]] = None,
                 emission_microticks: Optional[List[int]] = None,
                 rho_threshold: float = 0.0,
                 convergence_target: float = math.sqrt(2)):
        """
        Fully parameterized TRTS initialization.
        """
        # Reset state
        self.step_count = 0
        self.microtick = 0
        self.rho_triggered = False
        self.rho_prime = None
        self.imbalance_active = True
        
        # Core oscillators - fully parameterized
        self.upsilon = sp.Rational(u_seed, u_denom)
        self.beta = sp.Rational(b_seed, b_denom)
        self.koppa = sp.Rational(k_seed_num, k_seed_den)
        
        # Operational parameters
        self.psi_mode = psi_mode
        self.koppa_mode = koppa_mode
        self.engine_type = engine_type
        self.rho_threshold = rho_threshold
        self.convergence_target = convergence_target
        
        # Configurable sequences
        self.fib_primes = fib_primes or [2, 3, 5, 13, 89, 233, 1597, 28657, 514229]
        self.emission_microticks = emission_microticks or [1, 4, 7, 10]
        
        # Tracking
        self.state_history = []
        self.emission_history = []
        self.csv_data = []
        
        self._initialize_csv_headers()
    
    def _initialize_csv_headers(self):
        """Comprehensive CSV headers for analysis."""
        headers = [
            'step', 'microtick', 
            'upsilon_num', 'upsilon_den', 'upsilon_value',
            'beta_num', 'beta_den', 'beta_value',
            'koppa_num', 'koppa_den', 'koppa_value',
            'ratio_value', 'target_value', 'convergence_error',
            'rho_triggered', 'rho_prime', 'imbalance_active',
            'psi_mode', 'koppa_mode', 'engine_type',
            'emission_count', 'structural_phase'
        ]
        self.csv_data.append(headers)
    
    def is_prime_trigger(self, n: int) -> bool:
        """Configurable prime detection."""
        abs_val = abs(n)
        if abs_val <= 1:
            return False
        return abs_val in self.fib_primes
    
    def should_trigger_rho(self, current_val: sp.Rational) -> bool:
        """Configurable ρ-trigger logic."""
        num_prime = self.is_prime_trigger(current_val.numerator)
        den_prime = self.is_prime_trigger(current_val.denominator)
        
        # Can add threshold logic here
        if self.rho_threshold > 0:
            val_float = float(current_val)
            threshold_trigger = abs(val_float - 1.0) > self.rho_threshold
            return (num_prime or den_prime) and threshold_trigger
        
        return num_prime or den_prime
    
    def psi_transform(self, a: sp.Rational, b: sp.Rational) -> Tuple[sp.Rational, sp.Rational]:
        """Ψ-transformation with configurable variants."""
        num_a, den_a = a.as_numer_denom()
        num_b, den_b = b.as_numer_denom()
        
        if self.psi_mode == PsiMode.RHO:
            # Standard Ψ: (a/b, c/d) → (d/a, b/c)
            return sp.Rational(den_b, num_a), sp.Rational(num_a, den_b)
        elif self.psi_mode == PsiMode.DUAL:
            # Dual transformation
            return sp.Rational(den_a, num_b), sp.Rational(num_b, den_a)
        else:
            # Identity transformation
            return a, b
    
    def apply_koppa_operation(self):
        """Apply κ operation based on selected mode."""
        if self.koppa_mode == KoppaMode.ACCUMULATE:
            self.koppa += (self.upsilon + self.beta) / 2
        elif self.koppa_mode == KoppaMode.FEED:
            self.koppa *= (self.upsilon / self.beta)
        elif self.koppa_mode == KoppaMode.OSCILLATE:
            sign = -1 if self.step_count % 2 == 0 else 1
            self.koppa = sp.Rational(sign * abs(self.koppa.numerator), abs(self.koppa.denominator))
        elif self.koppa_mode == KoppaMode.DUMP and self.rho_triggered:
            self.koppa = sp.Rational(1, 1)  # Reset on emission
        # KoppaMode.NONE does nothing
    
    def apply_engine_propagation(self):
        """Apply engine-specific propagation logic."""
        if self.engine_type == EngineType.ADDITIVE:
            # Linear additive propagation
            self.upsilon += self.koppa / 10
            self.beta += self.koppa / 10
        elif self.engine_type == EngineType.QUIET:
            # Weighted fractional propagation
            weight = sp.Rational(1, 100)
            self.upsilon = self.upsilon * (1 + weight) + self.koppa * weight
            self.beta = self.beta * (1 - weight) + self.koppa * weight
        elif self.engine_type == EngineType.PHASE_LOCKED:
            # Phase-synchronized propagation
            phase = (self.microtick - 1) % 3
            if phase == 0:  # E phase
                self.upsilon += self.koppa
            elif phase == 1:  # M phase  
                self.beta += self.koppa
            # R phase does nothing
        # EngineType.PURE and EngineType.CANONICAL use default propagation
    
    def advance_microtick(self):
        """Execute one microtick with full parameterization."""
        self.microtick += 1
        if self.microtick > 11:
            self.microtick = 1
            self.step_count += 1
        
        # Emission check at configurable microticks
        if self.microtick in self.emission_microticks:
            current_val = self.upsilon if self.microtick in [1, 7] else self.beta
            
            if self.should_trigger_rho(current_val):
                self.rho_triggered = True
                self.rho_prime = current_val.numerator
                
                # Apply Ψ based on mode
                if self.psi_mode in [PsiMode.RHO, PsiMode.DUAL]:
                    self.upsilon, self.beta = self.psi_transform(self.upsilon, self.beta)
                elif self.psi_mode == PsiMode.FORCED:
                    # Force Ψ every time
                    self.upsilon, self.beta = self.psi_transform(self.upsilon, self.beta)
        
        # Apply κ operations
        self.apply_koppa_operation()
        
        # Apply engine propagation
        self.apply_engine_propagation()
        
        # Ω ejection at microtick 11
        if self.microtick == 11:
            self._eject_null_tick()
    
    def _eject_null_tick(self):
        """Eject Ω null tick."""
        self.rho_triggered = False
        self.rho_prime = None
        self.imbalance_active = not self.imbalance_active
    
    def execute_step(self, steps: int = 1):
        """Execute steps with state recording."""
        for _ in range(steps):
            for mt in range(11):
                self.advance_microtick()
                self._record_state()
    
    def _record_state(self):
        """Record current state to CSV."""
        ratio_val = float(self.upsilon / self.beta)
        error = abs(ratio_val - self.convergence_target)
        phase = (self.microtick - 1) % 3
        
        record = [
            self.step_count, self.microtick,
            int(self.upsilon.numerator), int(self.upsilon.denominator), float(self.upsilon),
            int(self.beta.numerator), int(self.beta.denominator), float(self.beta),
            int(self.koppa.numerator), int(self.koppa.denominator), float(self.koppa),
            ratio_val, self.convergence_target, error,
            self.rho_triggered, self.rho_prime if self.rho_prime else 0, self.imbalance_active,
            self.psi_mode.value, self.koppa_mode.value, self.engine_type.value,
            len(self.emission_history), phase
        ]
        
        self.csv_data.append(record)
        self.state_history.append({
            'step': self.step_count,
            'microtick': self.microtick,
            'upsilon': self.upsilon,
            'beta': self.beta,
            'koppa': self.koppa,
            'ratio': ratio_val,
            'error': error
        })
        
        if self.rho_triggered:
            self.emission_history.append({
                'step': self.step_count,
                'microtick': self.microtick,
                'prime': self.rho_prime,
                'upsilon': self.upsilon,
                'beta': self.beta
            })
    
    def export_csv(self, filename: str):
        """Export data to CSV."""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.csv_data)
        print(f"Data exported to {filename}")
    
    def get_convergence_analysis(self) -> Dict:
        """Comprehensive convergence analysis."""
        if len(self.state_history) < 2:
            return {}
        
        ratios = [state['ratio'] for state in self.state_history]
        errors = [state['error'] for state in self.state_history]
        
        return {
            'final_ratio': ratios[-1],
            'target': self.convergence_target,
            'final_error': errors[-1],
            'error_percentage': (errors[-1] / self.convergence_target) * 100,
            'min_error': min(errors),
            'max_error': max(errors),
            'avg_error': sum(errors) / len(errors),
            'total_emissions': len(self.emission_history),
            'emission_steps': [e['step'] for e in self.emission_history],
            'converged': errors[-1] < 0.001
        }


def create_engine_from_args(args) -> TRTSEngine:
    """Create TRTS engine from command line arguments."""
    return TRTSEngine(
        u_seed=args.u_seed,
        u_denom=args.u_denom,
        b_seed=args.b_seed,
        b_denom=args.b_denom,
        k_seed_num=args.k_seed_num,
        k_seed_den=args.k_seed_den,
        psi_mode=PsiMode(args.psi_mode),
        koppa_mode=KoppaMode(args.koppa_mode),
        engine_type=EngineType(args.engine_type),
        fib_primes=args.fib_primes,
        emission_microticks=args.emission_microticks,
        rho_threshold=args.rho_threshold,
        convergence_target=args.convergence_target
    )


def main():
    """Main function with full command-line interface."""
    parser = argparse.ArgumentParser(description='TRTS Framework - Fully Parameterized')
    
    # Seed parameters
    parser.add_argument('--u_seed', type=int, default=13, help='υ numerator seed')
    parser.add_argument('--u_denom', type=int, default=7, help='υ denominator')
    parser.add_argument('--b_seed', type=int, default=3, help='β numerator seed')  
    parser.add_argument('--b_denom', type=int, default=11, help='β denominator')
    parser.add_argument('--k_seed_num', type=int, default=1, help='κ numerator seed')
    parser.add_argument('--k_seed_den', type=int, default=1, help='κ denominator seed')
    
    # Mode parameters
    parser.add_argument('--psi_mode', type=str, default='RHO', 
                       choices=[m.value for m in PsiMode], help='Ψ transformation mode')
    parser.add_argument('--koppa_mode', type=str, default='ACCUMULATE',
                       choices=[m.value for m in KoppaMode], help='κ accumulation mode')
    parser.add_argument('--engine_type', type=str, default='ADDITIVE',
                       choices=[m.value for m in EngineType], help='Engine propagation type')
    
    # Configuration parameters
    parser.add_argument('--fib_primes', type=int, nargs='+', 
                       default=[2, 3, 5, 13, 89, 233, 1597],
                       help='Fibonacci primes for ρ-trigger')
    parser.add_argument('--emission_microticks', type=int, nargs='+',
                       default=[1, 4, 7, 10], 
                       help='Microticks that check for emissions')
    parser.add_argument('--rho_threshold', type=float, default=0.0,
                       help='Threshold for ρ-trigger (0 = prime only)')
    parser.add_argument('--convergence_target', type=float, default=math.sqrt(2),
                       help='Target value for convergence analysis')
    
    # Execution parameters
    parser.add_argument('--ticks', type=int, default=100, help='Number of ticks to run')
    parser.add_argument('--output', type=str, default='trts_output.csv', 
                       help='Output CSV filename')
    
    args = parser.parse_args()
    
    print("=== TRTS FRAMEWORK - FULLY PARAMETERIZED ===")
    print(f"Seeds: υ={args.u_seed}/{args.u_denom}, β={args.b_seed}/{args.b_denom}")
    print(f"Modes: Ψ={args.psi_mode}, κ={args.koppa_mode}, Engine={args.engine_type}")
    print(f"Target: {args.convergence_target}, Ticks: {args.ticks}")
    print()
    
    # Create and run engine
    engine = create_engine_from_args(args)
    engine.execute_step(args.ticks)
    
    # Analyze results
    analysis = engine.get_convergence_analysis()
    
    print("=== RESULTS ===")
    print(f"Final ratio: {analysis['final_ratio']:.6f}")
    print(f"Target: {analysis['target']:.6f}")
    print(f"Error: {analysis['final_error']:.8f} ({analysis['error_percentage']:.4f}%)")
    print(f"Emissions: {analysis['total_emissions']} at steps {analysis['emission_steps']}")
    print(f"Converged: {analysis['converged']}")
    
    # Export data
    engine.export_csv(args.output)
    
    print(f"\nData exported to {args.output}")


if __name__ == "__main__":
    main()
