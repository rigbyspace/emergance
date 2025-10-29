import math
from sympy import isprime

# Custom UnreducedRational class to avoid GCD
class UnreducedRational:
    def __init__(self, numerator, denominator=1):
        self.numerator = numerator
        self.denominator = denominator
        if denominator == 0:
            raise ValueError("Denominator cannot be zero")
    
    def __add__(self, other):
        if isinstance(other, UnreducedRational):
            num = self.numerator * other.denominator + other.numerator * self.denominator
            den = self.denominator * other.denominator
        else:
            num = self.numerator + other * self.denominator
            den = self.denominator
        return UnreducedRational(num, den)
    
    def __sub__(self, other):
        if isinstance(other, UnreducedRational):
            num = self.numerator * other.denominator - other.numerator * self.denominator
            den = self.denominator * other.denominator
        else:
            num = self.numerator - other * self.denominator
            den = self.denominator
        return UnreducedRational(num, den)
    
    def __mul__(self, other):
        if isinstance(other, UnreducedRational):
            num = self.numerator * other.numerator
            den = self.denominator * other.denominator
        else:
            num = self.numerator * other
            den = self.denominator
        return UnreducedRational(num, den)
    
    def __truediv__(self, other):
        if isinstance(other, UnreducedRational):
            num = self.numerator * other.denominator
            den = self.denominator * other.numerator
        else:
            num = self.numerator
            den = self.denominator * other
        return UnreducedRational(num, den)
    
    def __eq__(self, other):
        if isinstance(other, UnreducedRational):
            return self.numerator * other.denominator == other.numerator * self.denominator
        return False
    
    def __float__(self):
        return float(self.numerator) / float(self.denominator)
    
    def __str__(self):
        return f"{self.numerator}/{self.denominator}"

# Miller-Rabin primality test for large integers
def is_miller_rabin_prime(n, k=5):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # Write n as d*2^r + 1
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# TRTS Engine Implementation
class TRTSEngine:
    def __init__(self, psi_mode='PSI_D', kappa_mode='KAPPA_A', engine_mode='ENG_Q'):
        self.upsilon = None
        self.beta = None
        self.koppa = UnreducedRational(0, 1)  # Default to 0
        self.upsilon_num_unreduced = 0
        self.beta_num_unreduced = 0
        self.rho = 0
        self.microtick = 0
        self.step = 0
        self.psi_mode = psi_mode
        self.kappa_mode = kappa_mode
        self.engine_mode = engine_mode
    
    def initialize_state(self, u_seed, b_seed):
        self.upsilon = u_seed
        self.beta = b_seed
        self.koppa = UnreducedRational(0, 1)
        self.upsilon_num_unreduced = u_seed.numerator
        self.beta_num_unreduced = b_seed.numerator
        self.rho = 0
        self.microtick = 0
        self.step = 0
    
    def is_prime_trigger(self):
        num = abs(self.upsilon_num_unreduced)
        return is_miller_rabin_prime(num)
    
    def update_koppa(self, trigger):
        if trigger == 0:
            return
        
        # Kappa modes based on microtick (from context)
        if self.microtick == 7:  # Strong Force -> Ratio Feed
            if float(self.koppa) == 0:
                self.koppa = UnreducedRational(1, 1)
            self.koppa = self.koppa * (self.upsilon / self.beta)
        elif self.microtick == 10:  # Massive -> Dump
            self.koppa = self.upsilon / self.beta
        elif self.microtick in [1, 4]:  # Low Energy -> Accumulate
            self.koppa = self.koppa + (self.upsilon - self.beta)
    
    def psi_transform(self):
        # PSI_DUAL_RECIPROCAL: Swap and invert based on kappa
        if self.psi_mode == 'PSI_D':
            if float(self.koppa) != 0:
                self.upsilon, self.beta = self.beta, self.upsilon
                self.upsilon = UnreducedRational(1, 1) / self.upsilon
                self.beta = UnreducedRational(1, 1) / self.beta
        # Add other psi modes if needed
    
    def apply_propagation_engine(self):
        diff = self.upsilon - self.beta
        eleven = UnreducedRational(11, 1)
        delta = diff / eleven
        
        if self.engine_mode == 'ENG_Q':  # QUIET ADDITIVE
            self.upsilon = self.upsilon + delta
            self.beta = self.beta - delta
            # Update unreduced numerators
            self.upsilon_num_unreduced += delta.numerator
            self.beta_num_unreduced -= delta.numerator
        elif self.engine_mode == 'ENG_A':  # ADDITIVE
            self.upsilon = self.upsilon + diff
            self.beta = self.beta - diff
        elif self.engine_mode == 'ENG_M':  # MULTIPLICATIVE
            self.upsilon = self.upsilon + (self.upsilon * delta)
            self.beta = self.beta - (self.beta * delta)
        elif self.engine_mode == 'ENG_R':  # ROTATIONAL
            temp = self.upsilon
            self.upsilon = self.beta
            self.beta = temp
    
    def process_microtick(self):
        self.microtick += 1
        if self.microtick > 11:
            self.microtick = 1
            self.step += 1
        
        # Check for prime trigger at emission points (microticks 1,4,7,10)
        if self.microtick in [1, 4, 7, 10]:
            if self.is_prime_trigger():
                self.rho = 1
                self.update_koppa(1)
            else:
                self.rho = 0
                self.update_koppa(0)
        else:
            self.rho = 0
        
        # At MT11 (M), apply propagation and psi_transform
        if self.microtick == 11:
            self.apply_propagation_engine()
            self.psi_transform()
    
    def execute_tick(self, total_steps=1000):
        results = []
        for _ in range(total_steps * 11):  # 11 microticks per step
            self.process_microtick()
            if self.microtick == 11:  # Log at end of each tick
                results.append({
                    'step': self.step,
                    'microtick': self.microtick,
                    'upsilon': float(self.upsilon),
                    'beta': float(self.beta),
                    'ratio': float(self.upsilon) / float(self.beta),
                    'koppa': float(self.koppa),
                    'rho': self.rho,
                    'upsilon_unreduced': self.upsilon_num_unreduced,
                    'beta_unreduced': self.beta_num_unreduced
                })
        return results

