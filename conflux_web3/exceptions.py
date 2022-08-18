class NoWeb3Exception(Exception):
    pass

class DisabledException(Exception):
    pass

def disabled_api(func):
    def inner(*args, **kwargs):
        raise DisabledException("This ethereum api is not valid in Conflux Network."
                               "Check https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc/#migrating-from-ethereum-json-rpc for more information")

    return inner

def use_instead(sub):
    def disabled_api(func):
        def inner(*args, **kwargs):
            if sub is None:
                raise DisabledException("This ethereum api is not valid in Conflux Network."
                                "Check https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc/#migrating-from-ethereum-json-rpc for more information")
            else:
                raise DisabledException("This ethereum api is not valid in Conflux Network."
                                f"use {sub} instead")
        return inner
    return disabled_api
