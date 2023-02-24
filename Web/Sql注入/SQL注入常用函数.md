### substr()
### if()
`IF( expr1 , expr2 , expr3 )`
expr1 的值为 TRUE，则返回值为 expr2   
expr1 的值为FALSE，则返回值为 expr3
### ifnull()
`IFNULL( expr1 , expr2 )`
判断第一个参数expr1是否为NULL：
如果expr1不为空，直接返回expr1；
如果expr1为空，返回第二个参数 expr2
### ascii()
`ASCII ( input_string )`
`ASCII()`函数接受字符表达式并返回字符表达式最左侧字符的ASCII代码值,`input_string`可以是文字字符，字符串表达式或列。 如果`input_string`有多个字符，则该函数返回其最左侧字符的ASCII代码值