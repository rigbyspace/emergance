import math
from fractions import Fraction
from sympy import isprime
import numpy as np
import matplotlib.pyplot as plt

class RigbySpaceEngine:
    def __init__(self, seed_u_num=1, seed_u_den=11, seed_b_num=1, seed_b_den=7):
        # Pure rational propagation - no normalization, no GCD
        self.upsilon = (seed_u_num, seed_u_den)  # υ
        self.beta = (seed_b_num, seed_b_den)      # β
        self.koppa_ledger = []  # ϙ - imbalance tracking
        self.emission_history = []
        self.microtick = 0
        self.tick = 0
        
    def psi_transform(self, upsilon, beta):
        """Ψ-transformation: (a/b, c/d) → (d/a, b/c)"""
        a, b = upsilon
        c, d = beta
        return ((d, a), (b, c))
    
    def check_prime_external(self, rational):
        """External prime check without disturbing propagation"""
        num, den = rational
        # Take absolute value for prime check only
        abs_num = abs(num)
        abs_den = abs(den)
        return isprime(abs_num), isprime(abs_den)
    
    def propagate_microtick(self):
        """Pure TRTS cycle propagation"""
        self.microtick += 1
        
        # Role mapping based on microtick
        if self.microtick in [1, 2, 3, 4]:
            role = 'E'
        elif self.microtick in [5, 6, 7, 8]:
            role = 'M' 
        else:
            role = 'R'
            
        # Apply Ψ-transformation at appropriate microticks
        if self.microtick in [2, 5, 8, 11]:
            self.upsilon, self.beta = self.psi_transform(self.upsilon, self.beta)
            
        # Check for emission (external snapshot)
        prime_num, prime_den = self.check_prime_external(self.upsilon)
        
        # Emission conditions
        emission = False
        emission_type = None
        
        if prime_num or prime_den:
            emission = True
            if prime_num and prime_den:
                emission_type = 'BOTH'
            elif prime_num:
                emission_type = 'NUM'
            else:
                emission_type = 'DEN'
                
        # Forced emission at microtick 10
        if self.microtick == 10:
            emission = True
            emission_type = 'FORCED'
            
        if emission:
            self.emission_history.append({
                'tick': self.tick,
                'microtick': self.microtick,
                'role': role,
                'type': emission_type,
                'upsilon': self.upsilon,
                'beta': self.beta
            })
            
            # Update koppa ledger with imbalance
            imbalance = (self.upsilon[0] * self.beta[1], self.upsilon[1] * self.beta[0])
            self.koppa_ledger.append(imbalance)
            
        # Reset microtick every 11 microticks
        if self.microtick == 11:
            self.microtick = 0
            self.tick += 1
            
    def get_product(self):
        """Calculate υ·β product (external evaluation)"""
        u_num, u_den = self.upsilon
        b_num, b_den = self.beta
        return (u_num * b_num, u_den * b_den)
        
    def run_propagation(self, ticks=200):
        """Run pure propagation for specified ticks"""
        results = []
        
        for i in range(ticks * 11):  # 11 microticks per tick
            self.propagate_microtick()
            
            if self.microtick == 0:  # End of full tick
                product = self.get_product()
                u_num, u_den = self.upsilon
                b_num, b_den = self.beta
                
                # External evaluation only - convert to float for analysis
                u_val = u_num / u_den if u_den != 0 else float('inf')
                b_val = b_num / b_den if b_den != 0 else float('inf')
                product_val = product[0] / product[1] if product[1] != 0 else float('inf')
                
                results.append({
                    'tick': self.tick,
                    'upsilon': (u_num, u_den),
                    'beta': (b_num, b_den),
                    'product': product,
                    'upsilon_val': u_val,
                    'beta_val': b_val,
                    'product_val': product_val
                })
                
        return results

# Initialize and run the engine
print("=== RIGBYSPACE ENGINE - PURE PROPAGATION ===")
print("Seeds: υ = 1/11, β = 1/7")
print("Rules: No GCD, no normalization, no continuum contamination")
print("Product invariance: υ·β must remain constant")
print()

engine = RigbySpaceEngine()
results = engine.run_propagation(ticks=200)

# Analyze results
print("=== PROPAGATION ANALYSIS ===")

# Check product invariance
initial_product = results[0]['product_val']
final_product = results[-1]['product_val']
product_variance = abs(final_product - initial_product)

print(f"Initial product υ·β: {initial_product:.10f}")
print(f"Final product υ·β: {final_product:.10f}")
print(f"Product variance: {product_variance:.2e}")
print()

# Analyze emissions
emissions_by_role = {'E': 0, 'M': 0, 'R': 0}
emissions_by_microtick = {1:0, 4:0, 7:0, 10:0}

for emission in engine.emission_history:
    emissions_by_role[emission['role']] += 1
    if emission['microtick'] in [1, 4, 7, 10]:
        emissions_by_microtick[emission['microtick']] += 1

print("=== EMISSION DISTRIBUTION ===")
print(f"Total emissions: {len(engine.emission_history)}")
print("By role:")
for role, count in emissions_by_role.items():
    print(f"  {role}: {count} ({count/len(engine.emission_history)*100:.1f}%)")
print("By key microticks:")
for mt, count in emissions_by_microtick.items():
    print(f"  mt{mt}: {count}")

# Check convergence to fundamental constants
print("\n=== CONVERGENCE ANALYSIS ===")
sqrt2 = math.sqrt(2)
golden_ratio = (1 + math.sqrt(5)) / 2

recent_upsilons = [r['upsilon_val'] for r in results[-20:]]
avg_upsilon = np.mean(recent_upsilons)

deviations = {
    '1/√2': abs(avg_upsilon - 1/sqrt2),
    '√2': abs(avg_upsilon - sqrt2), 
    'φ': abs(avg_upsilon - golden_ratio)
}

closest_constant = min(deviations, key=deviations.get)
print(f"Average recent υ: {avg_upsilon:.6f}")
print(f"Closest to {closest_constant}: deviation = {deviations[closest_constant]:.6f}")

# Phase transition analysis around tick 137
print("\n=== PHASE TRANSITION ANALYSIS (tick 137) ===")
pre_137_emissions = len([e for e in engine.emission_history if e['tick'] < 137])
post_137_emissions = len([e for e in engine.emission_history if e['tick'] >= 137])

print(f"Emissions before tick 137: {pre_137_emissions}")
print(f"Emissions after tick 137: {post_137_emissions}")
if pre_137_emissions > 0:
    change_pct = (post_137_emissions - pre_137_emissions) / pre_137_emissions * 100
    print(f"Change: {change_pct:+.1f}%")

print("\n=== KOMPPA LEDGER SUMMARY ===")
print(f"Total imbalance events: {len(engine.koppa_ledger)}")
if engine.koppa_ledger:
    avg_imbalance = np.mean([i[0]/i[1] for i in engine.koppa_ledger if i[1] != 0])
    print(f"Average imbalance: {avg_imbalance:.4f}")
