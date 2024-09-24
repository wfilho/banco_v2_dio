import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

# Classe responsável por implementar um iterador customizado para as contas bancárias
class ContasIterador:
    def __init__(self, contas):
        # Armazena a lista de contas a serem iteradas
        self.contas = contas
        self._index = 0  # Inicializa o índice que será usado no processo de iteração

    # Define a função que torna essa classe iterável
    def __iter__(self):
        return self

    # Define o comportamento para cada iteração (próximo item)
    def __next__(self):
        try:
            # Obtém a conta na posição atual do índice
            conta = self.contas[self._index]
            # Retorna as informações da conta formatadas como string
            return f"""\
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
        """
        except IndexError:
            # Lança exceção quando todas as contas já foram iteradas
            raise StopIteration
        finally:
            # Incrementa o índice para a próxima iteração
            self._index += 1


# Classe Cliente representa um cliente bancário
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco  # Armazena o endereço do cliente
        self.contas = []  # Lista de contas associadas ao cliente
        self.indice_conta = 0  # Um índice para controle adicional, se necessário

    # Método que realiza uma transação em uma conta específica
    def realizar_transacao(self, conta, transacao):
        # Verifica se o número de transações permitidas por dia foi excedido
        if len(conta.historico.transacoes_do_dia()) >= 2:
            print("\n@@@ Você excedeu o número de transações permitidas para hoje! @@@")
            return

        # Registra a transação na conta
        transacao.registrar(conta)

    # Método para adicionar uma nova conta à lista de contas do cliente
    def adicionar_conta(self, conta):
        self.contas.append(conta)


# Classe PessoaFisica herda de Cliente e representa uma pessoa física, adicionando os atributos específicos de CPF e data de nascimento
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        # Inicializa a classe Cliente (superclasse) passando o endereço
        super().__init__(endereco)
        # Define os atributos específicos da Pessoa Física
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


# Classe Conta representa uma conta bancária genérica
class Conta:
    def __init__(self, numero, cliente):
        # Define saldo inicial da conta como 0
        self._saldo = 0
        # Atributos número da conta, agência e cliente associado
        self._numero = numero
        self._agencia = "0001"  # Número fixo da agência
        self._cliente = cliente
        # Histórico de transações associado à conta
        self._historico = Historico()

    # Método de classe para criar uma nova conta
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    # Propriedades para acessar os atributos privados da conta de forma controlada
    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    # Método para realizar saque na conta
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo  # Verifica se o saque excede o saldo

        # Caso o saldo seja insuficiente
        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")

        # Caso o valor do saque seja válido
        elif valor > 0:
            self._saldo -= valor  # Subtrai o valor do saldo
            print("\n=== Saque realizado com sucesso! ===")
            return True

        # Caso o valor informado seja inválido (menor ou igual a zero)
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

        return False

    # Método para realizar depósito na conta
    def depositar(self, valor):
        # Verifica se o valor de depósito é válido
        if valor > 0:
            self._saldo += valor  # Adiciona o valor ao saldo
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False

        return True

# Classe ContaCorrente herda de Conta e adiciona atributos específicos de limite de saque e número de saques permitidos
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        # Inicializa a classe Conta (superclasse) passando o número da conta e o cliente
        super().__init__(numero, cliente)
        # Define o limite de saque e o limite de saques por dia
        self._limite = limite
        self._limite_saques = limite_saques

    # Método de classe para criar uma nova conta corrente com limite de saque e número de saques
    @classmethod
    def nova_conta(cls, cliente, numero, limite, limite_saques):
        return cls(numero, cliente, limite, limite_saques)

    # Sobrescreve o método sacar para adicionar a lógica de verificação de limite de saque e número de saques permitidos
    def sacar(self, valor):
        # Conta o número de saques já realizados no histórico
        numero_saques = len(
            [
                transacao
                for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__  # Filtra transações do tipo Saque
            ]
        )

        # Verifica se o valor excede o limite de saque e se o número de saques já realizados excede o permitido
        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")

        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")

        else:
            return super().sacar(valor)  # Se não excedeu limites, realiza o saque normalmente

        return False

    # Método que define a representação da conta corrente como string
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

