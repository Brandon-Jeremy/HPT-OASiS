# Made for Exploration vs Exploitation figure.

import numpy as np
import matplotlib.pyplot as plt

def ackley_function(x, y):
    return -20 * np.exp(-0.2 * np.sqrt(0.5 * (x**2 + y**2))) - np.exp(0.5 * (np.cos(2 * np.pi * x) + np.cos(2 * np.pi * y))) + np.e + 20

num_particles = 30
num_iterations = 100
w = 0.5
c1 = 1.5
c2 = 1.5

positions = np.random.uniform(low=-5, high=5, size=(num_particles, 2))
velocities = np.random.uniform(low=-1, high=1, size=(num_particles, 2))
personal_best_positions = positions.copy()
personal_best_values = np.zeros(num_particles)
global_best_position = np.zeros(2)
global_best_value = np.inf

x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)
Z = ackley_function(X, Y)

for i in range(num_iterations):
    for j in range(num_particles):
        x, y = positions[j]
        fitness = ackley_function(x, y)
        
        if fitness < personal_best_values[j]:
            personal_best_values[j] = fitness
            personal_best_positions[j] = positions[j].copy()
        
        if fitness < global_best_value:
            global_best_value = fitness
            global_best_position = positions[j].copy()
    
        velocities[j] = w * velocities[j] + c1 * np.random.rand() * (personal_best_positions[j] - positions[j]) + c2 * np.random.rand() * (global_best_position - positions[j])
        
        positions[j] = positions[j] + velocities[j]
    
    plt.figure(figsize=(8, 6))
    plt.contourf(X, Y, Z, levels=50, cmap='viridis') 
    plt.scatter(positions[:, 0], positions[:, 1], color='red', label='Particles') 
    plt.scatter(global_best_position[0], global_best_position[1], color='blue', label='Global Best')
    plt.title(f'PSO Iteration {i+1}')
    plt.legend()
    plt.colorbar()
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
