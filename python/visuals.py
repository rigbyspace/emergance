import numpy as np
import matplotlib.pyplot as plt
from sympy import isprime
import seaborn as sns

# Reimplement RigbySpace engine for clarity
class RigbySpaceEngine:
    def __init__(self, seed_u=(1,11), seed_b=(1,7), psi_behavior='rho_mstep', koppa_behavior='dump'):
        self.upsilon = seed_u
        self.beta = seed_b
        self.koppa = []
        self.koppa_behavior = koppa_behavior
        self.psi_behavior = psi_behavior
        self.emission_history = []
        self.rho_active = False
        self.microtick = 0
        self.tick = 0
        self.psi_fired = False
        self.trajectory = []

    def check_prime_external(self, rational):
        num, den = rational
        abs_num = abs(num)
        abs_den = abs(den)
        return isprime(abs_num), isprime(abs_den)

    def psi_transform(self, upsilon, beta):
        a, b = upsilon
        c, d = beta
        return ((d, a), (b, c))

    def handle_koppa(self, imbalance):
        if self.koppa_behavior == 'dump':
            self.koppa.append(imbalance)
        elif self.koppa_behavior == 'accumulate':
            self.koppa.append(imbalance)
        elif self.koppa_behavior == 'pop':
            self.koppa.append(imbalance)
            if len(self.koppa) > 1:
                self.koppa.pop(0)

    def apply_koppa_dump(self):
        if self.koppa_behavior == 'dump' and self.koppa:
            dumped_value = self.koppa.pop(0)
            self.upsilon = (self.upsilon[0] + dumped_value[0], self.upsilon[1] + dumped_value[1])

    def propagate_microtick(self):
        self.microtick += 1
        role = 'E' if self.microtick in [1,2,3,4] else 'M' if self.microtick in [5,6,7,8] else 'R'
        
        # Track state for analysis
        if self.microtick == 1:  # Start of new microtick cycle
            self.trajectory.append({
                'tick': self.tick,
                'microtick': self.microtick,
                'upsilon': self.upsilon,
                'beta': self.beta,
                'role': role
            })

        # Epsilon microticks (1,4,7,10) - emission checks
        if self.microtick in [1,4,7,10]:
            prime_num, prime_den = self.check_prime_external(self.upsilon)
            if prime_num or prime_den:
                self.rho_active = True
                emission_type = 'BOTH' if prime_num and prime_den else 'NUM' if prime_num else 'DEN'
                self.emission_history.append({
                    'tick': self.tick,
                    'microtick': self.microtick,
                    'role': role,
                    'type': emission_type,
                    'upsilon': self.upsilon,
                    'beta': self.beta
                })
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

        # Mu microticks (2,5,8,11) - psi transformations
        if self.microtick in [2,5,8,11]:
            psi_should_fire = False
            if self.psi_behavior == 'forced' and self.microtick == 11:
                psi_should_fire = True
            elif self.psi_behavior == 'rho' and self.rho_active:
                psi_should_fire = True
            elif self.psi_behavior == 'mu':
                psi_should_fire = True
            elif self.psi_behavior == 'rho_mstep' and (self.rho_active or self.microtick in [5,8]):
                psi_should_fire = True
            
            if self.microtick == 11:
                psi_should_fire = True
            
            if psi_should_fire:
                self.upsilon, self.beta = self.psi_transform(self.upsilon, self.beta)
                self.psi_fired = True
                imbalance = (self.upsilon[0] * self.beta[1], self.upsilon[1] * self.beta[0])
                self.handle_koppa(imbalance)
                self.rho_active = False

        if self.microtick == 1 and self.koppa_behavior == 'dump':
            self.apply_koppa_dump()

        if self.microtick == 11:
            self.microtick = 0
            self.tick += 1
            self.psi_fired = False

