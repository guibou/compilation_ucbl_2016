import glob
import sys
import os
import subprocess

antlrpath = '/home/guillaume/teaching/compil_ucbl_2016/lib/antlr-4.5.3-complete.jar'


def antl_command(path):
    currentDir = os.getcwd()

    os.chdir(os.path.dirname(path))
    cmd = ["java", "-jar", antlrpath, "Mu.g4", "-Dlanguage=Python2", "-visitor", "-no-listener"]

    # print(' '.join(cmd))
    subprocess.check_call(cmd)

    os.chdir(currentDir)

def test_command(path, flog):
    try:
        (stdout, stderr) = subprocess.Popen("FAST=10 PYTHONPATH='%s' python2 test.py -q" % path,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            shell=True).communicate()

        flog.write(stdout)
        flog.write(stderr)

        errors = list(filter(lambda x: 'Error:' in x, stderr.decode('utf8').split('\n')))
        errors.sort()
        for i in errors:
            if not i.startswith('AssertionError'):
                print('\t', i)

        return True
    except subprocess.CalledProcessError:
        return False

correction_path = os.path.realpath(sys.argv[1])

g4s = glob.glob(os.path.join(correction_path, "**/Mu.g4"), recursive=True)

print(len(g4s))

generateG4 = False

with open("allResult.csv", "w") as fResult, open('logs', 'wb') as flog:
    headerOk = False
    for g4 in g4s:
        dir = os.path.dirname(g4)

        name = '/'.join(dir[len(correction_path) + 1:].split('/')[:2])
        print(name)

        if  generateG4:
            antl_command(g4)
        else:
            worked = test_command(dir, flog)

            if worked:
                # copy partial result to the big file
                with open('result.csv', 'r') as f:
                    line1, line2, _ = f.read().split('\n')

                if not headerOk:
                    fResult.write("Nom," + line1 + '\n')

                    headerOk = True

                fResult.write(name + ',' + line2 + '\n')
            else:
                fResult.write(name + ', MISERABLE FAILURE\n')
