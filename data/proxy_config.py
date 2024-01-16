import socks
from environs import Env

env = Env()
env.read_env('.env')

proxy_username = env.str('proxy_username')
proxy_pass = env.str('proxy_password')
proxy_ip = env.str('proxy_ip')
proxy_port = env.int('proxy_port')

proxy = (socks.SOCKS5, proxy_ip, proxy_port, True, proxy_username, proxy_pass)
