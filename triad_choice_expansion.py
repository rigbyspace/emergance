import argparse
import sys
from sympy import isprime

# Fibonacci primes for seed options
FIBONACCI_PRIMES = [2, 3, 5, 13, 89, 233, 1597]

class RigbySpaceEngine:
    def __init__(self, seed_u, seed_b, psi_behavior='forced', koppa_behavior='dump'):
        self.upsilon = seed_u  # (num, den)
        self.beta = seed_b      # (num, den)
        self.koppa = []  # ϙ - holds imbalances as list of rationals
        self.koppa_behavior = koppa_behavior
        self.psi_behavior = psi_behavior
        self.emission_history = []
        self.rho_active = False
        self.microtick = 0
        self.tick = 0
        self.psi_fired = False
        
    def check_prime_external(self, rational):
        """External prime check without disturbing propagation"""
        num, den = rational
        abs_num = abs(num)
        abs_den = abs(den)
        return isprime(abs_num), isprime(abs_den)
    
    def psi_transform(self, upsilon, beta):
        """Ψ-transformation: (a/b, c/d) → (d/a, b/c)"""
        a, b = upsilon
        c, d = beta
        return ((d, a), (b, c))
    
    def handle_koppa(self, imbalance):
        """Handle koppa based on behavior mode"""
        if self.koppa_behavior == 'dump':
            # Dump to mt1 and reset - stored for next mt1
            self.koppa.append(imbalance)
        elif self.koppa_behavior == 'accumulate':
            # Accumulate endlessly
            self.koppa.append(imbalance)
        elif self.koppa_behavior == 'pop':
            # Hold value, add new, pop oldest if more than 1
            self.koppa.append(imbalance)
            if len(self.koppa) > 1:
                self.koppa.pop(0)
    
    def apply_koppa_dump(self):
        """Apply koppa dump at mt1 if behavior is 'dump'"""
        if self.koppa_behavior == 'dump' and self.koppa:
            # Dump the first value and reset
            dumped_value = self.koppa.pop(0)
            # Simple effect: modify upsilon with dumped value (example logic)
            self.upsilon = (self.upsilon[0] + dumped_value[0], self.upsilon[1] + dumped_value[1])
    
    def propagate_microtick(self):
        """Pure TRTS propagation with refined rules"""
        self.microtick += 1
        role = 'E' if self.microtick in [1,2,3,4] else 'M' if self.microtick in [5,6,7,8] else 'R'
        
        # Epsilon microticks (1,4,7,10) - check for primes and set rho
        if self.microtick in [1,4,7,10]:
            prime_num, prime_den = self.check_prime_external(self.upsilon)
            if prime_num or prime_den:
                self.rho_active = True
                emission_type = 'NUM' if prime_num else 'DEN' if prime_den else 'BOTH'
                self.emission_history.append({
                    'tick': self.tick,
                    'microtick': self.microtick,
                    'role': role,
                    'type': emission_type,
                    'upsilon': self.upsilon,
                    'beta': self.beta
                })
            # Autoset rho on mt10 if no emission occurred
            if self.microtick == 10 and not self.rho_active:
                self.rho_active = True
                self.emission_history.append({
                    'tick': self.tick,
                    'microtick': self.microtick,
                    'role': role,
                    'type': 'FORCED',
                    'upsilon': self.upsilon,
                    'beta': self.beta
                })
        
        # Mu microticks (2,5,8,11) - handle psi based on behavior
        if self.microtick in [2,5,8,11]:
            psi_should_fire = False
            if self.psi_behavior == 'forced' and self.microtick == 11:
                psi_should_fire = True
            elif self.psi_behavior == 'rho' and self.rho_active:
                psi_should_fire = True
            elif self.psi_behavior == 'mu':
                psi_should_fire = True  # All mu microticks
            elif self.psi_behavior == 'rho_mstep' and (self.rho_active or self.microtick in [5,8]):
                psi_should_fire = True
            
            # Psi always fires at mt11 regardless of behavior
            if self.microtick == 11:
                psi_should_fire = True
            
            if psi_should_fire:
                self.upsilon, self.beta = self.psi_transform(self.upsilon, self.beta)
                self.psi_fired = True
                # Pass imbalance to koppa (imbalance as product difference example)
                imbalance = (self.upsilon[0] * self.beta[1], self.upsilon[1] * self.beta[0])
                self.handle_koppa(imbalance)
                self.rho_active = False  # Reset rho after psi
        
        # Apply koppa dump at mt1 if behavior is 'dump'
        if self.microtick == 1 and self.koppa_behavior == 'dump':
            self.apply_koppa_dump()
        
        # Reset microtick after 11
        if self.microtick == 11:
            self.microtick = 0
            self.tick += 1
            self.psi_fired = False

