# Let's analyze the emission patterns more deeply, focusing on epsilon microticks and the rho-psi-koppa chain

print("=== Detailed Emission Analysis ===")

# Group emissions by microtick and type
epsilon_emissions = [e for e in emissions if e['microtick'] in [1, 4, 7, 10]]
mu_emissions = [e for e in emissions if e['microtick'] in [2, 5, 8, 11]]
phi_emissions = [e for e in emissions if e['microtick'] in [3, 6, 9]]

print(f"Epsilon emissions (mt 1,4,7,10): {len(epsilon_emissions)}")
print(f"Mu emissions (mt 2,5,8,11): {len(mu_emissions)}") 
print(f"Phi emissions (mt 3,6,9): {len(phi_emissions)}")

# Analyze the rho-psi-koppa chain
print(f"\n=== Rho-Psi-Koppa Chain Analysis ===")
print(f"Total rho events (emissions at epsilon): {len(epsilon_emissions)}")
print(f"Total psi activations (koppa entries): {len(koppa_entries)}")

# Check if every rho event leads to a psi activation on the next mu step
rho_to_psi_pairs = []
for emission in epsilon_emissions:
    emission_tick = emission['tick']
    emission_microtick = emission['microtick']
    
    # Find the corresponding mu step (next microtick in same tick, or first mu of next tick)
    if emission_microtick in [1, 4, 7]:
        # Next microtick in same tick is the mu step
        target_microtick = emission_microtick + 1
        target_tick = emission_tick
    else:  # emission_microtick == 10
        # Next mu step is microtick 2 of next tick
        target_microtick = 2
        target_tick = emission_tick + 1
    
    # Look for koppa entry at this target
    corresponding_koppa = None
    for koppa in koppa_entries:
        if koppa['tick'] == target_tick and koppa['microtick'] == target_microtick:
            corresponding_koppa = koppa
            break
    
    rho_to_psi_pairs.append({
        'emission': emission,
        'koppa_entry': corresponding_koppa,
        'matched': corresponding_koppa is not None
    })

matched_pairs = [p for p in rho_to_psi_pairs if p['matched']]
print(f"Rho events that successfully triggered psi on next mu step: {len(matched_pairs)}/{len(rho_to_psi_pairs)} ({len(matched_pairs)/len(rho_to_psi_pairs)*100:.1f}%)")

# Analyze the imbalance values in koppa
if koppa_entries:
    imbalance_values = [entry['imbalance'] for entry in koppa_entries]
    print(f"\n=== Koppa Imbalance Analysis ===")
    print(f"First imbalance: {imbalance_values[0]}")
    print(f"Last imbalance: {imbalance_values[-1]}")
    
    # Check if imbalance is conserved (product invariance)
    unique_imbalances = set(imbalance_values)
    print(f"Unique imbalance values: {len(unique_imbalances)}")
    if len(unique_imbalances) == 1:
        print("IMBALANCE IS CONSERVED - Product invariance holds perfectly!")
    else:
        print("Imbalance varies - investigating patterns...")
        # Convert to floats for analysis
        imbalance_floats = []
        for num, den in imbalance_values:
            if den != 0:
                imbalance_floats.append(num/den)
            else:
                imbalance_floats.append(float('inf'))
        
        if len(imbalance_floats) > 1 and all(val != float('inf') for val in imbalance_floats):
            min_imb = min(imbalance_floats)
            max_imb = max(imbalance_floats)
            print(f"Imbalance range: {min_imb:.6f} to {max_imb:.6f}")
            print(f"Imbalance variance: {max_imb - min_imb:.2e}")

# Let's also track the state evolution and look for convergence patterns
print(f"\n=== State Evolution Analysis ===")
upsilon_values = [r['upsilon_val'] for r in results if r['upsilon_val'] != float('inf')]
beta_values = [r['beta_val'] for r in results if r['beta_val'] != float('inf')]

if upsilon_values and beta_values:
    print(f"Upsilon range: {min(upsilon_values):.6f} to {max(upsilon_values):.6f}")
    print(f"Beta range: {min(beta_values):.6f} to {max(beta_values):.6f}")
    
    # Check convergence to fundamental constants
    fundamental_constants = {
        '1/√2': 1/2**0.5,
        '√2': 2**0.5, 
        'φ (golden)': (1 + 5**0.5)/2,
        '1/φ': 2/(1 + 5**0.5)
    }
    
    print(f"\n=== Convergence to Fundamental Constants ===")
    final_upsilon = upsilon_values[-1]
    final_beta = beta_values[-1]
    
    for name, value in fundamental_constants.items():
        upsilon_dev = abs(final_upsilon - value)
        beta_dev = abs(final_beta - value)
        print(f"{name} ({value:.6f}):")
        print(f"  υ deviation: {upsilon_dev:.6f} ({upsilon_dev/value*100:.2f}%)")
        print(f"  β deviation: {beta_dev:.6f} ({beta_dev/value*100:.2f}%)")

# Let's run a longer simulation to see if we can observe the tick-137 phase transition
print(f"\n=== Extended Simulation for Phase Transition Analysis ===")
engine_extended = RigbySpaceEngine(seed_u_num=1, seed_u_den=11, seed_b_num=1, seed_b_den=7)
results_extended = engine_extended.run_propagation(ticks=150)  # Run to 150 ticks to approach 137

emissions_extended = engine_extended.emission_history

# Analyze emissions before and after tick 137
emissions_pre_137 = [e for e in emissions_extended if e['tick'] < 137]
emissions_post_137 = [e for e in emissions_extended if e['tick'] >= 137]

print(f"Emissions before tick 137: {len(emissions_pre_137)}")
print(f"Emissions after tick 137: {len(emissions_post_137)}")

if emissions_pre_137 and emissions_post_137:
    rate_pre = len(emissions_pre_137) / 137
    remaining_ticks = 150 - 137
    rate_post = len(emissions_post_137) / remaining_ticks if remaining_ticks > 0 else 0
    
    print(f"Emission rate before tick 137: {rate_pre:.3f} per tick")
    print(f"Emission rate after tick 137: {rate_post:.3f} per tick")
    
    if rate_pre > 0:
        change = ((rate_post - rate_pre) / rate_pre) * 100
        print(f"Change at tick 137: {change:+.1f}%")
        
        if abs(change) > 5:  # Significant change threshold
            print("SIGNIFICANT PHASE TRANSITION DETECTED AT TICK 137!")
        else:
            print("No significant phase transition detected at tick 137 in this simulation.")
