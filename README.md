This code is not interesing if you are not working with me on that course ;)


See the file `test.py` for all tests.

# Tips

You can add the environment variable `FAST` to generate faster (but less exhaustives) tests.

- no `FAST` : exhaustives tests, can be slow (2 minutes on my computer)
- `FAST=1` : one case per testcase, quick (<1s), but not exhaustive
- `FAST=10` : quick (2s), only 10 cases per testcase, but usually enough

# Usage


The `PYTHONPATH` environment variable must be set to the path of the `MyMuCodeGenVisitor.py` file.

Run and get the assembly for a mu file, for example, `exemple.mu` :

```
a = 0;
n = 3;
while(a < n)
{
   a = a + 1;
}
```

```shell
$ PYTHONPATH=../MIF08_TP4/StudFilesTP4 python2 test_utils.py exemple.mu 
assign statement, rightexpression is:
(expr (atom 0))
assign statement, rightexpression is:
(expr (atom 3))
assign statement, rightexpression is:
(expr (expr (atom a)) + (expr (atom 1)))
--variables to register map--
a-->temp_2
n-->temp_4
And(dr='temp_1', sr1='temp_1', sr2orimm7=0)
Add(dr='temp_1', sr1='temp_1', sr2orimm7=0)
And(dr='temp_2', sr1='temp_2', sr2orimm7=0)
Add(dr='temp_2', sr1='temp_2', sr2orimm7='temp_1')
And(dr='temp_3', sr1='temp_3', sr2orimm7=0)
Add(dr='temp_3', sr1='temp_3', sr2orimm7=3)
And(dr='temp_4', sr1='temp_4', sr2orimm7=0)
Add(dr='temp_4', sr1='temp_4', sr2orimm7='temp_3')
Label(label='l_while_begin_1')
And(dr='temp_5', sr1='temp_5', sr2orimm7=0)
Not(dr='temp_5', sr1='temp_4')
Add(dr='temp_5', sr1='temp_5', sr2orimm7=1)
Add(dr='temp_6', sr1='temp_2', sr2orimm7='temp_5')
Br(label='l_cond_neg_2', s='n')
And(dr='temp_7', sr1='temp_7', sr2orimm7=0)
Br(label='l_cond_end_2', s='')
Label(label='l_cond_neg_2')
And(dr='temp_7', sr1='temp_7', sr2orimm7=0)
Add(dr='temp_7', sr1='temp_7', sr2orimm7=1)
Label(label='l_cond_end_2')
Br(label='l_while_end_1', s='z')
And(dr='temp_8', sr1='temp_8', sr2orimm7=0)
Add(dr='temp_8', sr1='temp_8', sr2orimm7=1)
Add(dr='temp_9', sr1='temp_2', sr2orimm7='temp_8')
And(dr='temp_2', sr1='temp_2', sr2orimm7=0)
Add(dr='temp_2', sr1='temp_2', sr2orimm7='temp_9')
Br(label='l_while_begin_1', s='')
Label(label='l_while_end_1')
{'temp_9': 3, 'temp_8': 1, 'temp_5': -3, 'temp_4': 3, 'temp_7': 0, 'temp_6': 0, 'temp_1': 0, 'temp_3':

```

Runs the test for one student :

```shell
$ FAST=10 PYTHONPATH=../MIF08_TP4/StudFilesTP4 python2 -m unittest test
..........................
----------------------------------------------------------------------
Ran 26 tests in 11.285s

OK
```