def main():
    parser = argparse.ArgumentParser(description='RigbySpace Engine with CLI options')
    parser.add_argument('--seed_u', type=str, default='1/11', help='Upsilon seed as a/b')
    parser.add_argument('--seed_b', type=str, default='1/7', help='Beta seed as a/b')
    parser.add_argument('--psi', type=str, choices=['forced', 'rho', 'mu', 'rho_mstep'], default='forced', help='Psi behavior')
    parser.add_argument('--koppa', type=str, choices=['dump', 'accumulate', 'pop'], default='dump', help='Koppa behavior')
    parser.add_argument('--ticks', type=int, default=50, help='Number of ticks to simulate')
    parser.add_argument('--fib_seed', action='store_true', help='Use Fibonacci primes for seeds')
    
    args = parser.parse_args()
    
    # Parse seeds
    if args.fib_seed:
        # Use Fibonacci primes: first for upsilon num, second for beta num
        seed_u = (FIBONACCI_PRIMES[0], 11)  # e.g., 2/11
        seed_b = (FIBONACCI_PRIMES[1], 7)   # e.g., 3/7
    else:
        u_parts = args.seed_u.split('/')
        b_parts = args.seed_b.split('/')
        seed_u = (int(u_parts[0]), int(u_parts[1]))
        seed_b = (int(b_parts[0]), int(b_parts[1]))
    
    engine = RigbySpaceEngine(seed_u, seed_b, args.psi, args.koppa)
    
    print(f"Starting RigbySpace Propagation")
    print(f"Seeds: υ={seed_u}, β={seed_b}")
    print(f"Psi behavior: {args.psi}, Koppa behavior: {args.koppa}")
    print(f"Ticks: {args.ticks}")
    print("-" * 50)
    
    # Run propagation
    for i in range(args.ticks * 11):
        engine.propagate_microtick()
        
        if engine.microtick == 0:  # End of tick
            product = (engine.upsilon[0] * engine.beta[0], engine.upsilon[1] * engine.beta[1])
            print(f"Tick {engine.tick}: υ={engine.upsilon}, β={engine.beta}, product={product}")
    
    # Summary
    print("\n" + "="*50)
    print("SIMULATION SUMMARY")
    print(f"Total emissions: {len(engine.emission_history)}")
    print(f"Koppa size: {len(engine.koppa)}")
    
    # Emission analysis by role
    role_counts = {'E': 0, 'M': 0, 'R': 0}
    for e in engine.emission_history:
        role_counts[e['role']] += 1
    print(f"Emissions by role: E={role_counts['E']}, M={role_counts['M']}, R={role_counts['R']}")
    
    # Check product invariance
    initial_product = (seed_u[0] * seed_b[0], seed_u[1] * seed_b[1])
    final_product = (engine.upsilon[0] * engine.beta[0], engine.upsilon[1] * engine.beta[1])
    print(f"Initial product: {initial_product}")
    print(f"Final product: {final_product}")
    print(f"Product invariant: {initial_product == final_product}")

if __name__ == '__main__':
    main()
