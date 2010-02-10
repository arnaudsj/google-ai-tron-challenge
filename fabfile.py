from fabric.api import run, env

def prod():
	env.hosts = ['atlas']
	env.user = 'arnaudsj'
	env.key_filename = '/Users/arnaudsj/.ssh/id_rsa'
	env.workdir = "/Users/arnaudsj/Development/Github/google-ai-tron-challenge-py"

def local():
	env.hosts = ["aura"]
	env.workdir = "/Users/arnaudsj/Development/Github/google-ai-tron-challenge-py"
	
def deploy():
	pull()

def pull():
	run('cd %s; git pull origin master' % env.workdir) #; git submodule update

def test():
	run('cd %s; ./test-mybot-all' % env.workdir )
