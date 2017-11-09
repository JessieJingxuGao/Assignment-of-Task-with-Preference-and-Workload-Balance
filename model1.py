from gurobipy import *
import numpy as np

# create a new model
myModel = Model( "Final" )

#-------.dat-----------
# there are 71 papers and 21 referees
noPapers = 71
noReferees = 21

#parameter: balance ratio
r=2
yes=3
maybe=2
no=1

# initialize the utility data
u=[]
import csv
with open('paper_preferences.csv', 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        u_temp=[]
        for j in row:
            utility=0
            if j =="yes":
                utility=yes
            elif j=="maybe":
                utility=maybe
            elif j=="no":
                utility=no
            elif j=="conflict":
                utility=0
            else:
                utility="attribute name"
            u_temp.append(utility)
        u.append(u_temp)
# print(u[71])
# print(u[1][1])
# print(u)


#-------.mod-----------
# create decision variables and store them in the array myVars
myVars =[]
for i in range (noPapers+1 ) :  #(1,oPapers+1 ) bug here??
    myVars_temp=[]
    for j in range (noReferees+1):
        myVars_temp.append(1)
        # print("(",i,j,")")
    myVars.append(myVars_temp)
# myVars = [ [ 1 for i in range (1, noPapers+1 ) ] for j in range (1,noReferees+1) ] #### bug here??



for i in range(1,noPapers +1):
    for j in range (1,noReferees+1):
        curVar = myModel.addVar( vtype = GRB.BINARY , name= "x"+str(i)+"_"+str(j)) # x171 hard to distringuish
        # print("(",i,j,")")
        myVars[ i ][ j ] = curVar
# integrate decision variables into the model
myModel.update()


# create a linear expression for the objective
objExpr = LinExpr()
for i in range(1, noPapers +1):
    for j in range (1,noReferees +1):
        curVar = myVars[ i ][ j ]
        objExpr += u[ i ][ j ] * curVar
        # print(objExpr)
myModel.setObjective( objExpr , GRB.MAXIMIZE )


# create constraints so that each paper is assigned to 3 referr
for i in range( 1, noPapers+1 ):
    constExpr = LinExpr()
    for j in range( 1, noReferees+1 ):
        curVar = myVars[ i ][ j ]
        constExpr += 1 * curVar
    myModel.addConstr( lhs = constExpr , sense = GRB.EQUAL , rhs = 3, \
                       name = "3_reviewers" + "referee"+str( i ) )

# create constraints to eliminate "conflict"
for i in range( 1, noPapers+1 ):
    constExpr = LinExpr()
    for j in range( 1, noReferees+1 ):
        curVar = myVars[ i ][ j ]
        constExpr = 1 * curVar
        myModel.addConstr( lhs = constExpr , sense = GRB.LESS_EQUAL , rhs = u[i][j], \
                       name = "no_conflict" + "paper"+str( i )+ "referee"+str( j ))


# create constraints for load balance
load=[]
load.append("this is noReferee_0, no existence")
for j in range( 1, noReferees+1):
    constExpr = LinExpr()
    for i in range( 1, noPapers+1 ):
        curVar = myVars[ i ][ j ]
        constExpr += 1 * curVar
    load.append(constExpr)
# for j in range( 1, noReferees+1):
#     print(j)
#     print(load[j])
# print(load)
#
for m in range( 1,noReferees+1):
    for n in range(1,noReferees+1):
        myModel.addConstr( lhs = load[m] , sense = GRB.LESS_EQUAL , rhs = load[n]*r , \
                       name = "balance" + str(m)+"<="+str(n) +"*r")
        # print("balance:" + str(m)+"<="+str(n) +"*r")



# integrate objective and constraints into the model
myModel.update()


# write the model in a file to make sure it is constructed correctly
myModel.write( filename = "final_model.lp" )



# optimize the model
myModel.optimize()
# print( "\nOptimal Solution:" )
allVars = myModel.getVars()



# output result in table form
assignment=[]
for curVar in allVars:
#     print ( curVar.varName + " " + str( curVar.x ) )
    if  curVar.x==1:
        assignment.append(curVar.varName.strip('x').split('_'))

import numpy as np
result=np.zeros((noPapers+1,noReferees+1))
for i in range(1,noPapers+1):
    for j in range(1,noReferees+1):
        if [str(i),str(j)] in assignment:
            result[i,j]=1

# print(result[1])


# model performance
noYes=0
noNo=0
noMaybe=0
noConflict=0
for i in range(1,noPapers+1):
    for j in range(1,noReferees+1):
        if result[i,j]==1:
            if u[i][j]==yes:
                noYes+=1
            elif u[i][j]==maybe:
                noMaybe+=1
            elif u[i][j]==no:
                noNo+=1
            elif u[i][j]==0:
                noConflict+=1

print("-----assignment-----")
print(assignment)

for j in range(1,noReferees+1):
    temp=[]
    for i in range(1,noPapers+1):
        if result[i,j]==1:
            temp.append(i)
    print("Referee", j, "is assigned to paper" ,temp)

print("-----noYes,noMaybe,noNo,noConflict-----")
print(noYes,noMaybe,noNo,noConflict)
if (noYes+noMaybe+noNo+noConflict)!=(3*71):
    print("sum error")

# print optimal objective and optimal solution
print( "-----Optimal Objective-----" )
print( str( myModel.ObjVal ) )


# excel writer
import pandas as pd
df_result = pd.DataFrame(result)
writer = pd.ExcelWriter("solution_model1_171201.xlsx", engine='xlsxwriter')
df_result.to_excel(writer,sheet_name='sheet1')
writer.save()