# Classe Historico armazena as transações de uma conta e gera relatórios
class Historico:
    def __init__(self):
        # Inicializa uma lista vazia para armazenar as transações realizadas
        self._transacoes = []

    # Propriedade para acessar as transações de forma controlada
    @property
    def transacoes(self):
        return self._transacoes

    # Método para adicionar uma transação ao histórico
    def adicionar_transacao(self, transacao):
        # Adiciona um dicionário com os detalhes da transação: tipo, valor, e a data/hora
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,  # Nome da classe da transação (Saque ou Deposito)
                "valor": transacao.valor,  # Valor da transação
                "data": datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),  # Data/hora em UTC
            }
        )

    # Método para gerar um relatório de todas as transações ou de um tipo específico
    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self._transacoes:
            # Filtra por tipo de transação se um tipo for especificado
            if (
                tipo_transacao is None
                or transacao["tipo"].lower() == tipo_transacao.lower()
            ):
                yield transacao  # Retorna as transações uma a uma

    # Método que retorna as transações realizadas no dia atual
    def transacoes_do_dia(self):
        data_atual = datetime.utcnow().date()  # Obtém a data atual (UTC)
        transacoes = []
        for transacao in self._transacoes:
            # Converte a data da transação de string para o tipo datetime e compara com a data atual
            data_transacao = datetime.strptime(
                transacao["data"], "%d-%m-%Y %H:%M:%S"
            ).date()
            if data_atual == data_transacao:
                transacoes.append(transacao)  # Adiciona a transação se for do mesmo dia
        return transacoes

# Classe abstrata Transacao define a interface para diferentes tipos de transações
class Transacao(ABC):
    # Propriedade abstrata que deve ser implementada para retornar o valor da transação
    @property
    @abstractproperty
    def valor(self):
        pass

    # Método abstrato para registrar a transação em uma conta
    @abstractclassmethod
    def registrar(self, conta):
        pass


# Classe Saque que herda de Transacao, representando uma operação de saque
class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor  # Armazena o valor do saque

    # Implementa a propriedade para acessar o valor do saque
    @property
    def valor(self):
        return self._valor

    # Registra o saque na conta, verificando se foi bem-sucedido e adicionando ao histórico
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)  # Adiciona ao histórico se o saque for bem-sucedido

# Classe Deposito que herda de Transacao, representando uma operação de depósito
class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor  # Armazena o valor do depósito

    # Implementa a propriedade para acessar o valor do depósito
    @property
    def valor(self):
        return self._valor

    # Registra o depósito na conta, verificando se foi bem-sucedido e adicionando ao histórico
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)  # Adiciona ao histórico se o depósito for bem-sucedido

# Decorator para registrar e logar transações, exibindo o nome e o momento da transação
def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)  # Executa a função original
        print(f"{datetime.now()}: {func.__name__.upper()}")  # Exibe o log com a data e o nome da função
        return resultado

    return envelope

# Função que exibe o menu do sistema de forma visual
def menu():
    menu = """\n
    ╔═══════════════════════════════════╗
    ║▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ MENU ▒▒▒▒▒▒▒▒▒▒▒▒▒▒║
    ║¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯║
    ║   [d] \tDepositar\t    ║
    ║   [s] \tSacar\t\t    ║
    ║   [e] \tExtrato\t\t    ║
    ║   [nc]\tNova Conta\t    ║
    ║   [lc]\tListar Contas\t    ║
    ║   [nu]\tNovo Usuário\t    ║
    ║   [q] \tSair\t\t    ║
    ╚═══════════════════════════════════╝
    =>"""
    return input(textwrap.dedent(menu))  # Exibe o menu e retorna a opção escolhida

# Função que filtra um cliente na lista de clientes com base no CPF
def filtrar_cliente(cpf, clientes):
    # Encontra o cliente com o CPF correspondente
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None  # Retorna o cliente encontrado ou None

# Função que recupera a primeira conta de um cliente
def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]  # Retorna a primeira conta do cliente (não permite selecionar outras contas)

# Função responsável por realizar um depósito em uma conta, decorada com log_transacao
@log_transacao
def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")  # Solicita o CPF do cliente
    cliente = filtrar_cliente(cpf, clientes)  # Busca o cliente com o CPF fornecido

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return  # Se o cliente não for encontrado, encerra a função

    valor = float(input("Informe o valor do depósito: "))  # Solicita o valor do depósito
    transacao = Deposito(valor)  # Cria uma instância da transação de depósito

    conta = recuperar_conta_cliente(cliente)  # Recupera a conta do cliente
    if not conta:
        return  # Se o cliente não tiver uma conta, encerra a função

    cliente.realizar_transacao(conta, transacao)  # Realiza o depósito na conta do cliente


