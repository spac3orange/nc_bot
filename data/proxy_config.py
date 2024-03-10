import socks
from environs import Env

env = Env()
env.read_env('.env')

proxy_username = env.str('proxy_username')
proxy_pass = env.str('proxy_password')
proxy_ip = env.str('proxy_ip')
proxy_port = env.int('proxy_port')

gpt_proxy_username = env.str('gpt_proxy_username')
gpt_proxy_pass = env.str('gpt_proxy_password')
gpt_proxy_ip = env.str('gpt_proxy_ip')
gpt_proxy_port = env.int('gpt_proxy_port')

proxy = (socks.SOCKS5, proxy_ip, proxy_port, True, proxy_username, proxy_pass)
