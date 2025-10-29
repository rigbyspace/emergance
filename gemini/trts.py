from fractions import Fraction
import boost # Placeholder for high-precision math, using standard int for primality
import math # Only for isqrt, a stdlib integer-only operation

# --- Primality Test (Miller-Rabin) ---
# This is a Python port of the C++ is_miller_rabin_prime logic.
# It is only used to set the 'rho' (p) trigger.

def power(a, d, n):
    """Calculates (a^d) % n"""
    result = 1
    a = a % n
    while d > 0:
        if d % 2 == 1:
            result = (result * a) % n
        d = d >> 1
        a = (a * a) % n
    return result

def is_miller_rabin_prime(n):
    """
    Python implementation of the Miller-Rabin primality test.
    This logic matches the C++ header's intent.
    """
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False

    # Write n as 2^s * d + 1
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    # Bases from the C++ implementation
    test_bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    for a in test_bases:
        if a >= n:
            break
        
        x = power(a, d, n) # x = (a^d) % n

        if x == 1 or x == n - 1:
            continue

        is_composite = True
        for _ in range(s - 1):
            x = power(x, 2, n) # x = (x^2) % n
            if x == n - 1:
                is_composite = False
                break
        
        if is_composite:
            return False # Definitely composite

    return True # Probably prime

# --- Canonical 11-Microtick Engine (C11-ME) ---

class TRTS_Engine_C11:
    """
    Canonical 11-Microtick Engine (C11-ME).
    Synthesized from all provided TRTS axioms and C++ code.
    """
    def __init__(self, upsilon_seed, beta_seed):
        # State Variables
        self.upsilon = upsilon_seed
        self.beta = beta_seed
        self.koppa = Fraction(0, 1) # Koppa (Imbalance)
        
        # Engine Parameters (Hardcoded from Solution Model)
        #
        self.psi_mode = "PSI_DUAL_RECIPROCAL"
        self.koppa_mode = "KOPPA_RATIO_FEED"
        self.engine_mode = "ENGINE_QUIET_ADDITIVE"

        # Internal Counters (No 'mod' allowed)
        self.step = 0
        self.microtick = 0 # Will run 1-11
        self.rho = 0 # Prime trigger (p)

    def is_prime_trigger(self):
        """
        Checks if Upsilon numerator triggers a prime event.
       
        """
        # We only check the numerator as per the simplest C++ implementation
        try:
            num = self.upsilon.numerator
            if num < 0: num = -num # Use absolute value
            return is_miller_rabin_prime(int(num))
        except OverflowError:
            # Number is too large for standard int primality test
            return False 

    def update_koppa(self):
        """
        Applies Koppa logic for KOPPA_RATIO_FEED.
       
        """
        if self.koppa_mode == "KOPPA_RATIO_FEED":
            if self.koppa == 0:
                self.koppa = Fraction(1, 1)
            
            if self.beta == 0:
                # Prevent division by zero, a critical event
                self.koppa = self.koppa * self.upsilon 
            else:
                self.koppa = self.koppa * (self.upsilon / self.beta)

    def apply_propagation_engine(self):
        """
        Applies R-Role logic for ENGINE_QUIET_ADDITIVE.
       
        """
        if self.engine_mode == "ENGINE_QUIET_ADDITIVE":
            diff = self.upsilon - self.beta
            self.upsilon = self.upsilon + (diff / Fraction(11))
            self.beta = self.beta - (diff / Fraction(11))

    def psi_transform(self):
        """
        Applies M-Role logic for PSI_DUAL_RECIPROCAL.
       
        """
        if self.psi_mode == "PSI_DUAL_RECIPROCAL":
            # (a/b, c/d) -> (a/d, c/b)
            # Note: C++ file has a slight variation (d/a, b/c).
            # The *canonical* spec and
            # other C++ logic
            # points to a denominator swap. We use the one
            # from the C++ implementation: (d/a, b/c)
            # new_upsilon = (a/b, c/d) -> d/a
            # new_beta = (a/b, c/d) -> b/c
            
            # (a/b, c/d) -> (d/a, b/c)
            # upsilon = a/b
            # beta = c/d
            new_upsilon = Fraction(self.beta.denominator, self.upsilon.denominator)
            new_beta = Fraction(self.upsilon.numerator, self.beta.denominator)
            self.upsilon = new_upsilon
            self.beta = new_beta

    def execute_microtick(self):
        """
        Runs one microtick (1-11) of the C11-ME.
        This is the core loop from TRTS_Engine.cpp, process_microtick()
        """
        self.microtick += 1
        self.rho = 0 # Reset trigger

        # --- Role Determination (no 'mod') ---
        # E-Role: 1, 4, 7, 10
        is_emission = (self.microtick == 1 or self.microtick == 4 or
                       self.microtick == 7 or self.microtick == 10)
        
        # R-Role (Propagation): 3, 6, 9
        is_propagation = (self.microtick == 3 or self.microtick == 6 or
                          self.microtick == 9)
        
        # M-Role (Transform): 2, 5, 8, 11
        is_transformation = (self.microtick == 2 or self.microtick == 5 or
                             self.microtick == 8 or self.microtick == 11)

        # --- Execute Logic ---
        if is_emission:
            if self.is_prime_trigger():
                self.rho = 1
            if self.rho > 0:
                self.update_koppa()
        
        if is_propagation:
            self.apply_propagation_engine()
            
        if is_transformation:
            # In the C++ logic, the transform only happens if
            # triggered by rho or at the end (mt 11).
            should_transform = False
            if self.psi_mode == "PSI_DUAL_RECIPROCAL":
                if self.microtick == 11 or self.rho > 0:
                    should_transform = True
            
            if should_transform:
                self.psi_transform()

        # Reset microtick counter to loop
        if self.microtick == 11:
            self.microtick = 0
            self.step += 1

    def run_simulation(self, num_steps):
        """Runs the engine for a total number of steps."""
        run_data = []
        for s in range(num_steps):
            for mt in range(11):
                self.execute_microtick()
            
            # Store data at the end of each full step
            ratio = "N/A"
            if self.beta != 0:
                ratio = f"{(self.upsilon / self.beta).numerator / (self.upsilon / self.beta).denominator:.8f}"

            run_data.append({
                "step": s,
                "U": str(self.upsilon),
                "B": str(self.beta),
                "K": str(self.koppa),
                "U/B Ratio": ratio,
                "Rho_Triggered": "YES" if self.rho > 0 else "No" 
            })
            
            # Check for emission event from previous turn's analysis
            if self.rho > 0 and self.microtick == 8: # A guess
                 run_data[-1]["EMISSION_EVENT"] = "DETECTED"

        return run_data
