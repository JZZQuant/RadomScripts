import re
import numpy as np

expression = '(a & (!b | b)) | (!a & (!b | b))'.strip()
operands=len(set(re.findall("[a-zA-Z]+", expression)))

point_topology=list(set(re.findall("[a-zA-Z]+", expression)))
topology = range(1,2**(operands)+1)
dualspace=[]

for i in range(0,operands):
    dualspace.append(np.array([x%2 for x in topology]))
    topology=[x/2 for x in topology]

duality=dict(zip(point_topology,dualspace))

print duality

def closure(expression,pos):
    expression=expression[pos:]
    ones=[int(char=='(') for char in expression]
    minus=[int(char==')') for char in expression]
    basearray=np.subtract(ones,minus)
    return np.where(np.cumsum(basearray)==0)[0][0] + 1 +pos

def Negation(a,operandmap):
    if type(a)==type(''):
        a=operandmap[a]
    return 1-a

def And(a,b,operandmap):
    if a==1: return b
    if b==1: return a
    if a==0 or b==0: return 0
    if type(a)==type(''):
        a=operandmap[a]
    if type(b)==type(''):
        b=operandmap[b]
    return a*b

def Or(a,b,operandmap):
    if type(a)==type(''):
        a=operandmap[a]
    if type(b)==type(''):
        b=operandmap[b]
    if a==0: return b
    if b==0: return a
    if a==1 or b==1: return 1
    return Negation(And(Negation(a),Negation(b)))

class graph(object):
    def __init__(self,expression,operandmap):
        self.operandmap=operandmap
        self.left=None
        self.right=None
        self.isNegation=False
        self.data=None
        self.buildgraph(expression)

    def buildgraph(self,expression):
        operandmap=self.operandmap
        if len(expression)<3:
            self.data=expression
            self.left=1
            self.right=0
            return 0
        if (expression[0]!='!' and expression[0]!='(') or (expression[0]=='!' and expression[1]!='('):
            if expression.index('&')>expression.index('|'):
                breaker=expression.index('|')
                self.data=graph(expression[0:breaker],operandmap)
                self.right=graph(expression[breaker:],operandmap)
            else:
                print expression
                breaker=expression.index('&')
                self.data=graph(expression[0:breaker],operandmap)
                self.left=graph(expression[breaker:],operandmap)
        if expression[0]=='(':
            #get corresponding close if its equal to len rebuild internal graph or else bracket break
            closing=closure(expression,0)
            if closing==len(expression):
                self.buildgraph(expression[1:-1])
            else:
                if expression[closing]=='|':
                    self.data=graph(expression[0:closing],operandmap)
                    self.right=graph(expression[closing:],operandmap)
                else:
                    self.data=graph(expression[0:closing],operandmap)
                    self.left=graph(expression[closing:],operandmap)
        if expression[0]=='!' and expression[1]=='(':
            #get corresponding close if its equal to len rebuild internal graph with a negation
            closing=closure(expression,1)
            if closing==len(expression):
                buildgraph(expression[2:-1])
                self.isNegation=True
            else:
                if expression[closing]=='|':
                    self.data=graph(expression[0:closing],operandmap)
                    self.right=graph(expression[closing:],operandmap)
                else:
                    self.data=graph(expression[0:closing],operandmap)
                    self.left=graph(expression[closing:],operandmap)

    def evaluate(self):
        x=Or(And(self.data,self.left.data,self.operandmap),self.right,self.operandmap)
        if self.isNegation:
            return Negation(x,self.operandmap)
        else:
            return x

g=graph(expression,duality)
g.evaluate()
print g.data()
