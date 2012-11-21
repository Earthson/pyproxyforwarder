from random import choice

fff = open('proxy.conf', 'r')
proxys = [each.split('\n')[0] for each in fff]
fff.close()

def random_proxy():
    return choice(proxys)

def proxy(data):
    return {"remote": random_proxy()}
