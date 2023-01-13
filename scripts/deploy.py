from brownie import Lottery, accounts, config, network
from scripts.helpful_scripts import get_account, get_contract,fund_with_link
import time

def deploy_lottery():
    account = get_account()
    lottery_contract = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract('link_token').address,
        config["networks"][network.show_active()]['fee'],
        config["networks"][network.show_active()]['keyhash'],
        publish_source= config["networks"][network.show_active()].get('verify', False)
    )

    print("Deployed Lottery!")

    return lottery_contract


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_lottery_tx = lottery.startLottery({"from":account})
    start_lottery_tx.wait(1)

    print("lottery started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    entrance_fee = lottery.getEntranceFee() + 1000000
    tx = lottery.enter({"from":account, "value":entrance_fee})
    tx.wait(1)
    print("You entered the lottery")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    #first fund the contract with link
    #Then end lottery
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    end_lottery_tx = lottery.endLottery({"from":account})
    end_lottery_tx.wait(1)
    time.sleep(60)
    print(f'{lottery.recentWinner()} is the new winner.')


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()