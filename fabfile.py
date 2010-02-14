from fabric.api import run, env
from compileall import compile_dir

def prod():
	env.hosts = ['facebook01']
	env.user = 'tronaigc'
	env.key_filename = '/Users/arnaudsj/.ssh/id_rsa_tronaigc'
	env.workdir = "/home/tronaigc/google-ai-tron-challenge-py"

def local():
	env.hosts = ["aura"]
	env.workdir = "/Users/arnaudsj/Development/Github/google-ai-tron-challenge-py"
	env.distdir = "/Users/arnaudsj/Temp/google-entry.zip"

def ping():
    run('uname -a')
		
def deploy():
	pull()

def pull():
	run('cd %s; git pull origin master' % env.workdir) #; git submodule update

def trun():
    run('cd %s; java -jar engine/Tron.jar maps/mytest-board.txt "python MyTronBot.py" "java -jar example_bots/Chaser.jar"' % env.workdir)

def package():
    compile_dir("%s/lib/diesel" % env.workdir, force=1)
    compile_dir("%s/lib/tronlib" % env.workdir, force=1)
    try:
        run("rm %s" % env.distdir)
    except:
        pass
    run("cd %s; zip -0 -r %s `find . -path *git* -prune -o -type f -print | grep -e engine -e lib -e example_bots -e maps -e MyTronBot.py`" % (env.workdir, env.distdir))

def test():
	run('cd %s; ./test-mybot-all' % env.workdir )
