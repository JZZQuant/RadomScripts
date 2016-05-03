import re
import numpy as np

expression = '(a & (!b | b)) | (!a & (!b | b))'.replace(' ','')
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
    return Negation(And(Negation(a),Negation(b)))

class atom(object):
    def __init__(self,left,condition):
        self.left=left
        self.condition=condition

def evaluate(expression):
    stack=[]
    remaining=''
    if expression[0]!='(':
        if expression[0]!='!':
            if len(expression)==1:stack.append(atom(duality[expression[0]],-1))
            else:
                stack.append(atom(duality[expression[0]],expression[1]))
                remaining=expression[2:]
        elif expression[1]!='(':
            if len(expression)==1:stack.append(atom(duality[expression[0]],-1))
            else:
                stack.append(atom(Negation(duality[expression[1]]),expression[2]))
                remaining=expression[3:]
        else:
            pos=closure(expression,1)
            if len(expression)==pos:stack.append(atom(Negation(evaluate(expression[2:pos-1]).left),-1))
            else:
                stack.append(atom(Negation(evaluate(expression[2:pos-1]).left),expression[pos]))
            remaining=expression[pos+1:]
    else:
        pos=closure(expression,0)
        if len(expression)==pos:stack.append(atom(Negation(evaluate(expression[1:pos-1]).left),-1))
        else:
            stack.append(atom(evaluate(expression[1:pos-1]).left,expression[pos]))
        remaining=expression[pos+1:]
    if remaining!='':
        stack.append(evaluate(remaining))
    if len(stack)==1: return stack[-1]
    orstack=[]
    i=0
    while i<len(stack):
        if stack[i].condition!='&':
            orstack.append(stack[i])
        else:
            stack[i+1]=atom(And(stack[i].left,stack[i+1].left),stack[i+1].condition)
        i=i+1
    i=0
    while orstack[i].condition!=-1 and i<len(orstack):
        orstack[i+1]=atom(Or(orstack[i].left,orstack[i+1].left),orstack[i+1].condition)
        i=i+1

    return orstack[-1]

print evaluate(expression).left