# Test seeds with Fibonacci primes
seeds = [
    (UnreducedRational(13, 11), UnreducedRational(13, 7)),
    (UnreducedRational(19, 7), UnreducedRational(89, 11)),
    (UnreducedRational(2, 1), UnreducedRational(3, 1)),
    (UnreducedRational(5, 1), UnreducedRational(13, 1)),
    (UnreducedRational(22, 7), UnreducedRational(3, 11)),
    (UnreducedRational(89, 1), UnreducedRational(233, 1))  # Fibonacci primes
]

import random

# Run simulations
for i, (u_seed, b_seed) in enumerate(seeds):
    engine = TRTSEngine(psi_mode='PSI_D', kappa_mode='KAPPA_A', engine_mode='ENG_Q')
    engine.initialize_state(u_seed, b_seed)
    results = engine.execute_tick(total_steps=500)
    
    # Analyze final state
    final = results[-1]
    print(f"Seed {i+1}: ({u_seed}, {b_seed})")
    print(f"  Final ratio: {final['ratio']:.6f}")
    print(f"  Final kappa: {final['koppa']:.6f}")
    print(f"  Prime triggers: {sum(1 for r in results if r['rho'] == 1)}")
    print(f"  Converged to √2: {abs(final['ratio'] - math.sqrt(2)) < 1e-5}")
    print(f"  Converged to 1.0: {abs(final['ratio'] - 1.0) < 1e-5}")
    print()

# Check for fine-structure constant approximation
alpha = 1 / 137.035999084
print(f"Fine-structure constant (α): {alpha:.10f}")
print("Checking if any ratios approximate α...")
for i, (u_seed, b_seed) in enumerate(seeds):
    engine = TRTSEngine(psi_mode='PSI_D', kappa_mode='KAPPA_A', engine_mode='ENG_Q')
    engine.initialize_state(u_seed, b_seed)
    results = engine.execute_tick(total_steps=500)
    final_ratio = results[-1]['ratio']
    if abs(final_ratio - alpha) < 0.001:  # Allow some tolerance
        print(f"Seed {i+1} approximates α: {final_ratio:.6f} vs {alpha:.6f}")
