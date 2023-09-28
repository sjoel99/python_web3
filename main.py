from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

# web3.py instanc
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
conn = w3.is_connected()
block = w3.eth.get_block('latest')

acct1: LocalAccount = Account.from_key('0xe1061623038fd07cd373dfa5b02e0df1a4a07ec02dc59784f88ea64b9bfc17e2')
acct2: LocalAccount = Account.from_key('0xeb890d2b8730f8264928b20ed7c15dd602790982d3a7422feefd70e22476ec76')

w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct1))

print(f"Your hot wallet address is {acct1.address}")

# # when using one of its generated test accounts,
# # eth-tester signs the tx (under the hood) before sending:
# # print(w3.eth.ge)
# tx_hash = w3.eth.send_transaction({
#     "from": acct1.address,
#     "to": acct2.address,
#     "value": w3.to_wei(10, 'ether'),
#     "nonce": w3.eth.get_transaction_count(acct1.address)
# })
# tx = w3.eth.get_transaction(tx_hash)
# print(tx)

# """
# 1- Entrar Bolao
# 2- Criar Bolao
# 3- Adicionar Participante
# 4- Visualizar Bolao
# 5- Visualizar Participantes
# 6- Escolher ganhador
# """

from solcx import compile_source
from solcx import install_solc
install_solc(version='latest')

# Solidity source code
compiled_sol = compile_source("""
// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.8.18 <0.9.0;

/*
Contrato Bolao
Criado por Henrique Poyatos para a demonstração de um contrato inteligente
*/
contract Bolao {
    // Atributo jogadores guarda múltiplos endereços das carteiras dos jogadores
    address payable[] private jogadores;
    // Atributo dono guarda a carteira do dono do bolão
    address private dono;

    // Estabelece o endereço da carteira do deploy como dono do contrato
    constructor() {
        dono = msg.sender;
    }

    // Função "pagável" a ser usada pelo apostador
    function apostar() public payable {
        //Assim que uma aposta for feita, guarde o endereço de carteira do apostador
        jogadores.push(payable(msg.sender));
    }

    // Função getJogadores() retorna os endereços de carteiras dos apostadores
    function getJogadores() public view returns (address payable[] memory) {
        return jogadores;
    }

    // Funcão retorna o valor total em custódia no momento
    function getSaldo() public view returns (uint) {
        return (payable(address(this))).balance;
    }

    // O modificador somenteDono, quando aplicado, restringe o uso da função 
    modifier somenteDono() {
        require(msg.sender == dono);
        _;
    }

    function random() private view returns (uint) {
        return uint(keccak256(abi.encodePacked(block.prevrandao, block.timestamp, jogadores)));
    }

    // escolherVencedor sorteia um apostador e transfere todo o valor em custódia para ele
    function escolherVencedor() public somenteDono {
        uint index = random() % jogadores.length;
        jogadores[index].transfer(address(this).balance);
        jogadores = new address payable[](0);
    }
}
                              
                              solc --bin -o /tmp/solcoutput dapp-bin=/usr/local/lib/dapp-bin contract.sol
""")
# retrieve the contract interface
contract_id, contract_interface = compiled_sol.popitem()

# get bytecode / bin
bytecode = contract_interface['bin']

# get abi
abi = contract_interface['abi']

# set pre-funded account as sender
w3.eth.default_account = acct1.address

Bolao = w3.eth.contract(abi=abi, bytecode=bytecode)

# Submit the transaction that deploys the contract
tx_hash = Bolao.constructor().transact()
print('tx_hash', tx_hash)
# # Wait for the transaction to be mined, and get the transaction receipt
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# print('tx_receipt', tx_receipt)

# bolao = w3.eth.contract(
#     address=tx_receipt.contractAddress,
#     abi=abi
# )

# bolao.functions.greet().call()

# tx_hash = bolao.functions.setGreeting('Nihao').transact()
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# bolao.functions.greet().call()
