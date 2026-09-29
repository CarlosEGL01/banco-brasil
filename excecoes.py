class BancoError(Exception):
    pass

class SaldoInsuficienteError(BancoError):
    pass

class ContaEncerradaError(BancoError):
    pass

class ContaNaoEncerradaError(BancoError):
    pass

class ClienteNaoEncontradoError(BancoError):
    pass

class ContaNaoEncontradaError(BancoError):
    pass
class MesmaContaError(BancoError):
    pass
class CreditoInsuficienteError(BancoError):
    pass