# Função responsável por realizar um saque, decorada com log_transacao
@log_transacao
def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")  # Solicita o CPF do cliente
    cliente = filtrar_cliente(cpf, clientes)  # Busca o cliente com o CPF fornecido

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return  # Se o cliente não for encontrado, encerra a função

    valor = float(input("Informe o valor do saque: "))  # Solicita o valor do saque
    transacao = Saque(valor)  # Cria uma instância da transação de saque

    conta = recuperar_conta_cliente(cliente)  # Recupera a conta do cliente
    if not conta:
        return  # Se o cliente não tiver uma conta, encerra a função

    cliente.realizar_transacao(conta, transacao)  # Realiza o saque na conta do cliente


# Função para exibir o extrato da conta de um cliente, decorada com log_transacao
@log_transacao
def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")  # Solicita o CPF do cliente
    cliente = filtrar_cliente(cpf, clientes)  # Busca o cliente com o CPF fornecido

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return  # Se o cliente não for encontrado, encerra a função

    conta = recuperar_conta_cliente(cliente)  # Recupera a conta do cliente
    if not conta:
        return  # Se o cliente não tiver uma conta, encerra a função

    print("\n================ EXTRATO ================")
    extrato = ""
    tem_transacao = False
    # Itera sobre as transações da conta e gera o extrato
    for transacao in conta.historico.gerar_relatorio():
        tem_transacao = True
        extrato += f"\n{transacao['data']}\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    # Caso não tenha transações, exibe uma mensagem apropriada
    if not tem_transacao:
        extrato = "Não foram realizadas movimentações"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")  # Exibe o saldo atual da conta
    print("==========================================")


# Função para criar um novo cliente, decorada com log_transacao
@log_transacao
def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")  # Solicita o CPF do novo cliente
    cliente = filtrar_cliente(cpf, clientes)  # Verifica se o cliente já existe

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return  # Se o cliente já existir, encerra a função

    nome = input("Informe o nome completo: ")  # Solicita o nome do cliente
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")  # Solicita a data de nascimento
    endereco = input(
        "Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): "
    )  # Solicita o endereço do cliente

    # Cria uma nova instância da classe PessoaFisica com os dados fornecidos
    cliente = PessoaFisica(
        nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco
    )

    clientes.append(cliente)  # Adiciona o cliente à lista de clientes

    print("\n=== Cliente criado com sucesso! ===")


# Função para criar uma nova conta para um cliente, decorada com log_transacao
@log_transacao
def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")  # Solicita o CPF do cliente
    cliente = filtrar_cliente(cpf, clientes)  # Busca o cliente com o CPF fornecido

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return  # Se o cliente não for encontrado, encerra a função

    # Cria uma nova conta corrente associada ao cliente, com limite padrão
    conta = ContaCorrente.nova_conta(
        cliente=cliente, numero=numero_conta, limite=500, limite_saques=50
    )
    contas.append(conta)  # Adiciona a conta à lista de contas
    cliente.contas.append(conta)  # Associa a conta ao cliente

    print("\n=== Conta criada com sucesso! ===")


# Função para listar todas as contas cadastradas
def listar_contas(contas):
    # Utiliza o iterador customizado para percorrer e exibir as contas
    for conta in ContasIterador(contas):
        print("=" * 100)
        print(textwrap.dedent(str(conta)))  # Exibe as informações formatadas da conta


# Função principal que gerencia o fluxo do sistema bancário
def main():
    clientes = []  # Inicializa a lista de clientes
    contas = []  # Inicializa a lista de contas

    # Loop principal que exibe o menu e processa as opções escolhidas
    while True:
        opcao = menu()  # Exibe o menu e captura a opção do usuário

        if opcao == "d":
            depositar(clientes)  # Executa a função de depósito

        elif opcao == "s":
            sacar(clientes)  # Executa a função de saque

        elif opcao == "e":
            exibir_extrato(clientes)  # Executa a função para exibir extrato

        elif opcao == "nu":
            criar_cliente(clientes)  # Executa a função para criar novo cliente

        elif opcao == "nc":
            numero_conta = len(contas) + 1  # Define o número da nova conta com base no total de contas
            criar_conta(numero_conta, clientes, contas)  # Executa a função para criar nova conta

        elif opcao == "lc":
            listar_contas(contas)  # Executa a função para listar todas as contas

        elif opcao == "q":
            break  # Encerra o loop e finaliza o programa

        else:
            print(
                "\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@"
            )


# Inicia a execução do programa
main()
