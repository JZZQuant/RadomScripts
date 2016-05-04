import re
import numpy as np

expression = '(a & (!b | b)) | (!a & (!b | b))'.replace(' ','')
#expression = '(!b | b)'.replace(' ','')
#expression = '!(b & !b)'.replace(' ','')
operands=len(set(re.findall("[a-zA-Z]+", expression)))

point_topology=list(set(re.findall("[a-zA-Z]+", expression)))
topology = range(1,2**(operands)+1)
dualspace=[]

for i in range(0,operands):
    dualspace.append(np.array([x%2 for x in topology]))
    topology=[x/2 for x in topology]

duality=dict(zip(point_topology,dualspace))
duality["0"]=np.array([0]*(2**(operands)))
duality["1"]=1-duality["0"]
print duality

def closure(expression,pos):
    expression=expression[pos:]
    ones=[int(char=='(') for char in expression]
    minus=[int(char==')') for char in expression]
    basearray=np.subtract(ones,minus)
    return np.where(np.cumsum(basearray)==0)[0][0] + 1 +pos

def Negation(a):
    return 1-a

def And(a,b):
    return a*b

def Or(a,b):
    return 1-((2**(a+b))%2)

class atom(object):
    def __init__(self,left,condition,negate=0):
        self.element=left
        self.condition=condition
        if negate==1 :self.element=Negation(left)
        print "added to stack "+ str(self.element ) + "with condition "+ str(self.condition)

#lazy stack
def stackCollapse(stack,symbol,fun,isLastinEngine):
    orstack=[]
    i=0
    while i+1<len(stack):
        if stack[i].condition!=symbol:orstack.append(stack[i])
        else:stack[i+1]=atom(fun(stack[i].element,stack[i+1].element),stack[i+1].condition)
        i=i+1
    if not isLastinEngine:
        orstack.append(stack[-1])
        return orstack
    else: return stack

def evaluate(expression):
    fullstack=[]
    if len(expression)<3:fullstack.append(atom(duality[expression[0]],-1,len(expression)-1))
    else:
        left=expression.find("(")
        if left not in [0,1]:
            negate=int(expression[0]=='!')
            fullstack.append(atom(duality[expression[0+negate]],expression[1+negate],negate))
            fullstack.append(evaluate(expression[2+negate:]))
        else:
            pos=closure(expression,left)
            if len(expression)==pos:fullstack.append(atom(evaluate(expression[1+left:pos-1]).element,-1,left))
            else:
                fullstack.append(atom(evaluate(expression[1+left:pos-1]).element,expression[pos],left))
                fullstack.append(evaluate(expression[pos+1:]))

    orstack=stackCollapse(fullstack,'&',And,False)
    return stackCollapse(orstack,'|',Or,True)[-1]

print evaluate(expression).element
