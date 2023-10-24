from QlikScriptParser import QlikScriptParser

script = '''\n
// Вот это да
load 
    dgd,
    dfgdfgd, 
    fgdfgdfg
FROM [lib://dgdfg];
/* dfggfgdfgdfg 
df
fdf
*/
Load * FROM connect;
Set dfdsf = 'dfsdfsdf';
SET dfdf = $(dfdsf);
'''
p = QlikScriptParser(script)

