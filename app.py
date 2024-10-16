import numpy as np
from scipy.optimize import linprog
import streamlit as st

# Function to get transportation cost matrix
def get_cost_matrix(facilities, warehouses):
    cost_matrix = []
    for facility in facilities.keys():
        cost_input = st.text_input(
            f"Enter the transportation costs from {facility} to each warehouse separated by commas (in order: {', '.join(warehouses.keys())})",
            key=f"cost_{facility}"  # Using unique keys to store values in session_state
        )
        if cost_input:
            cost_input = [float(x.strip()) for x in cost_input.split(',')]
            if len(cost_input) != len(warehouses):
                st.error(f"Error: You must enter {len(warehouses)} cost values for {facility}.")
                return None
            cost_matrix.append(cost_input)
    return np.array(cost_matrix)

# Function to solve the transportation problem
def transportation_problem_solver():
    st.title("Transportation Problem Solver")
    
    # Inputs for facilities and warehouses
    num_facilities = st.number_input("Enter the number of facilities:", min_value=1, step=1, key="num_facilities")
    facilities = {}
    
    for i in range(1, num_facilities + 1):
        facility_name = st.text_input(f"Enter Facility {i} name:", key=f"facility_{i}_name")
        facility_capacity = st.number_input(f"Enter Facility {i} capacity:", min_value=0.0, step=1.0, key=f"facility_{i}_capacity")
        facilities[facility_name] = facility_capacity
    
    num_warehouses = st.number_input("Enter the number of warehouses:", min_value=1, step=1, key="num_warehouses")
    warehouses = {}

    for i in range(1, num_warehouses + 1):
        warehouse_name = st.text_input(f"Enter Warehouse {i} name:", key=f"warehouse_{i}_name")
        warehouse_demand = st.number_input(f"Enter Warehouse {i} demand:", min_value=0.0, step=1.0, key=f"warehouse_{i}_demand")
        warehouses[warehouse_name] = warehouse_demand
    
    # Submit button to finalize inputs
    if st.button("Submit"):
        # Fetch the transportation cost matrix
        cost_matrix = get_cost_matrix(facilities, warehouses)
        
        if cost_matrix is None:
            return
        
        # Supply and demand values
        supply = list(facilities.values())
        demand = list(warehouses.values())
        
        # Check if the supply matches the demand
        if sum(supply) != sum(demand):
            st.error(f"Error: Total supply {sum(supply)} does not match total demand {sum(demand)}.")
            return
        
        # Create the coefficient matrix for linear programming
        num_facilities = len(facilities)
        num_warehouses = len(warehouses)
        
        # Objective function (minimize cost)
        c = cost_matrix.flatten()
        
        # Constraints
        A_eq = []
        for i in range(num_facilities):
            supply_constraint = [0] * num_facilities * num_warehouses
            for j in range(num_warehouses):
                supply_constraint[i * num_warehouses + j] = 1
            A_eq.append(supply_constraint)
        
        for j in range(num_warehouses):
            demand_constraint = [0] * num_facilities * num_warehouses
            for i in range(num_facilities):
                demand_constraint[i * num_warehouses + j] = 1
            A_eq.append(demand_constraint)
        
        b_eq = supply + demand
        
        # Bounds for each variable (non-negative shipments)
        x_bounds = [(0, None) for _ in range(num_facilities * num_warehouses)]
        
        # Solve the problem
        result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=x_bounds, method='highs')
        
        if result.success:
            st.success("Optimal solution found!")
            solution_matrix = result.x.reshape((num_facilities, num_warehouses))
            st.write("Optimal Transport Plan:")
            st.write(solution_matrix)
            st.write(f"Total Minimum Cost: {result.fun}")
        else:
            st.error(f"Error solving the transportation problem: {result.message}")

if __name__ == "__main__":
    transportation_problem_solver()
