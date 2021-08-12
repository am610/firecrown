"""The module mapping provides facilities for mapping the cosmological constants
used by one body of code to another. This is done by defining one of the codes
(pyccl) as being the 'standard', and for all other supported code, providing
functions from_ccl and to_ccl.

The supported codes include:
    pyccl
    CAMB (Fortran convention)
    pycamb (similar but not identical to the CAMB Fortran convention)
    CLASS
    Cobaya
    CosmoSIS
"""
import numpy as np


def redshift_to_scale_factor(z, p_k):
    """Given arrays of redshift and a (2d) power spectrum ordered by redshift,
    return an array of scale factor and the equivalent power spectrum ordered
    by scale factor."""
    scale = np.flip(1.0 / (1.0 + z))
    p_k_out = np.flipud(p_k)
    return scale, p_k_out


def require_type(val, typ, typename):
    """If val is of type typ, return it; else raise a TypeError with a message
    '{typename} value is required'
    """
    if type(val) is typ:
        return val
    raise TypeError(f"{typename} value is required")


def require_float(val):
    return require_type(val, float, "float")


def require_string(val):
    return require_type(val, str, "string")


# TODO: Consider creating several dataclasses, each for a specific
# parameterization of the cosmology. This will do away with the need
# to preserve invariants (like that relating sigma_8 and A_s), which
# will become untenable if the constraints become nontrivial.


class PyCCLCosmologyConstants:
    def __init__(
        self,
        *,
        Omega_c,
        Omega_b,
        h,
        A_s=None,
        sigma8=None,
        n_s,
        Omega_k,
        Neff,
        m_nu,
        m_nu_type,
        w0,
        wa,
        T_CMB,
    ):
        """Construct an object suitable for use in constructing a pyccl.core.CosmologyCalculator. See the
        documentation of that class for an explanation of the choices and meanings of default values of
        None.
        """

        # We typecheck arguments to avoid very confusing error messages at a later time in case
        # of error.
        self.Omega_c = require_float(Omega_c)
        self.Omega_b = require_float(Omega_b)
        self.h = require_float(h)

        if A_s is not None and sigma8 is not None:
            raise ValueError("Exactly one of A_s and sigma8 must be supplied")
        if sigma8 is None:
            self.A_s = require_float(A_s)
            self.sigma8 = None
        else:
            self.A_s = None
            self.sigma8 = require_float(sigma8)

        self.n_s = require_float(n_s)
        self.Omega_k = require_float(Omega_k)
        self.Omega_g = None
        self.Neff = require_float(Neff)
        self.m_nu = require_float(m_nu)
        self.m_nu_type = require_string(m_nu_type)
        self.w0 = require_float(w0)
        self.wa = require_float(wa)
        self.T_CMB = require_float(T_CMB)

    def asdict(self):
        return {
            "Omega_c": self.Omega_c,
            "Omega_b": self.Omega_b,
            "h": self.h,
            "A_s": self.A_s,
            "sigma8": self.sigma8,
            "n_s": self.n_s,
            "Omega_k": self.Omega_k,
            "Omega_g": self.Omega_g,
            "Neff": self.Neff,
            "m_nu": self.m_nu,
            "m_nu_type": self.m_nu_type,
            "w0": self.w0,
            "wa": self.wa,
            "T_CMB": self.T_CMB,
        }


def from_cosmosis_camb(cosmosis_params: dict):
    """Return a PyCCLCosmologyConstants object with parameters equivalent to
    those read from CosmoSIS when using CAMB."""
    # TODO: Verify that CosmoSIS/CAMB does not use Omega_g
    # TODO: Verify that CosmoSIS/CAMB uses delta_neff, not N_eff
    Omega_c = cosmosis_params["omega_c"]
    Omega_b = cosmosis_params["omega_b"]
    h = cosmosis_params["h0"]  # Not 'hubble' !
    sigma8 = cosmosis_params["sigma_8"]
    n_s = cosmosis_params["n_s"]
    Omega_k = cosmosis_params["omega_k"]
    # Read omega_nu from CosmoSIS (in newer CosmoSIS)
    # Read m_nu from CosmoSIS (in newer CosmoSIS)
    Neff = cosmosis_params.get("delta_neff", 0.0) + 3.046  # Verify this with Joe
    m_nu = cosmosis_params["omega_nu"] * h * h * 93.14
    m_nu_type = "normal"
    w0 = cosmosis_params["w"]
    wa = cosmosis_params["wa"]
    return PyCCLCosmologyConstants(
        Omega_c=Omega_c,
        Omega_b=Omega_b,
        h=h,
        sigma8=sigma8,
        n_s=n_s,
        Omega_k=Omega_k,
        Neff=Neff,
        m_nu=m_nu,
        m_nu_type=m_nu_type,
        w0=w0,
        wa=-wa,
        T_CMB=2.7255,  # Modify CosmoSIS to make this available in the datablock
    )