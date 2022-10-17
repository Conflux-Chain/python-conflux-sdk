class NoWeb3Exception(Exception):
    pass

class DisabledException(Exception):
    pass

class DeploymentInfoNotFound(Exception):
    pass

class ContractMetadataNotFound(Exception):
    pass

class NameServiceNotSet(Exception):
    pass

class InterfaceNotSupported(Exception):
    pass

class MissingTransactionSender(Exception):
    pass

class UnstableAPI(Exception):
    pass
