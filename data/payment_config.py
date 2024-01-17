from environs import Env

env = Env()
env.read_env()

ukassa_token = env('UKASSA_TOKEN')
