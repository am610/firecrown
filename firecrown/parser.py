import importlib
import yaml
import jinja2
import collections

def parse(source, memory_data=None):
    """Parse a configuration file.

    Parameters
    ----------
    source : str
        The config file to parse. Should be YAML formatted.
        if source has 'read' attribute, it is used to fetch data,
        otherwise it is interpreted as a filename
    memory_data : (optional). Dictionary (can be of dictionaries) 
                  used to update parsed config file after reading it.

    Returns
    -------
    config : dict
        The raw config file as a dictionary.
    data : dict
        A dictionary containg each analyses key replaced with its
        corresponding data and function to compute the log-likelihood.
    """

    if  not hasattr(source,"read"):
        source = open (source,'r')
    config_str = jinja2.Template(source.read()).render()
    config = yaml.load(config_str, Loader=yaml.Loader)
    data = yaml.load(config_str, Loader=yaml.Loader)

    ## if stuff came already parsed, bring it in
    if memory_data is not None:
        ## recursive update of potentially nested dictionaries
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, collections.abc.Mapping):
                    d[k] = update_dict(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        data = update_dict (data, memory_data)
        config = update_dict (config, memory_data)
        
    params = {}
    for p, val in data['parameters'].items():
        if isinstance(val, list) and not isinstance(val, str):
            params[p] = val[1]
        else:
            params[p] = val
    data['parameters'] = params

    analyses = list(
        set(list(data.keys())) -
        set(['parameters', 'cosmosis', 'emcee']))
    for analysis in analyses:
        new_keys = {}

        try:
            mod = importlib.import_module(data[analysis]['module'])
        except Exception:
            print("Module '%s' for analysis '%s' cannot be imported!" % (
                data[analysis]['module'], analysis))
            raise

        new_keys = {}
        if hasattr(mod, 'parse_config'):
            new_keys['data'] = getattr(mod, 'parse_config')(data[analysis])
            new_keys['eval'] = getattr(mod, 'compute_loglike')
            new_keys['write'] = getattr(mod, 'write_stats')
        else:
            raise ValueError("Analsis '%s' could not be parsed!" % (analysis))

        data[analysis] = new_keys

    return config, data
