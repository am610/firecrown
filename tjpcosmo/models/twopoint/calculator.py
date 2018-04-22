import pyccl as ccl
from ..base_calculator import TheoryCalculator
from .theory_results import TwoPointTheoryResults
from ...systematics import Systematic, SourceSystematic, OutputSystematic, CosmologySystematic
from ..sources import make_source, LSSSource

def make_fake_source(name, stype, metadata):
    import numpy as np

    z = np.arange(0.0, 2.0, 0.01)
    n_of_z = np.exp(-0.5 * (z - 0.8)**2/0.1**2)
    metadata = {
        "sources":{
            name: {
                "nz": [z, n_of_z]
            }
        }
    }
    return LSSSource(name, stype, metadata)

        # self.z,self.nz = metadata['sources'][name]["nz"]
def convert_cosmobase_to_ccl(cosmo_base):
    # Although these are lower case they are fractions
    # not densities - this is an artifact of cosmosis
    # case insesitivity
    omega_c = cosmo_base.omega_c
    omega_b = cosmo_base.omega_b
    omega_k = cosmo_base.omega_k
    if (cosmo_base.omega_n_rel + cosmo_base.omega_n_mass):
        raise ValueError("cosmo_base doesn't handle massive neutrinos yet")
    w = cosmo_base.w0
    wa = cosmo_base.wa
    h0 = cosmo_base.h
    if 'sigma_8' in cosmo_base:
        sigma8 = cosmo_base.sigma_8
    else:
        sigma8 = 0.0

    if 'a_s' in cosmo_base:
        A_s = cosmo_base.a_s
    else:
        A_s = 0.0

    n_s = cosmo_base.n_s

    if sigma8 and A_s:
        raise ValueError("Specifying both sigma8 and A_s: pick one")
    elif sigma8:
        params=ccl.Parameters(Omega_c=omega_c,Omega_b=omega_b,Omega_k=omega_k,
                              w0=w,wa=wa,sigma8=sigma8,n_s=n_s,h=h0)
    elif A_s:
        params = ccl.Parameters(Omega_c=omega_c,Omega_b=omega_b,Omega_k=omega_k,
                                w0=w,wa=wa,A_s=A_s,n_s=n_s,h=h0)
    else:
        raise ValueError("Need either sigma 8 or A_s in pyccl.")
    return params

class TwoPointTheoryCalculator(TheoryCalculator):
    def __init__(self, config, metadata):
        super().__init__(config, metadata)
        print("Warning! Making a fake source")
        self.setup_systematics(config['systematics'])
        self.setup_sources(config)
        self.metadata = metadata

    def setup_systematics(self, sys_config):
        self.systematics = {}
        for name, info in sys_config.items():
            sys = Systematic.from_info(info)
            self.systematics[name] = sys
        
        self.output_systematics = {
            name:sys
            for name,sys in self.systematics.items()
            if isinstance(sys,OutputSystematic)
        }

        self.cosmology_systematics = {
            name:sys
            for name,sys in self.systematics.items()
            if isinstance(sys,CosmologySystematic)
        }

        self.source_systematics = {
            name:sys
            for name,sys in self.systematics.items()
            if isinstance(sys,SourceSystematic)
        }


    def setup_sources(self, config):
        info = config['sources']
        used_systematics = set()
        self.sources = []

        for name, source_info in info.items():
            stype = source_info['type']

            source = make_source(name, stype, self.metadata)

            sys_names = source_info.get('systematics', [])
            # check if string or list
            for sys_name in sys_names:
                sys = self.systematics.get(sys_name)
                if sys is None:
                    raise ValueError(f"Systematic with name {sys_name} was specified for source {name} but not defined in parameter file systematics section")
                source.systematics.append(sys)
                used_systematics.add(sys_name)
            self.sources.append(source)

        for sys_name in self.source_systematics.keys():
            if sys_name not in used_systematics:
                raise ValueError(f"Systematic with name {sys_name} was specified in param file but never used")

    def update_systematics(self, parameters):
        for sys in self.systematics:
            sys.update(parameters)

    def make_tracers(self,cosmo):
        for source in self.sources:
            pass

    def run(self, parameters):
        print("Running 2pt theory prediction")
        print(parameters)
        print("Still need to implement TwoPointTheoryCalculator.update_systematics")
        #self.update_systematics(parameters)
        params = convert_cosmobase_to_ccl(parameters)
        cosmo=ccl.Cosmology(params)
                            #transfer_function=dic_par['transfer_function'],
                            #matter_power_spectrum=dic_par['matter_power_spectrum'])
        print(cosmo)
        tracers = self.make_tracers(cosmo)

        for twopoint_pair in something:
            tracer1 = ccl.CLTracer(..., tracer_type=...)
            tracer2 = ccl.CLTracer(...)
            CCL.XXX(cosmo, tracer, tracer2)

        results = TwoPointTheoryResults(...)
        return results