def analyze_propagation_lengths():
    tick_lengths = [75, 100, 200]
    results = {}
    
    for ticks in tick_lengths:
        engine = RigbySpaceEngine(seed_u=(2,11), seed_b=(3,7), psi_behavior='rho_mstep', koppa_behavior='dump')
        
        # Run propagation
        for i in range(ticks * 11):
            engine.propagate_microtick()
        
        # Analyze results
        emissions_pre_137 = len([e for e in engine.emission_history if e['tick'] < 137])
        emissions_post_137 = len([e for e in engine.emission_history if e['tick'] >= 137]) if ticks >= 137 else 0
        
        # Calculate convergence to sqrt(2)
        upsilon_vals = []
        for state in engine.trajectory:
            u_num, u_den = state['upsilon']
            if u_den != 0:
                upsilon_vals.append(u_num / u_den)
        
        sqrt2 = np.sqrt(2)
        convergence_dev = np.abs(np.array(upsilon_vals) - sqrt2).mean() if upsilon_vals else float('inf')
        
        results[ticks] = {
            'total_emissions': len(engine.emission_history),
            'emissions_pre_137': emissions_pre_137,
            'emissions_post_137': emissions_post_137,
            'emission_rate_change': (emissions_post_137 / max(ticks-137,1)) - (emissions_pre_137 / min(137,ticks)) if ticks >= 137 else 0,
            'convergence_to_sqrt2': convergence_dev,
            'role_distribution': {
                'E': len([e for e in engine.emission_history if e['role'] == 'E']),
                'M': len([e for e in engine.emission_history if e['role'] == 'M']),
                'R': len([e for e in engine.emission_history if e['role'] == 'R'])
            }
        }
    
    return results

# Run analysis
results = analyze_propagation_lengths()

# Print results
print("PROPAGATION LENGTH ANALYSIS")
print("=" * 50)
for ticks, data in results.items():
    print(f"Ticks: {ticks}")
    print(f"  Total Emissions: {data['total_emissions']}")
    print(f"  Emissions Pre-137: {data['emissions_pre_137']}")
    print(f"  Emissions Post-137: {data['emissions_post_137']}")
    print(f"  Emission Rate Change: {data['emission_rate_change']:.4f}")
    print(f"  Convergence to √2: {data['convergence_to_sqrt2']:.6f}")
    print(f"  Role Distribution: E={data['role_distribution']['E']}, M={data['role_distribution']['M']}, R={data['role_distribution']['R']}")
    print("-" * 30)

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Emission patterns
tick_labels = list(results.keys())
emission_counts = [results[ticks]['total_emissions'] for ticks in tick_labels]
axes[0,0].bar(tick_labels, emission_counts, color=['blue', 'orange', 'green'])
axes[0,0].set_title('Total Emissions vs Propagation Length')
axes[0,0].set_xlabel('Ticks')
axes[0,0].set_ylabel('Emission Count')

# Convergence to sqrt(2)
convergence_vals = [results[ticks]['convergence_to_sqrt2'] for ticks in tick_labels]
axes[0,1].plot(tick_labels, convergence_vals, marker='o', linewidth=2)
axes[0,1].set_title('Convergence to √2 vs Propagation Length')
axes[0,1].set_xlabel('Ticks')
axes[0,1].set_ylabel('Mean Absolute Deviation')

# Role distribution
role_data = {role: [results[ticks]['role_distribution'][role] for ticks in tick_labels] for role in ['E', 'M', 'R']}
x = np.arange(len(tick_labels))
width = 0.25
axes[1,0].bar(x - width, role_data['E'], width, label='E', color='red')
axes[1,0].bar(x, role_data['M'], width, label='M', color='blue')
axes[1,0].bar(x + width, role_data['R'], width, label='R', color='green')
axes[1,0].set_title('Role Distribution vs Propagation Length')
axes[1,0].set_xlabel('Ticks')
axes[1,0].set_ylabel('Emission Count')
axes[1,0].set_xticks(x)
axes[1,0].set_xticklabels(tick_labels)
axes[1,0].legend()

# Phase transition evidence
rate_changes = [results[ticks]['emission_rate_change'] for ticks in tick_labels]
axes[1,1].bar(tick_labels, rate_changes, color=['gray', 'darkgray', 'black'])
axes[1,1].set_title('Emission Rate Change at Tick 137')
axes[1,1].set_xlabel('Ticks')
axes[1,1].set_ylabel('Rate Change (post-137 - pre-137)')

plt.tight_layout()
plt.show()
