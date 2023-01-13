from brownie import (
    accounts, 
    network,
    config, 
    MockV3Aggregator,
    LinkToken,
    VRFCoordinatorMock,
    Contract,
    interface)

FORKED_LOCAL_BLOCKCHAIN = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development', 'ganache-local']

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS 
    or network.show_active() in FORKED_LOCAL_BLOCKCHAIN):
        return accounts[0]
    
    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    'link_token': LinkToken,
}

def get_contract(contract_name):
    '''This function will grab the contract addresses
    from the brownie config if defined otherwise it will
    deploy a mock version of that contract and return a mock contract

        Args:
            contract_name(string) 

        returns:
            brownie.network.contract.ProjectContract: The most
            recently deployed version of this contract
    '''
     
    contract_object = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_object) <= 0:
            deploy_mocks()

        contract = contract_object[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]

        contract = Contract.from_abi(
            contract_object._name, contract_address, 
            contract_object.abi, )

    return contract
 
DECIMALS = 8
INITIAL_VALUE = 2*10**8

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, 
        initial_value, 
        {"from":account})
    link_token = LinkToken.deploy({"from":account})
    VRFCoordinatorMock.deploy(link_token.address, {"from":account})

    print("Deployed! Mocks")


def fund_with_link(contract_address, account=None, link_token=None, amount=1000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from":account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from":account})
    tx.wait(1)
    print("Funded Contract!")
    return tx


