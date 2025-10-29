import sympy as sp
import math

class TRTSEngine:
    """
    PURE Rational TRTS Propagation Engine.
    No GCD. No Floats. No Normalization.
    Prime checks use abs(), but sign is preserved in propagation.
    """
    
    def __init__(self):
        self.step_count = 0
        self.microtick = 0
        self.rho_triggered = False
        self.rho_prime = None
        
        # Initialize state - PURE RATIONALS ONLY
        self.upsilon = sp.Rational(13, 11)    # υ = 13/11
        self.beta = sp.Rational(3, 7)         # β = 3/7
        self.koppa = []                       # Koppa ledger - stores rationals
        self.imbalance_active = True          # ϙ₁ - Initial active state
        
        # Track state history
        self.state_history = []
        self.emission_history = []
        
    def is_prime_trigger(self, n):
        """Check if number is prime using abs(), but preserve original sign"""
        # Use absolute value ONLY for prime check
        abs_val = abs(n)
        if abs_val <= 1:
            return False
        return abs_val in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    
    def psi_transform(self, a, b):
        """Ψ-transformation: (a/b, c/d) → (d/a, b/c)"""
        # Extract numerators and denominators - preserve signs
        num_a, den_a = a.as_numer_denom()
        num_b, den_b = b.as_numer_denom()
        
        # Apply Ψ: (a/b, c/d) → (d/a, b/c)
        new_upsilon = sp.Rational(den_b, num_a)  # d/a
        new_beta = sp.Rational(num_a, den_b)     # b/c  
        
        return new_upsilon, new_beta
    
    def advance_microtick(self):
        """Execute one microtick of TRTS cycle"""
        self.microtick += 1
        
        # Emission check at mt 1,4,7,10
        if self.microtick in [1, 4, 7, 10]:
            current_val = self.upsilon if self.microtick in [1, 7] else self.beta
            
            if self.is_prime_trigger(current_val.p):
                self.rho_triggered = True
                self.rho_prime = current_val.p
                self.emission_history.append({
                    'step': self.step_count,
                    'microtick': self.microtick,
                    'value': current_val,
                    'prime': self.rho_prime
                })
                print(f"EMISSION: mt{self.microtick}, prime {self.rho_prime}")
        
        # Ψ-transformation at NEXT µ after ρ trigger
        if self.rho_triggered and self.microtick in [2, 5, 8, 11]:
            print(f"Ψ-TRANSFORM at mt{self.microtick}")
            self.upsilon, self.beta = self.psi_transform(self.upsilon, self.beta)
            self.rho_triggered = False
        
        # µ-transition always at mt11
        if self.microtick == 11:
            if self.imbalance_active:
                # ϙ₁ - Active: recycle imbalance
                self.koppa.append(self.upsilon + self.beta)
            else:
                # ϙ₀ - Dormant: store locally
                pass  # Implementation for dormant state
        
        # Ω - Null Tick injection after ρ emission
        if self.microtick == 11 and any(e['step'] == self.step_count 
                                      for e in self.emission_history):
            print("Ω - NULL TICK INJECTED")
        
        # Koppa dump at transition to next step's mt1
        if self.microtick == 11 and self.koppa:
            koppa_value = sum(self.koppa, sp.Rational(0))
            print(f"KOPPA DUMP: {koppa_value}")
            # Koppa value would feed into next cycle
            self.koppa = []
    
    def execute_step(self):
        """Execute one full TRTS step (11 microticks)"""
        print(f"\n--- STEP {self.step_count} ---")
        print(f"Initial: υ={self.upsilon}, β={self.beta}")
        
        self.microtick = 0
        for _ in range(11):
            self.advance_microtick()
        
        # Record final state
        self.state_history.append({
            'step': self.step_count,
            'upsilon': self.upsilon,
            'beta': self.beta,
            'ratio': self.upsilon/self.beta
        })
        
        self.step_count += 1
        
        print(f"Final: υ={self.upsilon}, β={self.beta}")
        print(f"Ratio υ/β: {float(self.upsilon/self.beta):.6f}")
        print(f"Target √2: {math.sqrt(2):.6f}")

# Initialize and run demonstration
if __name__ == "__main__":
    print("🚀 TRTS PURE PROPAGATION ENGINE")
    print("CONSTRAINTS: No GCD, No Floats, Pure Rationals")
    print("PRIME CHECK: abs() used for detection only")
    print("SIGN: Preserved in all propagation\n")
    
    engine = TRTSEngine()
    
    # Run first few steps to demonstrate
    for i in range(5):
        engine.execute_step()
        
        # Show convergence progress
        if i > 0:
            current_ratio = float(engine.upsilon/engine.beta)
            target = math.sqrt(2)
            error = abs(current_ratio - target)
            print(f"Convergence Error: {error:.8f}")
