# SQL Injection — calibration examples

## VULNERABLE — string interpolation into SQL
    cursor.execute("SELECT * FROM users WHERE username = '%s'" % username)
The user input is concatenated directly into the query → SQL injection.

## SAFE — parameterized query
    cursor.execute("SELECT * FROM users WHERE username = %s", [username])
Uses parameter binding → NOT SQL injection. Do not flag.

## NOT SQLi — different vulnerability class (command injection)
    cmd = "ping -c 5 %s" % ip; subprocess.getoutput(cmd)
This is command injection, not SQL injection — do not report it under SQLi.

## NOT A FINDING — form field definition
    ssn = forms.CharField(max_length=11, required=False)
A form field declaration is not a SQL injection. Do not flag.
