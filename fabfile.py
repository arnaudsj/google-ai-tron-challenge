from fabric.api import run, env
from compileall import compile_dir

def prod():
    env.user = 'tronaigc'
    env.key_filename = '/Users/arnaudsj/.ssh/id_rsa_tronaigc'
        
    env.hosts = ['facebook01']
    env.workdir = "/home/tronaigc/google-ai-tron-challenge-py"
    env.distdir = "/tmp/google-entry.zip"
    
    env.testdir = "/home/tronaigc/test-entry"

def local():
    env.hosts = ["aura"]
    env.workdir = "/Users/arnaudsj/Development/Github/google-ai-tron-challenge-py"
    env.distdir = "/Users/arnaudsj/Temp/google-entry.zip"
    env.testdir = "/tmp"

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
    
    run('cd %s/build/python; rm -Rf *' % env.workdir)
    run('cd %s; cp -R engine build/python/' % env.workdir)
    run('cd %s; cp -R example_bots build/python/' % env.workdir)
    run('cd %s; cp -R lib build/python/' % env.workdir)
    run('cd %s; cp -R maps build/python/' % env.workdir)
    run('cd %s; cp -R MyTronBot.py build/python/' % env.workdir)
    
    try:
        run("rm %s" % env.distdir)
    except:
        pass
    run("cd %s/build; zip -r %s `find . -path *git* -prune -o -type f -print`" % (env.workdir, env.distdir))

def testdist():
    package()
    try:
        run("rm -Rf %s/python" % env.testdir)
    except:
        pass
    run("cd %s; unzip %s" % (env.testdir, env.distdir))
    run('cd %s/python; java -jar engine/Tron.jar maps/mytest-board.txt "python MyTronBot.py" "java -jar example_bots/Chaser.jar"' % env.testdir)
    

def test():
    run('cd %s; ./test-mybot-all' % env.workdir )
