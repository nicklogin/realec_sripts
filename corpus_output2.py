import os, re

def multiple_strip(s,splitpatterns):
    pass
        
def getallfiles(path):
    all_files = []
    for root, dirs, files in os.walk(path):
        for f in files:
            all_files.append((f,root))
    return all_files
            
def find_errors_indoc(line, err_type, path):
    ##thanks to the author of realec_grammar_exercises.py for this function
    if re.search('^T[0-9]+', line) is not None and 'pos_' not in line:
        try:
            t, span, text_mistake = line.split('\t')
            if ';' in span:
                err = span[:span.find(' ')]
                indexes = span[span.find(' ')+1:]
                indexes = indexes.split(';')
                index1 = indexes[0].split()[0]
                index2 = indexes[-1].split()[1]
            else:
                err, index1, index2 = span.split()
            if err == err_type:
                return (int(index1), int(index2), text_mistake)
            else:
                return None
        except ValueError:
            print("Errors: Something wrong! No notes or a double span")
            print('number of tabs in line: ',line.count('\t'))
            print(path)
            print('"'+line+'"')
            raise Error
    else:
        return None

def dotsplit(txt):
    outp = []
    el = ''
    is_insert = False
    for i in range(len(txt)):
        if txt[i] == '[':
            is_insert = True
        elif txt[i] == ']':
            is_insert = False
        el += txt[i]
        if txt[i] == '.' and is_insert == False:
            outp.append(el)
            el = ''
    if el:
        outp.append(el)
    return outp

def find_corr(mist_ind, ann):
    for line in ann.splitlines():
        if mist_ind in line:
            if line.startswith('#'):
                return line.split('\t')[-1]
    return ''

def get_corpus_output(path, err_tag, output_path):
    
    output = ['text'+'\t'+'sentence']

    for f,fold in getallfiles(path):
        insertions = []
        new_text = ''
        if f.endswith('.txt'):
            with open(os.path.join(fold,f),'r',encoding='utf-8') as t:
                text = t.read()
            ptext = text
            tname = f[:f.rfind('.txt')]
            with open(os.path.join(fold,tname)+'.ann','r',encoding='utf-8') as t:
                ann = t.read()
            for line in ann.splitlines():
                error_mark = find_errors_indoc(line, err_tag, os.path.join(fold, tname))
                if error_mark:
                    ind0, ind1, error = error_mark[0], error_mark[1], error_mark[2]
                    mist_ind = re.search('^T[0-9]+', line).group(0)
                    correction = find_corr(mist_ind, ann)
                    insertion = '[error:'+error+'|correction:'+correction+']'
                    insertions.append((ind0, insertion, ind1))

            if insertions:
                insertions = sorted(insertions, key = lambda m: m[0])
                print(f)
                c = 0
                for i in insertions:
                    print(c,i[0],i[2])
                    new_text += text[c:i[0]]
                    new_text += i[1]
                    c = i[2]
                new_text += text[c:]
##                print(c, len(text))
##                print('ENDTEXT')

            split_text = dotsplit(new_text)
            for i in split_text:
                if '[' in i:
                    rowstring = os.path.join(fold,f)+'\t'+i.replace('\n','').replace('\t',' ')
                    output.append(rowstring)
                        
    with open (output_path,'w',encoding='utf-8') as t:
        for line in output:
            t.write(line+'\n')

if __name__ == '__main__':
    path = input('Введите полный путь к папке: ')
    err_tag = input('Введите тег ошибки: ')
    output_path = input('Введите путь к выходному файлу: ')
    get_corpus_output(path, err_tag, output_path)
    print('Выдача сохранена в ',output_path)
