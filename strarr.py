from types import ListType

__all__ = ['str2arr', 'arr2str']

caps = { '(': ')', '{': '}', '[': ']' }

def _str2num(str):
    a = str.strip().split(';')
    a = map(float, str.split(';'))
    return a

def _str2arr(cap, str):
    if str[0] in caps.keys():
        subcap = str[0]
        arr = []
        while len(str):
            str = str[1:]
            (str, sub) = _str2arr(subcap, str)
            arr.append(sub)
            if str[0] == caps[subcap] or str[0] == caps[cap]:
                str = str[1:]
                break
        return (str, arr)
    else:
        pos = str.find(caps[cap])
        nums = _str2num(str[:pos])
        str = str[(pos + 1):]
        
        return (str, nums)

def str2arr(str):
   
    (str, arr) = _str2arr(str[0], str[1:])
 
    return arr

def _arr2str(arr):
    ret = ''
    if isinstance(arr[0], ListType):
        ret = '('
        for elem in arr:
            ret += _arr2str(elem)
        ret += ')'
    else:
        ret = '(' + ';'.join(map(str, arr)) + ')'
    return ret
        
def arr2str(arr):
    ret = '('
    for elem in arr:
        ret += _arr2str(elem)
    ret += ')'
    return ret

if __name__ == "__main__":
    test = '((1.2;3.4)(1.3;3.5;6.7)((1.2;3.4)(1.3;3.5;6.7)))'
    print test
    print str2arr(test)
    print arr2str(str2arr(test))
    test = '{(1.2;3.4)(1.3;3.5;6.7)((1.2;3.4)(1.3;3.5;6.7))}'
    print test
    print str2arr(test)
    print arr2str(str2arr(test))
    test = '[(1.2;3.4)(1.3;3.5;6.7)((1.2;3.4)(1.3;3.5;6.7))]'
    print test
    print str2arr(test)
    print arr2str(str2arr(test))