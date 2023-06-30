from flask import Flask,render_template,request
from scipy.optimize import linprog
from pulp import *
import numpy as np

app=Flask(__name__)

@app.route('/')
def welcome():
    return render_template('index.html')

#Method for Manufacturing problem

@app.route('/submit',methods=['GET','POST'])
def submit():
    
    #Fetching profits per product, total raw material, raw material per product and total 
    # products to be produced
      
    if request.method=='POST':
         profit1=float(request.form['p1'])
         profit2=float(request.form['p2'])
         profit3=float(request.form['p3'])
         totalRaw=float(request.form['totalRaw'])
         raw1=float(request.form['r1'])
         raw2=float(request.form['r2'])
         raw3=float(request.form['r3'])
         totalProds=float(request.form['totalProds'])
         
         # <------------Problem in the form of linear equations------------>

         # Objective function: max (profit1*X1 + profit2*X2 + profit3*X3); x1,x2,x3 are the products
         # Raw material constraint: raw1*X1 + raw2*X2 + raw3*X3 <= totalRaw
         # Manpower constraint: X1 + X2 + X3 <= totalProds

         obj_fun=[-profit1,-profit2,-profit3]  # Objective function

         # As scipy doesn't accomodate maximization, we will need to use minimization and 
         # hence we have put negative signs  
   
         lhs_eq=[[1,1,1],[raw1,raw2,raw3]]  # lhs of both constraints
         rhs_eq=[totalProds,totalRaw]  # rhs of both constraints 
         
         optimized_solution=linprog(c=obj_fun,A_ub=lhs_eq,b_ub=rhs_eq,method='highs') #Performing optimization
    
         return render_template('result.html',optimization=optimized_solution) # Passing the optimized_solution to result.html

#Method for Transportation problem

@app.route('/submit2',methods=['GET','POST'])
def submit2():

    #Fetching capacities of godowns, demands from customers and transportation costs
    if request.method=='POST':
         supply1=float(request.form['s1'])
         supply2=float(request.form['s2'])
         demand1=float(request.form['d1'])
         demand2=float(request.form['d2'])
         demand3=float(request.form['d3'])
         demand4=float(request.form['d4'])

         costx1=float(request.form['cx1'])
         costx2=float(request.form['cx2'])
         costx3=float(request.form['cx3'])
         costx4=float(request.form['cx4'])

         costy1=float(request.form['cy1'])
         costy2=float(request.form['cy2'])
         costy3=float(request.form['cy3'])
         costy4=float(request.form['cy4'])

         # Opening a file to write the results of this problem 
         f = open("result.txt", "w")

         godowns = ["X", "Y"]  # Two godowns
         supplyCapacity = {"X":supply1,"Y":supply2}  # godowns' supply capacities
         consumerPoints = ["P1", "P2", "P3", "P4"]   # 4 Customer points
         demandFromConsumers={"P1":demand1,"P2":demand2,"P3":demand3,"P4":demand4} #Demand of consumers
        
         transportCosts = makeDict([godowns,consumerPoints],[[costx1,costx2,costx3,costx4],
         [costy1,costy2,costy3,costy4]],0) # A dictionary is made up of all transportation costs 

         lp_problem = LpProblem("A Transportation Problem",LpMinimize) #Defining the Linear Programming problem

         routesToCustomers = [(g,c) for g in godowns for c in consumerPoints]

         lp_variables = LpVariable.dicts("Route from ",(godowns,consumerPoints),0,None,LpInteger) #lp_variables stores the routes

         lp_problem += lpSum([lp_variables[g][c]*transportCosts[g][c] for (g,c) in routesToCustomers]) # sum of transportation cost is calculated 
         
         #Supply constraint
         for g in godowns:
            lp_problem += lpSum([lp_variables[g][c] for c in consumerPoints])<=supplyCapacity[g] #Sum is added to lp_problem considering godowns' supply capacities
         
         #Demand constraint
         for c in consumerPoints: 
            lp_problem += lpSum([lp_variables[g][c] for g in godowns])>=demandFromConsumers[c] #Sum is added to lp_problem considering customer points' demands

         lp_problem.solve() #solving the problem
         
         #Printing the optimal solutions
         for vr in lp_problem.variables(): # By looping through the lp_prob.variables, the units that both godowns should send to the customer points get printed
            print("Units to be sent via ",vr.name, "=", vr.varValue,file=f)
        
         print("Total Transportation Cost will be  = ", value(lp_problem.objective),"\n",file = f) #Total transportation cost gets printed
         print("Status of the solution:", LpStatus[lp_problem.status],"\n",file = f) #Status= optimal/not optimal

         return render_template('result2.html',prob=lp_problem) # Passing the lp_problem to result2.html
         

if __name__=='__main__':
    app.run(debug=True)